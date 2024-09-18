# Making the swig interface files

One look for the netsnmp app file under <https://github.com/net-snmp/net-snmp/tree/5e691a85bcd95a42872933515698309e57832cfc/apps>

Two copy the c file over, for example `snmpwalk.c`. Then rename to change the extension to `.cpp`.

Three make a header file for it `snmpwalk.h` and extract methods/functions from the source code.

Four run the command below to generate the wrap file.

```bash
swig -c++ -python -builtin -outdir ezsnmp/. -o ezsnmp/src/ezsnmp_wrap.cpp ezsnmp/interface/ezsnmp.i
```

* `-c++` to force generation of a `.cpp` file
* `-python` to build a python module
* `-builtin` to build with native python data types. [Python_builtin_types](https://swig.org/Doc4.0/Python.html#Python_builtin_types)

Five run

```python3
clear && rm -drf build ezsnmp.egg-info && python3 -m pip install .
```

Six run it in python3

```bash
python3
>>> import ezsnmp
>>> args = ["-v" , "3", "-u", "secondary_sha_aes", "-a", "SHA", "-A", "auth_second", "-x", "AES", "-X" ,"priv_second", "-l", "authPriv", "localhost:11161"]
>>> retval = ezsnmp.snmpwalk(args)
>>> print(retval)
```

## Making the patch files

Within the patches directory run the following command.

```bash
diff -Naurw ~/Downloads/net-snmp-master/apps/snmpwalk.c ../src/snmpwalk.cpp > snmpwalk.patch
```

consider the following names for the api.
`snmp` is redundant in the name since the module `ezsnmp` already has it in its' name.
snmpwalk --> ezsnmp.walk
snmpbulkwalk --> ezsnmp.bulk_walk
snmpget --> ezsnmp.get
snmpbulkget --> ezsnmp.bulk_get
etc...