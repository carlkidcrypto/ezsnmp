from re import search
from sys import platform
from subprocess import check_output, CalledProcessError

class HomeBrew:
    def __init__(self, libdirs: list[str], incdirs: list[str], openssl_ver: str):
        self._libdirs = libdirs
        self._incdirs = incdirs
        self._openssl_ver = openssl_ver
        
    def check_brew_isinstalled(self):
        # Check if brew is installed via: `brew --version` it should return something like: `Homebrew 4.4.5`
        try:
            homebrew_version = check_output("brew --version", shell=True).decode()
            if search(r"Homebrew (\d+\.\d+\.\d+)", homebrew_version):
                pass

        except CalledProcessError:
            print("Homebrew isn't installed...")
            pass

    def check_netsnmp_isinstalled(self) -> None:
        # Check if net-snmp is installed via Brew
        try:
            brew = check_output(
                "brew list net-snmp 2>/dev/null", shell=True
            ).decode()
            lines = brew.splitlines()
            include_dir = list(filter(lambda l: "include/net-snmp" in l, lines))[0]
            self._incdirs.append(include_dir[: include_dir.index("include/net-snmp") + 7])

        except CalledProcessError:
            print("net-snmp isn't installed via HomeBrew...")
            pass

    def get_homebrew_net_snmp_info(self):
        try:
            brew = check_output("brew info net-snmp", shell=True).decode() # this may cause error
            self._openssl_ver = self.get_openssl_ver(brew)
        except CalledProcessError:
            print("A brew command failed...")
            pass

    # no need try-except. check_output may throw CalledProcessError  
    def brew_platform_info(self) -> None:
        if platform == "darwin":
            lib_dir = list(filter(lambda l: "lib/libnetsnmp.dylib" in l, lines))[0]
            self._libdirs.append(lib_dir[: lib_dir.index("lib/libnetsnmp.dylib") + 3])

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
            
    def append_openssl_paths(self) -> None:
        try:
            brew = check_output(
                "brew info {0}".format(openssl_ver), shell=True
            ).decode()
            temp = brew.split("\n")
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
            # print(temp)
            temp_path = str(temp[4].split("(")[0]).strip()

            self._libdirs.append(temp_path + "/lib")
            self._incdirs.append(temp_path + "/include")

        except CalledProcessError:
            print("A brew command failed...")
            pass

try:
    # Check if brew is installed via: `brew --version` it should return something like: `Homebrew 4.4.5`
    homebrew_version = check_output("brew --version", shell=True).decode()
    if search(r"Homebrew (\d+\.\d+\.\d+)", homebrew_version):
        # Check if net-snmp is installed via Brew
        try:
            brew = check_output(
                "brew list net-snmp 2>/dev/null", shell=True
            ).decode()
            lines = brew.splitlines()
            include_dir = list(filter(lambda l: "include/net-snmp" in l, lines))[0]
            incdirs.append(include_dir[: include_dir.index("include/net-snmp") + 7])

            if platform == "darwin":
                lib_dir = list(
                    filter(lambda l: "lib/libnetsnmp.dylib" in l, lines)
                )[0]
                libdirs.append(lib_dir[: lib_dir.index("lib/libnetsnmp.dylib") + 3])




            # The homebrew version also depends on the Openssl keg
            brew = check_output("brew info net-snmp", shell=True).decode()
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

            brew = check_output(
                "brew info {0}".format(openssl_ver), shell=True
            ).decode()
            temp = brew.split("\n")
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
            # print(temp)
            temp_path = str(temp[4].split("(")[0]).strip()

            libdirs.append(temp_path + "/lib")
            incdirs.append(temp_path + "/include")

            print(f"libdirs: {libdirs}")
            print(f"incdirs: {incdirs}")
            print(f"openssl_ver: {openssl_ver}")

        except CalledProcessError:
            print("A brew command failed...")
            pass

except CalledProcessError:
    print("Homebrew isn't installed...")
    pass

