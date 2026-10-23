#!/usr/bin/env python3

"""Build script for ezsnmp.

This script configures and builds the ezsnmp package, a blazingly fast Python SNMP library
based on Net-SNMP. It performs the following tasks:

1. Detects the system's Net-SNMP installation (system, Homebrew, or MacPorts)
2. Runs SWIG to generate C++ wrapper code from interface files (.i -> .cpp)
3. Compiles four C++ extension modules (_datatypes, _exceptionsbase, _netsnmpbase, _sessionbase)
4. Selects version-specific Net-SNMP source files based on detected version (5.7, 5.8, 5.9, or 5.10)

Command-line options:
    --debug         Enable debug compilation flags (-Wall -O0 -g)
    --basedir=PATH  Use in-tree Net-SNMP build from specified directory

Requirements:
    - Net-SNMP library and headers (via system package manager, Homebrew, or MacPorts)
    - SWIG 4.x for generating Python bindings
    - C++17 compatible compiler
    - setuptools and wheel
"""

import json
import os
import shutil
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from shutil import which
from subprocess import run, CalledProcessError
from sys import path, platform
from setuptools import setup, Extension
from setuptools.command.build_py import build_py as _build_py
from setuptools.command.build_ext import build_ext
import time

setup_dir = str(Path(globals().get("__file__", "setup.py")).resolve().parent)
if setup_dir not in path:
    path.insert(0, setup_dir)
from build_utils import (
    collect_files_with_suffixes,
    compute_object_cache_key,
    gather_build_configuration,
    is_python_independent_source,
    is_up_to_date,
    resolve_build_jobs,
)

swig_targets = [
    ("ezsnmp/interface/datatypes.i", "ezsnmp/src/ezsnmp_datatypes.cpp"),
    ("ezsnmp/interface/exceptionsbase.i", "ezsnmp/src/ezsnmp_exceptionsbase.cpp"),
    ("ezsnmp/interface/netsnmpbase.i", "ezsnmp/src/ezsnmp_netsnmpbase.cpp"),
    ("ezsnmp/interface/sessionbase.i", "ezsnmp/src/ezsnmp_sessionbase.cpp"),
]


def _read_signature(sig_path: str) -> str | None:
    try:
        return Path(sig_path).read_text(encoding="utf-8")
    except OSError:
        return None


def _write_signature(sig_path: str, content: str) -> None:
    try:
        parent = os.path.dirname(sig_path)
        if parent:
            os.makedirs(parent, exist_ok=True)
        tmp_path = f"{sig_path}.{os.getpid()}.{threading.get_ident()}.tmp"
        Path(tmp_path).write_text(content, encoding="utf-8")
        os.replace(tmp_path, sig_path)
    except OSError:
        pass


