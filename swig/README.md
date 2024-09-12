# Making the swig interface fils

One look for the netsnmp app file under <https://github.com/net-snmp/net-snmp/tree/5e691a85bcd95a42872933515698309e57832cfc/apps>

Two copy the c file over, for example `snmpwalk.c`.

Three make a header file for it `snmpwalk.h`.

Four run to generate the wrap file.

```bash
swig -python -outdir . -o src/ezsnmp_wrap.c interface/ezsnmp.i
```

Five compile stuff

```bash
clear && clang -Wno-unused-result -Wsign-compare -Wunreachable-code -fno-common -dynamic -DNDEBUG -g -fwrapv -O3 -Wall -iwithsysroot/System/Library/Frameworks/System.framework/PrivateHeaders -iwithsysroot/Applications/Xcode.app/Contents/Developer/Library/Frameworks/Python3.framework/Versions/3.9/Headers -arch arm64 -arch x86_64 -Werror=implicit-function-declaration -Wno-error=unreachable-code -I/opt/homebrew/Cellar/net-snmp/5.9.4/include -I/opt/homebrew/Cellar/openssl@3/3.3.1/include -I/Users/carlossantos/Documents/GitHub/ezsnmp/.venv/include -I/Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/include/python3.9 -I./include/ -c src/snmpwalk.c  src/snmpget.c src/snmpbulkwalk.c src/snmpbulkget.c src/ezsnmp_wrap.c src/helpers.c -std=c17 -Wunused-function -fpermissive
```

six link stuff

```bash
clear && clang++ -bundle -undefined dynamic_lookup -arch arm64 -arch x86_64 -Wl,-headerpad,0x1000 snmpwalk.o snmpget.o snmpbulkwalk.o snmpbulkget.o ezsnmp_wrap.o -L/opt/homebrew/opt/openssl@3/lib -L/opt/homebrew/Cellar/net-snmp/5.9.4/lib -L/opt/homebrew/Cellar/net-snmp/5.9.4/lib -L/opt/homebrew/Cellar/openssl@3/3.3.1/lib -lnetsnmp -lcrypto -o _ezsnmp_swig.so -flat_namespace -framework CoreFoundation -framework CoreServices -framework DiskArbitration -framework IOKit 
```

seven run it in python3

```bash
python3
>>> import ezsnmp_swig
>>> args = ["my_program", "-v" , "3", "-u", "secondary_sha_aes", "-a", "SHA", "-A", "auth_second", "-x", "AES", "-X" ,"priv_second", "-l", "authPriv", "localhost:11161"]
>>> ezsnmp_swig.snmpwalk(args)
```
