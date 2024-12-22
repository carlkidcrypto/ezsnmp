from re import search
from sys import platform
from subprocess import check_output, CalledProcessError


class HomeBrew:
    def __init__(self):
        self._temp_libdirs = []
        self._temp_incdirs = []
        self._libdirs = None
        self._incdirs = None
        self._lines = []
        self._homebrew_version = None
        self._netsnmp_version = None
        self._openssl_version = None
        self._check_brew_isinstalled()

    @property
    def libdirs(self):
        return self._libdirs

    @property
    def incdirs(self):
        return self._incdirs

    @property
    def homebrew_version(self):
        return self._homebrew_version

    @property
    def homebrew_netsnmp_version(self):
        return self._netsnmp_version

    @property
    def homebrew_openssl_version(self):
        return self._openssl_version

    @property
    def get_lines(self):
        return self._lines

    def _check_brew_isinstalled(self):
        # Check if brew is installed via: `brew --version` it should return something like: `Homebrew 4.4.5`
        try:
            homebrew_version = check_output("brew --version", shell=True).decode()
            self._homebrew_version = homebrew_version
        except CalledProcessError:
            print("Homebrew isn't installed...")
            pass

        else:
            if search(r"Homebrew (\d+\.\d+\.\d+)", homebrew_version):
                self._check_netsnmp_isinstalled(self)
                self._add_homebrew_platform_info(self, self._lines)
                self._get_homebrew_net_snmp_info(self)

    def _check_netsnmp_isinstalled(self) -> list[str]:
        # Check if net-snmp is installed via Brew
        try:
            brew = check_output("brew list net-snmp 2>/dev/null", shell=True).decode()

        except CalledProcessError:
            print("net-snmp isn't installed via HomeBrew...")
            pass

        else:
            lines = brew.splitlines()
            self._lines = lines

            # extract brew version here...
            pattern = r"/opt/homebrew/Cellar/net-snmp/(\d+\.\d+\.\d+)/"
            match = search(pattern, lines[0])
            if match:
                homebrew_netsnmp_version = match.group(1)

            temp_include_dir = list(filter(lambda l: "include/net-snmp" in l, lines))[0]

            self._temp_incdirs.append(
                temp_include_dir[: temp_include_dir.index("include/net-snmp") + 7]
            )

            self._netsnmp_version = homebrew_netsnmp_version

    # no need try-except. check_output may throw CalledProcessError
    def _add_homebrew_platform_info(self, lines: list[str]) -> None:
        if platform == "darwin":
            lib_dir = list(filter(lambda l: "lib/libnetsnmp.dylib" in l, lines))[0]
            self._temp_libdirs.append(
                lib_dir[: lib_dir.index("lib/libnetsnmp.dylib") + 3]
            )

    def _get_homebrew_net_snmp_info(self):
        # The homebrew version also depends on the Openssl keg
        try:
            brew = check_output(
                "brew info net-snmp", shell=True
            ).decode()  # this may cause error

            self._netsnmp_version = brew
            self._get_openssl_ver(self, brew)
            self._append_openssl_paths(self, self._openssl_ver)

        except CalledProcessError:
            print("A brew command failed...")
            pass

    def _get_openssl_ver(self, brew) -> list:
        # The homebrew version also depends on the Openssl keg
        openssl_ver = list(
            filter(
                lambda o: "openssl" in o,
                *map(
                    str.split,
                    filter(
                        lambda l: "openssl" in l,
                        str(brew.replace("'", "")).split("\n"),
                    ),
                ),
            )
        )[0]
        self._openssl_version = openssl_ver

    def _append_openssl_paths(self, openssl_ver) -> None:
        try:
            brew = check_output(
                "brew info {0}".format(openssl_ver), shell=True
            ).decode()

        except CalledProcessError:
            print("A brew command failed...")
            pass

        else:
            # As of 06/04/2024 brew info openssl spits out lines. the fifth one is what we care about
            # This works for now, but we need a better solution
            # ==> openssl@3: stable 3.3.0 (bottled)
            # Cryptography and SSL/TLS Toolkit
            # https://openssl.org/
            # Installed
            # /opt/homebrew/Cellar/openssl@3/3.3.0 (6,977 files, 32.4MB) *
            # Poured from bottle using the formulae.brew.sh API on 2024-06-04 at 21:17:37
            # From: https://github.com/Homebrew/homebrew-core/blob/HEAD/Formula/o/openssl@3.rb
            # License: Apache-2.0
            # ...
            temp = brew.split("\n")
            temp_path = str(temp[4].split("(")[0]).strip()

            self._temp_libdirs.append(temp_path + "/lib")
            self._temp_incdirs.append(temp_path + "/include")

            self._libdirs = self._libdirs + self._temp_libdirs
            self._incdirs = self._incdirs + self._temp_incdirs