class SwigBuildExt(build_ext):
    """Custom build_ext: incremental SWIG + deduplicated, conflict-free parallel C++ builds."""

    def _run_swig_command(self, swig_command, interface_file, wrapper_file):
        start_time = time.perf_counter()
        print(f"\t[PROFILE] SWIG start for {interface_file} at {start_time:.6f}")
        command = swig_command + ["-o", wrapper_file, interface_file]
        try:
            run(command, check=True)
            end_time = time.perf_counter()
            delta = end_time - start_time
            print(
                f"\t[PROFILE] SWIG end for {interface_file} at {end_time:.6f} (delta: {delta:.6f}s)"
            )
            return True, interface_file, None
        except (CalledProcessError, FileNotFoundError):
            end_time = time.perf_counter()
            delta = end_time - start_time
            print(
                f"\t[PROFILE] SWIG failed for {interface_file} at {end_time:.6f} (delta: {delta:.6f}s)"
            )
            return False, interface_file, f"SWIG failed for {interface_file}"

    def _get_compiler_identity(self):
        compiler_type = getattr(self.compiler, "compiler_type", "")
        if compiler_type == "msvc":
            cc_bin = getattr(self.compiler, "cc", None)
            opts_attr = "compile_options_debug" if self.debug else "compile_options"
            opts = list(getattr(self.compiler, opts_attr, []) or [])
            cmd = ([cc_bin] if cc_bin else []) + opts
            resolved_bin = (
                cc_bin
                if (cc_bin and os.path.isfile(cc_bin))
                else (which(cc_bin) if cc_bin else None)
            )
        else:
            raw_cmd = (
                getattr(self.compiler, "compiler_so_cxx", None)
                or getattr(self.compiler, "compiler_cxx", None)
                or getattr(self.compiler, "compiler_so", None)
                or []
            )
            cmd = [str(part) for part in raw_cmd]
            resolved_bin = which(cmd[0]) if cmd else None

        bin_meta = None
        if resolved_bin and os.path.isfile(resolved_bin):
            try:
                stat = os.stat(resolved_bin)
                bin_meta = [resolved_bin, stat.st_size, int(stat.st_mtime)]
            except OSError:
                bin_meta = [resolved_bin]

        return {
            "compiler_type": compiler_type,
            "cmd": [str(part) for part in cmd],
            "bin_meta": bin_meta,
        }

    def _compile_unit(self, unit: dict) -> None:
        start_time = time.perf_counter()
        self.compiler.compile(
            [unit["src"]],
            output_dir=unit["output_dir"],
            macros=list(unit["macros"]),
            include_dirs=list(unit["include_dirs"]),
            debug=self.debug,
            extra_postargs=list(unit["extra_args"]),
            depends=list(unit["depends"]),
        )
        delta = time.perf_counter() - start_time
        print(f"\t[PROFILE] Compiled {unit['src']} in {delta:.3f}s")

        cache_path = unit.get("cache_path")
        if cache_path and os.path.isfile(unit["obj"]):
            try:
                os.makedirs(os.path.dirname(cache_path), exist_ok=True)
                tmp_cache = f"{cache_path}.{os.getpid()}.{threading.get_ident()}.tmp"
                shutil.copy2(unit["obj"], tmp_cache)
                os.replace(tmp_cache, cache_path)
            except OSError:
                pass

    def build_extensions(self) -> None:
        if not self.extensions:
            return

        self.check_extensions_list(self.extensions)

        # Initialize MSVC on the main thread before spawning worker threads so
        # lazy vcvarsall.bat execution never races on os.environ.
        if hasattr(self.compiler, "initialize") and not getattr(
            self.compiler, "initialized", True
        ):
            self.compiler.initialize()

        jobs = resolve_build_jobs(self.parallel)
        build_temp = self.build_temp or "build/temp"
        header_files = collect_files_with_suffixes(["ezsnmp/include"], (".h", ".hpp"))
        compiler_identity = self._get_compiler_identity()
        compiler_macros = list(getattr(self.compiler, "macros", []) or [])
        compiler_incdirs = list(getattr(self.compiler, "include_dirs", []) or [])
        is_msvc = getattr(self.compiler, "compiler_type", "") == "msvc"

        ext_configs = []
        for ext in self.extensions:
            extra_args = list(ext.extra_compile_args or [])
            if is_msvc and (
                self.debug
                or any(flag in extra_args for flag in ("/Zi", "/ZI", "-Zi", "-ZI"))
            ):
                if "/FS" not in extra_args and "-FS" not in extra_args:
                    extra_args.append("/FS")

            macros = list(ext.define_macros or [])
            for undef in ext.undef_macros or []:
                macros.append((undef,))

            sources = self.swig_sources(sorted(ext.sources), ext)
            ext_configs.append(
                (ext, sources, macros, list(ext.include_dirs or []), extra_args)
            )

        compile_sig = json.dumps(
            {
                "compiler_identity": compiler_identity,
                "compiler_macros": [list(m) for m in compiler_macros],
                "compiler_incdirs": compiler_incdirs,
                "debug": bool(self.debug),
                "extensions": [
                    {
                        "name": ext.name,
                        "macros": [list(m) for m in macros],
                        "include_dirs": inc_dirs,
                        "extra_args": extra_args,
                    }
                    for ext, _, macros, inc_dirs, extra_args in ext_configs
                ],
            },
            sort_keys=True,
        )
        sig_path = os.path.join(build_temp, ".ezsnmp_compile_signature")
        sig_valid = (not self.force) and (_read_signature(sig_path) == compile_sig)

        exts_to_build = []
        for ext, sources, macros, inc_dirs, extra_args in ext_configs:
            ext_path = self.get_ext_fullpath(ext.name)
            ext_deps = sources + list(ext.depends or []) + header_files
            if sig_valid and is_up_to_date([ext_path], ext_deps):
                print(f"skipping '{ext.name}' extension (up-to-date)")
                continue
            exts_to_build.append((ext, sources, macros, inc_dirs, extra_args, ext_path))

        if not exts_to_build:
            return

        # Deduplicate shared C++ translation units across extensions so each .o/.obj
        # path is compiled once without race conditions.
        unique_units: dict[str, dict] = {}
        ext_object_lists: dict[str, list[str]] = {}

        for ext, sources, macros, inc_dirs, extra_args, _ in exts_to_build:
            ext_objs = []
            settings_key = (
                tuple(tuple(m) for m in macros),
                tuple(inc_dirs),
                tuple(extra_args),
            )
            for src in sources:
                default_obj = self.compiler.object_filenames(
                    [src], strip_dir=False, output_dir=build_temp
                )[0]
                norm_obj = os.path.normcase(os.path.normpath(default_obj))
                existing = unique_units.get(norm_obj)
                if existing is not None and existing["settings_key"] != settings_key:
                    scoped_dir = os.path.join(build_temp, ext.name.replace(".", "_"))
                    scoped_obj = self.compiler.object_filenames(
                        [src], strip_dir=False, output_dir=scoped_dir
                    )[0]
                    norm_obj = os.path.normcase(os.path.normpath(scoped_obj))
                    output_dir = scoped_dir
                    target_obj = scoped_obj
                else:
                    output_dir = build_temp
                    target_obj = default_obj

                if norm_obj not in unique_units:
                    unique_units[norm_obj] = {
                        "src": src,
                        "obj": target_obj,
                        "output_dir": output_dir,
                        "macros": macros,
                        "include_dirs": inc_dirs,
                        "extra_args": extra_args,
                        "depends": list(ext.depends or []),
                        "settings_key": settings_key,
                        "cache_path": None,
                    }
                else:
                    merged_deps = set(unique_units[norm_obj]["depends"]) | set(
                        ext.depends or []
                    )
                    unique_units[norm_obj]["depends"] = sorted(merged_deps)
                ext_objs.append(unique_units[norm_obj]["obj"])
            ext_object_lists[ext.name] = ext_objs

        # Pre-create all object directories on the main thread before parallel compile.
        for unit in unique_units.values():
            obj_dir = os.path.dirname(unit["obj"])
            if obj_dir:
                os.makedirs(obj_dir, exist_ok=True)

        object_cache_dir = os.environ.get("EZSNMP_OBJECT_CACHE_DIR", "").strip()
        units_to_compile = []
        reused_local = 0
        reused_cache = 0

        for unit in unique_units.values():
            unit_deps = [unit["src"]] + unit["depends"] + header_files
            if sig_valid and is_up_to_date([unit["obj"]], unit_deps):
                reused_local += 1
                continue

            if (
                not self.force
                and object_cache_dir
                and is_python_independent_source(unit["src"])
                and os.path.isfile(unit["src"])
            ):
                effective_macros = compiler_macros + list(unit["macros"])
                cache_key = compute_object_cache_key(
                    src_path=unit["src"],
                    header_files=header_files,
                    compiler_identity=compiler_identity,
                    macros=effective_macros,
                    non_python_incdirs=unit["include_dirs"],
                    extra_args=unit["extra_args"],
                    debug=self.debug,
                    plat_name=getattr(self, "plat_name", None),
                )
                obj_ext = os.path.splitext(unit["obj"])[1]
                cache_path = os.path.join(object_cache_dir, f"{cache_key}{obj_ext}")
                unit["cache_path"] = cache_path
                if os.path.isfile(cache_path):
                    shutil.copy2(cache_path, unit["obj"])
                    reused_cache += 1
                    continue

            units_to_compile.append(unit)

        # Schedule largest C++ sources first (LPT) so SWIG wrappers start immediately.
        units_to_compile.sort(
            key=lambda u: os.path.getsize(u["src"]) if os.path.isfile(u["src"]) else 0,
            reverse=True,
        )

        print(
            f"------- Compiling {len(units_to_compile)}/{len(unique_units)} unique C++ "
            f"sources using {min(max(len(units_to_compile), 1), jobs)} worker(s) "
            f"(max_jobs={jobs}, local_hits={reused_local}, cache_hits={reused_cache}) -------"
        )

        if units_to_compile:
            worker_count = min(len(units_to_compile), jobs)
            if worker_count == 1:
                for unit in units_to_compile:
                    self._compile_unit(unit)
            else:
                with ThreadPoolExecutor(max_workers=worker_count) as executor:
                    futures = [
                        executor.submit(self._compile_unit, unit)
                        for unit in units_to_compile
                    ]
                    for future in as_completed(futures):
                        future.result()

        _write_signature(sig_path, compile_sig)

        # Link each extension sequentially from its deduplicated object list.
        for ext, sources, _, _, _, ext_path in exts_to_build:
            objects = list(ext_object_lists[ext.name])
            if ext.extra_objects:
                objects.extend(ext.extra_objects)
            self._built_objects = objects[:]
            language = ext.language or self.compiler.detect_language(sources)
            self.compiler.link_shared_object(
                objects,
                ext_path,
                libraries=self.get_libraries(ext),
                library_dirs=ext.library_dirs,
                runtime_library_dirs=ext.runtime_library_dirs,
                extra_postargs=list(ext.extra_link_args or []),
                export_symbols=self.get_export_symbols(ext),
                debug=self.debug,
                build_temp=build_temp,
                target_lang=language,
            )
            if getattr(ext, "_needs_stub", False):
                build_lib = self.get_finalized_command("build_py").build_lib
                self.write_stub(build_lib, ext)

    def run(self):
        print("------- Running SWIG to generate wrapper code -------")
        swig_command = [
            "swig",
            "-c++",  # Force C++ code generation
            "-python",  # Generate Python bindings
            "-builtin",  # Use native Python data types
            "-threads",  # Add thread support
            "-doxygen",  # Convert Doxygen comments to pydoc
            "-std=c++17",  # Specify C++17 standard
            "-outdir",  # Specify output directory for the .py module
            "ezsnmp/.",
        ]

        for inc_dir in self.extensions[0].include_dirs:
            swig_command.append(f"-I{inc_dir}")
        swig_command.append("-Iezsnmp/interface")

        swig_sig = json.dumps(swig_command)
        build_root = os.path.dirname(self.build_temp or "build/temp") or "build"
        swig_sig_path = os.path.join(build_root, ".ezsnmp_swig_signature")
        swig_sig_valid = (not self.force) and (
            _read_signature(swig_sig_path) == swig_sig
        )
        swig_inputs = collect_files_with_suffixes(
            ["ezsnmp/interface", "ezsnmp/include"], (".i", ".h", ".hpp")
        )

        pending_targets = []
        for interface_file, wrapper_file in swig_targets:
            py_wrapper = f"ezsnmp/{Path(interface_file).stem}.py"
            if swig_sig_valid and is_up_to_date(
                [wrapper_file, py_wrapper], swig_inputs
            ):
                print(f"\t[PROFILE] SWIG up-to-date for {interface_file}, skipping")
                continue
            pending_targets.append((interface_file, wrapper_file))

        if pending_targets:
            jobs = resolve_build_jobs(self.parallel)
            max_workers = min(len(pending_targets), jobs)
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = [
                    executor.submit(
                        self._run_swig_command,
                        swig_command,
                        interface_file,
                        wrapper_file,
                    )
                    for interface_file, wrapper_file in pending_targets
                ]
                for future in as_completed(futures):
                    success, interface_file, error_msg = future.result()
                    if not success:
                        raise RuntimeError(
                            f"{error_msg}. Ensure SWIG is installed and on PATH."
                        )
            _write_signature(swig_sig_path, swig_sig)
        print("------- SWIG processing complete -------")
        super().run()


