from re import search
from sys import platform
from subprocess import check_output, CalledProcessError

class HomeBrew:
    def __init__(self, libdirs: list[str], incdirs: list[str]):
        self._libdirs = libdirs
        self._incdirs = incdirs
        
    def check_brew_isinstalled(self):
        # Check if brew is installed via: `brew --version` it should return something like: `Homebrew 4.4.5`
        try:
            homebrew_version = check_output("brew --version", shell=True).decode()
        
        except CalledProcessError:
            print("Homebrew isn't installed...")
            pass

        else:
            if search(r"Homebrew (\d+\.\d+\.\d+)", homebrew_version):
                lines: list[str] = self.check_netsnmp_isinstalled(self)
                self.add_homebrew_platform_info(self, lines)
                self.get_homebrew_net_snmp_info(self)

    def check_netsnmp_isinstalled(self) -> list[str]:
        # Check if net-snmp is installed via Brew
        try:
            brew = check_output("brew list net-snmp 2>/dev/null", shell=True).decode()

        except CalledProcessError:
            print("net-snmp isn't installed via HomeBrew...")
            pass

        else:
            lines = brew.splitlines()
            include_dir = list(filter(lambda l: "include/net-snmp" in l, lines))[0]
            self._incdirs.append(include_dir[: include_dir.index("include/net-snmp") + 7])
            
            self.get_lines(lines)
            return lines

    def get_lines(self, lines):
        return lines

    # no need try-except. check_output may throw CalledProcessError  
    def add_homebrew_platform_info(self, lines: list[str]) -> None:
        if platform == "darwin":
            lib_dir = list(filter(lambda l: "lib/libnetsnmp.dylib" in l, lines))[0]
            self._libdirs.append(lib_dir[: lib_dir.index("lib/libnetsnmp.dylib") + 3])

    def get_homebrew_net_snmp_info(self):
        # The homebrew version also depends on the Openssl keg
        try:
            brew = check_output("brew info net-snmp", shell=True).decode() # this may cause error
            openssl_ver = self.get_openssl_ver(self, brew)
            self.append_openssl_paths(self, openssl_ver)
        except CalledProcessError:
            print("A brew command failed...")
            pass

    def get_openssl_ver(self, brew) -> list:
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
            
        return openssl_ver
            
    def append_openssl_paths(self, openssl_ver) -> None:
        try:
            brew = check_output("brew info {0}".format(openssl_ver), shell=True).decode()

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

            self._libdirs.append(temp_path + "/lib")
            self._incdirs.append(temp_path + "/include")

            print(f"libdirs: {self._libdirs}")
            print(f"incdirs: {self._incdirs}")
            print(f"openssl_ver: {openssl_ver}")