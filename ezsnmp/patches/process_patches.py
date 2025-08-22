#!/usr/bin/env python3
import argparse
import os
import re
from pathlib import Path


def parse_definitive_patch(definitive_patch_path: Path) -> set:
    """
    Reads the definitive patch file (e.g., snmpwalk-5.9.patch) and
    returns a set of all explicit changes (+ or - lines).
    This set acts as a filter for what changes are allowed.
    """
    if not definitive_patch_path.is_file():
        print(f"Error: Definitive patch file not found at {definitive_patch_path}")
        return set()

    allowed_changes = set()
    with open(definitive_patch_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith(("+", "-")) and not line.startswith(("+++", "---")):
                allowed_changes.add(line)
    return allowed_changes


def process_target_patch(
    tool: str,
    target_version: str,
    allowed_changes: set,
    patch_dir: Path,
    output_dir: Path,
):
    """
    Reads a target patch file from its versioned subdirectory, filters its
    changes, and writes a new, corrected patch file to a new version-specific
    final directory.
    """
    target_subdir = patch_dir / f"net-snmp-{target_version}-patches"
    target_patch_path = target_subdir / f"{tool}-{target_version}.patch"

    if not target_patch_path.is_file():
        print(
            f"  -> Skipping version {target_version}: Patch file not found at {target_patch_path}"
        )
        return

    # Create a version-specific output directory based on the target version
    versioned_output_dir = output_dir / f"net-snmp-{target_version}-final-patches"
    versioned_output_dir.mkdir(exist_ok=True)
    output_patch_path = versioned_output_dir / f"{tool}-{target_version}.patch"

    hunk_header_re = re.compile(r"@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@.*")

    with open(target_patch_path, "r", encoding="utf-8") as infile, open(
        output_patch_path, "w", encoding="utf-8"
    ) as outfile:

        current_hunk_lines = []
        old_start, new_start = 0, 0

        def write_hunk():
            if not current_hunk_lines:
                return

            old_line_count = sum(
                1 for line in current_hunk_lines if not line.startswith("+")
            )
            new_line_count = sum(
                1 for line in current_hunk_lines if not line.startswith("-")
            )

            new_header = (
                f"@@ -{old_start},{old_line_count} +{new_start},{new_line_count} @@\n"
            )
            outfile.write(new_header)
            outfile.writelines(current_hunk_lines)
            current_hunk_lines.clear()

        for line in infile:
            if line.startswith(("---", "+++")):
                outfile.write(line)
                continue

            if line.startswith("@@"):
                write_hunk()
                match = hunk_header_re.match(line)
                if match:
                    old_start = int(match.group(1))
                    new_start = int(match.group(3))
                continue

            if line.startswith((" ", "+", "-")):
                if line.startswith(("+", "-")):
                    if line in allowed_changes:
                        current_hunk_lines.append(line)
                else:
                    current_hunk_lines.append(line)

        write_hunk()

    print(f"  -> Successfully created '{output_patch_path}'")


def main():
    parser = argparse.ArgumentParser(
        description="Filters older Net-SNMP patch files based on a definitive patch file.",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument("--tools", required=True, nargs="+", help="List of tool names.")
    parser.add_argument(
        "--definitive-version", required=True, help="Version of the definitive patch."
    )
    parser.add_argument(
        "--target-versions",
        required=True,
        nargs="+",
        help="List of older versions to process.",
    )
    parser.add_argument(
        "--patch-dir",
        default=".",
        help="Base directory containing versioned subdirectories.",
    )
    parser.add_argument(
        "--output-dir",
        default=".",
        help="Base directory to save the new versioned patch folders.",
    )
    args = parser.parse_args()

    patch_dir = Path(args.patch_dir)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(exist_ok=True)

    print(f"Using definitive version: {args.definitive_version}\n")

    for tool in args.tools:
        print(f"Processing tool: '{tool}'...")

        definitive_subdir = patch_dir / f"net-snmp-{args.definitive_version}-patches"
        definitive_patch_path = (
            definitive_subdir / f"{tool}-{args.definitive_version}.patch"
        )

        allowed_changes = parse_definitive_patch(definitive_patch_path)
        if not allowed_changes:
            print(
                f"Warning: No changes found in '{definitive_patch_path}'. Skipping tool '{tool}'.\n"
            )
            continue

        for version in args.target_versions:
            process_target_patch(tool, version, allowed_changes, patch_dir, output_dir)

        print("-" * 20)


if __name__ == "__main__":
    main()