class BuildEverythingWithSwig(_build_py):
    """Run build_ext first so SWIG outputs .py wrappers before packaging."""

    def run(self):
        self.run_command("build_ext")
        super().run()


def resolve_snmp_source_path(version_str: str) -> str:
    if version_str.startswith("5.6"):
        if platform == "darwin":
            raise RuntimeError(
                f"Net-SNMP version {version_str} is no longer supported. "
                "On macOS, the system-provided Net-SNMP (5.6.x) is not supported. "
                "Please install a supported version via Homebrew "
                "(`brew install net-snmp`) or MacPorts "
                "(`sudo port install net-snmp`)."
            )
        raise RuntimeError(
            f"Net-SNMP version {version_str} is no longer supported. "
            "Please upgrade to Net-SNMP 5.7 or later."
        )
    if version_str.startswith("5.7"):
        return "ezsnmp/src/net-snmp-5.7-final-patched"
    if version_str.startswith("5.8"):
        return "ezsnmp/src/net-snmp-5.8-final-patched"
    if version_str.startswith("5.9"):
        return "ezsnmp/src/net-snmp-5.9-final-patched"
    if version_str.startswith("5.10"):
        return "ezsnmp/src/net-snmp-5.10-final-patched"
    raise RuntimeError(f"Unsupported net-snmp version: {version_str}")


