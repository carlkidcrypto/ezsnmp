# Making the swig interface fils

One look for the netsnmp app file under <https://github.com/net-snmp/net-snmp/tree/5e691a85bcd95a42872933515698309e57832cfc/apps>

Two copy the c file over, for example `snmpwalk.c`. Then rename to change the extension to `.cpp`.

Three make a header file for it `snmpwalk.h` and extract methods/functions from the source code.

Four run the command below to generate the wrap file.

```bash
swig -c++ -python -outdir . -o src/ezsnmp_wrap.cpp interface/ezsnmp.i
```

Five run

```python3
clear && rm -drf build ezsnmp_swig.egg-info && python3 -m pip install .
```

Six run it in python3

```bash
python3
>>> import ezsnmp_swig
>>> args = ["THIS_CAN_BE_ANYTHING_FOR_NOW", "-v" , "3", "-u", "secondary_sha_aes", "-a", "SHA", "-A", "auth_second", "-x", "AES", "-X" ,"priv_second", "-l", "authPriv", "localhost:11161"]
>>> retval = ezsnmp_swig.snmpwalk(args)
>>> print(retval)
```
