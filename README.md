About
=====

This tool emulates an EMV-CAP device, to illustrate the article "Banque en ligne : à la decouverte d'EMV-CAP" published in MISC, issue #56 [1]

Usage
=====
Command line help:

```
$ ./EMV-CAP -h
usage: EMV-CAP [-h] [-l] [-L] [--tlv PARSETLV]
               [-r {<index>, <reader_substring>}] [-d] [-v] [-m {1,2}]
               [--warmreset {auto,yes,no}]
               [N [N ...]]

EMV-CAP calculator

optional arguments:
  -h, --help            show this help message and exit

Standalone options:
  -l, --listreaders     print list of available readers and exit
  -L, --listapps        print list of available applications on the card and
                        exit
  --tlv PARSETLV        parse a hex string into TLV elements

Global options:
  -r {<index>, <reader_substring>}, --reader {<index>, <reader_substring>}
                        select one specific reader with reader index, name
                        string or sub-string otherwise first reader found will
                        be used.
  -d, --debug           print exchanged APDU for debugging
  -v, --verbose         print APDU parsing

Modes and data:
  -m {1,2}, --mode {1,2}
                        M1/M2 mode selection (mandatory, unless -l or -L is
                        used)
  N                     number(s) as M1/M2 data: max one 8-digit number for M1
                        and max 10 10-digit numbers for M2
  --warmreset {auto,yes,no}
                        Warm reset: yes / no / auto (default) If 'auto' it
                        will perform a warm reset if the ATR starts with 3F
                        (indirect convention)

Examples:
    EMV-CAP --listreaders
    EMV-CAP --listapps
    EMV-CAP --listapps --debug --reader foo
    EMV-CAP -m1 123456
    EMV-CAP -m2
    EMV-CAP -m2 1000 3101234567
```

Links
=====

[1] http://connect.ed-diamond.com/MISC/MISC-056/Banques-en-ligne-a-la-decouverte-d-EMV-CAP  
[2] https://sites.uclouvain.be/EMV-CAP/
