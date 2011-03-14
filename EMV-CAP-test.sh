#!/bin/bash

function EMV-CAP {
    # $1: CARD $2: OTP $3: DATA (optional)
    echo "TEST $1 $3"
    ./EMV-CAP.py -m1 $3 -r foo:$1 |\
      grep ": $2\$" || echo "****** FAIL ******"
}

EMV-CAP cap_be           23790240
EMV-CAP debit            23580039 1234
EMV-CAP maestro_be       53780079
EMV-CAP visa_dpa_be      19814125
EMV-CAP visa_dpa_fr      34656023
EMV-CAP visa_cleo_fr    102823328
EMV-CAP cap_abnamro_nl   34998891 24661140
EMV-CAP cap_fc09_uk       4822527 12345678
EMV-CAP bancontact_be    53780079
EMV-CAP eid_pt            8669448
EMV-CAP visa_be          53780079

# ./EMV-CAP.py -L -r foo:pse_uk
# ./EMV-CAP.py -m1 -r foo:visa_rosa_sk -v -d
