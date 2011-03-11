#!/bin/bash

echo Test1
./EMV-CAP.py -m1 -r foo:debit |\
  grep 23790240 || echo FAIL

echo Test2
./EMV-CAP.py -m1 -r foo:debit 1234 |\
  grep 23580039 || echo FAIL

echo Test3
./EMV-CAP.py -m1 -r foo:maestro_be |\
  grep 1179700 || echo FAIL

echo Test4
./EMV-CAP.py -m1 -r foo:visa_dpa_be |\
  grep 19814125 || echo FAIL

echo Test5
./EMV-CAP.py -m1 -r foo:visa_dpa_fr |\
  grep 34656023 || echo FAIL

echo Test6
./EMV-CAP.py -m1 -r foo:visa_cleo_fr |\
  grep 102823328 || echo FAIL

#echo Test7
#./EMV-CAP.py -m1 -r foo:visa_rosa_sk -v -d

echo Test8
./EMV-CAP.py -m1 24661140 -r foo:cap_abnamro_nl |\
  grep 34998891 || echo FAIL

echo Test9
./EMV-CAP.py -m1 12345678 -r foo:cap_fc09_uk |\
  grep 4822527 || echo FAIL

echo Test10
./EMV-CAP.py -L -r foo:pse_uk |\
  grep LINK || echo FAIL