def build_extensions(cfg: dict):
    version_str = (
        cfg.get("homebrew_netsnmp_version")
        or cfg.get("macports_netsnmp_version")
        or cfg["system_netsnmp_version"]
    )
    snmp_source_path = resolve_snmp_source_path(version_str)
    netsnmp_versioned_sources = [
        f"{snmp_source_path}/snmpbulkget.cpp",
        f"{snmp_source_path}/snmpgetnext.cpp",
        f"{snmp_source_path}/snmpbulkwalk.cpp",
        f"{snmp_source_path}/snmpget.cpp",
        f"{snmp_source_path}/snmpwalk.cpp",
        f"{snmp_source_path}/snmpset.cpp",
        f"{snmp_source_path}/snmptrap.cpp",
    ]
    netsnmpbase_sources = [
        "ezsnmp/src/ezsnmp_netsnmpbase.cpp",  # Generated by SWIG
        "ezsnmp/src/exceptionsbase.cpp",
        "ezsnmp/src/datatypes.cpp",
        "ezsnmp/src/helpers.cpp",
        "ezsnmp/src/thread_safety.cpp",
    ] + netsnmp_versioned_sources
    sessionbase_sources = [
        "ezsnmp/src/ezsnmp_sessionbase.cpp",  # Generated by SWIG
        "ezsnmp/src/exceptionsbase.cpp",
        "ezsnmp/src/datatypes.cpp",
        "ezsnmp/src/sessionbase.cpp",
        "ezsnmp/src/helpers.cpp",
        "ezsnmp/src/thread_safety.cpp",
    ] + netsnmp_versioned_sources
    compile_args = cfg["compile_args"]
    link_args = cfg["link_args"]
    libdirs = cfg["libdirs"]
    incdirs = cfg["incdirs"]
    libs = cfg["libs"]
    return [
        Extension(
            name="ezsnmp._datatypes",
            sources=[
                "ezsnmp/src/ezsnmp_datatypes.cpp",  # Generated by SWIG
                "ezsnmp/src/datatypes.cpp",
            ],
            library_dirs=libdirs,
            include_dirs=incdirs,
            libraries=libs,
            extra_compile_args=compile_args,
            extra_link_args=link_args,
        ),
        Extension(
            name="ezsnmp._exceptionsbase",
            sources=[
                "ezsnmp/src/ezsnmp_exceptionsbase.cpp",  # Generated by SWIG
                "ezsnmp/src/exceptionsbase.cpp",
            ],
            library_dirs=libdirs,
            include_dirs=incdirs,
            libraries=libs,
            extra_compile_args=compile_args,
            extra_link_args=link_args,
        ),
        Extension(
            name="ezsnmp._netsnmpbase",
            sources=netsnmpbase_sources,
            library_dirs=libdirs,
            include_dirs=incdirs,
            libraries=libs,
            extra_compile_args=compile_args,
            extra_link_args=link_args,
        ),
        Extension(
            name="ezsnmp._sessionbase",
            sources=sessionbase_sources,
            library_dirs=libdirs,
            include_dirs=incdirs,
            libraries=libs,
            extra_compile_args=compile_args,
            extra_link_args=link_args,
        ),
    ]


def debug_print(cfg: dict):
    for k, v in cfg.items():
        display_value = v if v else "None"
        print(f"{k}: {display_value}")


def main():
    cfg = gather_build_configuration()
    debug_print(cfg)
    extensions = build_extensions(cfg)
    print(
        f"Using SNMP sources from: {resolve_snmp_source_path(cfg['system_netsnmp_version'])}"
    )
    setup(
        ext_modules=extensions,
        cmdclass={"build_ext": SwigBuildExt, "build_py": BuildEverythingWithSwig},
    )


if __name__ == "__main__":
    main()
