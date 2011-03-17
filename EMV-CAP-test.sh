#!/bin/bash

function EMV-CAP {
    # $1: CARD $2: OTP $3:MODE $4: DATA (optional)
    echo "TEST $1 $3 $4"
    ./EMV-CAP.py -$3 $4 -r foo:$1 |\
      grep ": $2\$" || echo "****** FAIL ******"
}

EMV-CAP cap_be           23790240 m1
EMV-CAP cap_be           23580039 m1 1234
EMV-CAP cap_be           23719593 m2 1234
EMV-CAP maestro_be       53780079 m1
EMV-CAP visa_dpa_be      19814125 m1
EMV-CAP visa_dpa_fr      34656023 m1
EMV-CAP visa_cleo_fr    102823328 m1
EMV-CAP cap_abnamro_nl   34998891 m1 24661140
EMV-CAP cap_fc09_uk       4822527 m1 12345678
EMV-CAP bancontact_be    53780079 m1
EMV-CAP eid_pt            8669448 m1
EMV-CAP visa_be          53780079 m1
EMV-CAP cap_rabo1_nl      7986951 m1
EMV-CAP cap_rabo2_nl      8180460 m2 0530026806

# ./EMV-CAP.py -L -r foo:pse_uk
# ./EMV-CAP.py -m1 -r foo:visa_rosa_sk -v -d
