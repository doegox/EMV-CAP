#!/bin/bash

function validate {
    # $1: CARD $2: OTP $3:MODE $4: DATA (optional)
    echo "TEST $1 $3 $4"
    ./EMV-CAP -$3 $4 -r foo:$1 |\
      grep ": $2\$" || echo "****** FAIL ******"
}

validate cap_be           23790240 m1
validate cap_be           23580039 m1 1234
validate cap_be           23719593 m2 1234
validate maestro_be       53780079 m1
validate visa_dpa_be      19814125 m1
validate visa_dpa_fr      34656023 m1
validate visa_cleo_fr    102823328 m1
validate cap_abnamro_nl   34998891 m1 24661140
validate cap_fc09_uk       4822527 m1 12345678
validate bancontact_be    53780079 m1
validate eid_pt            8669448 m1
validate visa_be          53780079 m1
validate cap_rabo1_nl     07986951 m1
validate cap_rabo2_nl     08180460 m2 0530026806
validate maestro_lu       75176930639874 m1
# EMV-CAP -L -r foo:pse_uk
# EMV-CAP -m1 -r foo:visa_rosa_sk -v -d
