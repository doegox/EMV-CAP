#!/usr/bin/env python

# All refs to "book" are from "Implementing Electronic Card Payment Systems" by Cristian Radu

import sys
import argparse
from EMVCAPfoo  import *
from EMVCAPcore import *

def MyListReaders():
    print 'Available readers:'
    try:
        readers=smartcard.System.readers()
        if len(readers) == 0:
            print 'Warning: no reader found!'
        else:
            for i in range(len(readers)):
                print i, ' :', readers[i]
    except smartcard.pcsc.PCSCExceptions.EstablishContextException:
        print 'Warning: cannot connect to PC/SC daemon!'
    print 'foo: provides fake reader and card for demo/debug purposes (PIN=1234)'
    return

def MyConnect(reader_match=None, debug=False):
    if reader_match is not None and len(reader_match) >=3 and reader_match[:3] == "foo":
        return MyConnectFoo(reader_match, debug)
    reader=None
    try:
        readers=smartcard.System.readers()
        if len(readers) == 0:
            print 'error: no reader found!'
            return None
    except smartcard.pcsc.PCSCExceptions.EstablishContextException:
        print 'Cannot connect to PC/SC daemon!'
        return None

    if reader_match is not None:
        try:
            reader_index=int(reader_match)
            reader=readers[reader_index]
        except:
            for r in readers:
                if reader_match in repr(r):
                    reader=r
                    break
        if reader is None:
            print 'error: no reader found according to option -r', reader_match
            return None
    if reader is None:
        reader=readers[0]
    try:
        connection=reader.createConnection()
    except:
        print 'Fail connecting to', reader
        return None
    try:
        connection.connect()
    except smartcard.Exceptions.CardConnectionException:
        print 'No card found!'
        del(connection)
        return None
    return connection

def myTransmit(connection, CAPDU, debug=False, maskpin=True):
    fetch_more=False
    if debug:
        if maskpin and CAPDU[:4]=="0020":
            print "CAPDU:        " + CAPDU[:12] + "*** (masked as it contains PIN info)"
        else:
            print "CAPDU:        " + CAPDU
    (RAPDU, sw1, sw2) = connection.transmit([ord(c) for c in CAPDU.decode('hex')])
    if debug:
        print "RAPDU(%02X %02X): " % (sw1, sw2) + ''.join(["%02X" % i for i in RAPDU])
    if sw1 == 0x61: # More bytes available
        CAPDU='00C00000'+("%02X" % sw2)
        fetch_more=True
    if sw1 == 0x6c: # Wrong length
        CAPDU=CAPDU[:4*2]+("%02X" % sw2)
        fetch_more=True
    if fetch_more:
        if debug:
            print "CAPDU:        " + CAPDU
        (RAPDU, sw1, sw2) = connection.transmit([ord(c) for c in CAPDU.decode('hex')])
        if debug:
            print "RAPDU(%02X %02X): " % (sw1, sw2) + ''.join(["%02X" % i for i in RAPDU])
    return (RAPDU, sw1, sw2)

parser = argparse.ArgumentParser(description='EMV-CAP calculator',
    formatter_class=argparse.RawDescriptionHelpFormatter,
    epilog='''\
Examples:
    %(prog)s --listreaders
    %(prog)s --listapps
    %(prog)s --listapps --debug --reader foo
    %(prog)s -m1 123456
    %(prog)s -m2
    %(prog)s -m2 1000 3101234567
     ''')
group1 = parser.add_argument_group('Standalone options')
group1.add_argument('-l', '--listreaders', dest='listreaders',
                   action='store_true', default=False,
                   help='print list of available readers and exit')
group1.add_argument('-L', '--listapps', dest='listapps',
                   action='store_true', default=False,
                   help='print list of available applications on the card and exit')
group1.add_argument('--tlv', dest='parsetlv',
                   action='store',
                   type=str,
                   help='parse a hex string into TLV elements')
group2 = parser.add_argument_group('Global options')
group2.add_argument('-r', '--reader', dest='reader_match',
                   metavar='{<index>, <reader_substring>}',
                   help='select one specific reader with reader index, name string or sub-string otherwise first reader found will be used. ')
group2.add_argument('-d', '--debug', dest='debug',
                   action='store_true', default=False,
                   help='print exchanged APDU for debugging')
group2.add_argument('-v', '--verbose', dest='verbose',
                   action='store_true', default=False,
                   help='print APDU parsing')
group3 = parser.add_argument_group('Modes and data')
group3.add_argument('-m', '--mode', dest='mode',
                   action='store',
                   type=int,
                   choices=[1, 2],
                   help='M1/M2 mode selection (mandatory, unless -l or -L is used)')
# We've to use type str for mdata instead of int to not mangle most left zeroes if any
group3.add_argument('mdata', metavar='N', type=str, nargs='*', \
                   help='number(s) as M1/M2 data: max one 8-digit number for M1 and max 10 10-digit numbers for M2')

args = parser.parse_args()
if args.listapps:
    args.verbose = True
if args.mode is None and args.listreaders is False and args.listapps is False and args.parsetlv is None:
    print 'error: argument -m/--mode is required'
    parser.print_usage()
    sys.exit()
if args.mode == 1 and len(args.mdata) > 1:
    print 'error: max one number in mode1 please'
    parser.print_usage()
    sys.exit()
# Check that mdata strings are actual numbers
for i in args.mdata:
    assert i.isdigit()

if args.parsetlv:
    print TLVparser([ord(c) for c in args.parsetlv.decode('hex')])
    sys.exit()

import smartcard
if args.listreaders:
    MyListReaders()
    sys.exit()

connection = MyConnect(args.reader_match, args.debug)
if connection is None:
    sys.exit()

# ---------------------------------------------------------------------------------------------------
# ATR
if args.debug:
    print "ATR:          " + ''.join(["%02X" % i for i in connection.getATR()])

# ---------------------------------------------------------------------------------------------------
# Select Application:
current_app=None
if args.verbose:
    print 'Trying PSE: accessing 1PAY.SYS.DDF01 file...'
file='1PAY.SYS.DDF01'
CAPDU='00A40400%02X' % len(file) + file.encode('hex')
(RAPDU, sw1, sw2) = myTransmit(connection, CAPDU, args.debug)
if len(RAPDU) != 0:
    parsedRAPDU = TLVparser(RAPDU)
    if args.debug:
        print parsedRAPDU
    assert 0x6F in parsedRAPDU
    fci_template = parsedRAPDU[parsedRAPDU.index(0x6F)]
    assert 0xA5 in fci_template
    fci_p_template = fci_template.get(0xA5)
    assert 0x88 in fci_p_template
    sfi = int(fci_p_template.get(0x88).V, 16)
    record=1
    p2 = (sfi << 3) + 0b100 # means P1 to be interpreted as a record
    p1 = 0x01
    if args.verbose:
        print 'Read record %02X of SFI %02X...' % (record, sfi)
    CAPDU='00B2%02X%02X00' % (p1, p2)
    (RAPDU, sw1, sw2) = myTransmit(connection, CAPDU, args.debug)
    parsedRAPDU = TLVparser(RAPDU)
    if args.debug:
        print parsedRAPDU
    assert 0x70 in parsedRAPDU
    aef_data_template = parsedRAPDU[parsedRAPDU.index(0x70)]
    if 0x61 in aef_data_template:
        aidList = [app['AID'] for app in ApplicationsList]
        for application_template in aef_data_template.get(0x61, multi=True):
            assert 0x4F in application_template
            aid = application_template.get(0x4F).V
            if 0x50 in application_template:
                label = application_template.get(0x50).prettyV
            if args.verbose:
                print "Application detected: %s (%s)" % (label, aid)
            if aid in aidList:
                if args.verbose:
                    print "Application already in pre-defined list, skipping..."
            else:
                if args.verbose:
                    print "Application not yet in pre-defined list, adding it..."
                ApplicationsList.append({'name':label, 'description':label, 'AID':aid})

if args.verbose:
    print 'Trying list of pre-defined applications:'
for app in ApplicationsList:
    CAPDU='00A40400'+("%02X" % (len(app['AID'])/2))+app['AID']
    (RAPDU, sw1, sw2) = myTransmit(connection, CAPDU, args.debug)
    if len(RAPDU) != 0:
        if current_app is None:
            current_app=app
        if args.verbose:
            print "Application detected: " + app['description']
        if args.debug:
            print ''.join(["%02X" % i for i in RAPDU])
            print TLVparser(RAPDU)
if args.listapps:
    # We're done
    sys.exit()

import getpass
if current_app is None:
    print 'No suitable app found, exiting'
    sys.exit()
if args.verbose:
    print 'Will use the following application: ' + current_app['name']
# Do a select again as we might have selected also other apps while scanning:
CAPDU='00A40400'+("%02X" % (len(current_app['AID'])/2))+current_app['AID']
(RAPDU, sw1, sw2) = myTransmit(connection, CAPDU, args.debug)
parsedRAPDU = TLVparser(RAPDU)
assert 0x6F in parsedRAPDU
fci_template = parsedRAPDU[parsedRAPDU.index(0x6F)]
assert 0x84 in fci_template
tlv_aid = fci_template.get(0x84)
tlv_pdol=None
psn_to_be_used=False
if 0xA5 in fci_template:
    fci_proprietary_template = fci_template.get(0xA5)
    if 0x9F38 in fci_proprietary_template:
        tlv_pdol = fci_proprietary_template.get(0x9F38)
    if 0xBF0C in fci_proprietary_template:
        fci_issuer_discretionary_data = fci_proprietary_template.get(0xBF0C)
        if 0x9F55 in fci_issuer_discretionary_data:
            issuer_authentication_flag = fci_issuer_discretionary_data.get(0x9F55)
            psn_to_be_used = (ord(issuer_authentication_flag.V.decode('hex')) & 0x40) != 0
            if psn_to_be_used:
                print 'Warning: card tells to use PSN but this was never tested, please report success/failure to developers, thanks!'

# ---------------------------------------------------------------------------------------------------
# Initiate transaction / Get Processing Options:
if args.verbose:
    print 'Get Processing Options...'
# From book, ch 6.2.1
pdol_data = pdol_filling(tlv_pdol, args.debug)
if pdol_data is None:
    sys.exit()
CAPDU = '80A80000%02X83%02X%s' % ((len(pdol_data)/2)+2, (len(pdol_data)/2), pdol_data)
if args.debug:
    print TLVparser([ord(c) for c in CAPDU[5*2:].decode('hex')])

(RAPDU, sw1, sw2) = myTransmit(connection, CAPDU, args.debug)
parsedRAPDU = TLVparser(RAPDU)
if args.debug:
    print parsedRAPDU
files=[]
if 0x80 in parsedRAPDU:
    # Answer is not TLV encoded, we only get values according to a template
    if args.verbose:
        print 'Warning: answer to Get Processing Options is not TLV, attempting to reconstruct it...'
    parsedRAPDU=reconstruct_processingoptions(parsedRAPDU)
    if args.debug:
        print parsedRAPDU
assert 0x77 in parsedRAPDU
rsp_msg_template2 = parsedRAPDU[parsedRAPDU.index(0x77)]
if 0x94 in rsp_msg_template2:
    application_file_locator = rsp_msg_template2.get(0x94)
    raw_afl=application_file_locator.V.decode('hex')
    for i in range(application_file_locator.L/4):
        files.append([ord(x) for x in raw_afl[i*4:i*4+4]])

# ---------------------------------------------------------------------------------------------------
# Read files
for f in files:
    # From book, ch 4.3.2.1
    sfi = f[0] >> 3
    p2 = (sfi << 3) + 0b100 # means P1 to be interpreted as a record
    for record in range(f[1], f[2]+1):
        p1 = record
        if args.verbose:
            print 'Read record %02X of SFI %02X...' % (record, sfi)
        CAPDU='00B2%02X%02X00' % (p1, p2)
        (RAPDU, sw1, sw2) = myTransmit(connection, CAPDU, args.debug)
        parsedRAPDU = TLVparser(RAPDU)
        if args.debug:
            print parsedRAPDU
        assert 0x70 in parsedRAPDU
        aef_data_template = parsedRAPDU[parsedRAPDU.index(0x70)]
        if 0x5F34 in aef_data_template:
            hex_psn = aef_data_template.get(0x5F34).V
        if 0x9F56 in aef_data_template:
            hex_ipb = aef_data_template.get(0x9F56).V
            if args.verbose:
                print 'Issuer Proprietary Bitmap: ' + hex_ipb
        if 0x8C in aef_data_template:
            tlv_cdol1 = aef_data_template.get(0x8C)
        if 0x8D in aef_data_template:
            tlv_cdol2 = aef_data_template.get(0x8D)
if psn_to_be_used:
    assert hex_psn
assert hex_ipb
assert tlv_cdol1
assert tlv_cdol2

# ---------------------------------------------------------------------------------------------------
# Get PIN Try Counter
# From book, ch 6.6.4
CAPDU='80CA9F1700'
(RAPDU, sw1, sw2) = myTransmit(connection, CAPDU, args.debug)
parsedRAPDU = TLVparser(RAPDU)
if args.debug:
    print parsedRAPDU
assert 0x9F17 in parsedRAPDU
ntry = int(parsedRAPDU[parsedRAPDU.index(0x9F17)].V, 16)
if ntry < 3 or args.verbose:
    print 'Still %i PIN tries available!' % ntry

# ---------------------------------------------------------------------------------------------------
# Verify PIN
# From book, ch 6.6.4
pin=getpass.getpass('Enter PIN (enter to abort)  :')
while len(pin)<4 or len(pin)>12 or not pin.isdigit():
    if len(pin) == 0:
        sys.exit()
    pin=getpass.getpass('Error! I expect a proper PIN: ')
CAPDU='00200080082%i' % len(pin)+pin+'F'*(14-len(pin))
(RAPDU, sw1, sw2) = myTransmit(connection, CAPDU, args.debug)
if sw1 != 0x90 or sw2 != 00:
    print 'Error wrong PIN!!!'
    sys.exit()
del(pin)

# ---------------------------------------------------------------------------------------------------
# Generate Application Cryptogram ARQC
if args.verbose:
    print 'Generate Application Cryptogram ARQC...'

# TODO handle CAP Sign, with amount into transaction_value and account into unpredictable_number
transaction_value = 0
unpredictable_number = 0
if args.mode == 1 and len(args.mdata) == 1:
    unpredictable_number = int(args.mdata[0])
    # TODO for ABN-AMRO NL there is apparently a scrambling of UN, cf [schouwenaar] annex B

cdol1_data = cdol_filling(tlv_cdol1, tlv_aid, transaction_value, unpredictable_number, args.debug)
if cdol1_data is None:
    sys.exit()
CAPDU='80AE8000%02X%s' % (len(cdol1_data)/2, cdol1_data)
(RAPDU, sw1, sw2) = myTransmit(connection, CAPDU, args.debug)
parsedRAPDU = TLVparser(RAPDU)
if args.debug:
    print parsedRAPDU
if 0x80 in parsedRAPDU:
    # Answer is not TLV encoded, we only get values according to a template
    if args.verbose:
        print 'Warning: answer to GenerateAC is not TLV, attempting to reconstruct it...'
    parsedRAPDU=reconstruct_generatearqc(parsedRAPDU)
    if args.debug:
        print parsedRAPDU
assert 0x77 in parsedRAPDU
resp = parsedRAPDU[parsedRAPDU.index(0x77)]
assert 0x9F10 in resp
hex_iad = resp.get(0x9F10).V
assert 0x9F26 in resp
hex_ac = resp.get(0x9F26).V
assert 0x9F27 in resp
hex_cid = resp.get(0x9F27).V
assert 0x9F36 in resp
hex_atc = resp.get(0x9F36).V
if args.verbose:
    print 'Got CID=%s ATC=%s AC=%s IAD=%s' % (hex_cid, hex_atc, hex_ac, hex_iad)

# ---------------------------------------------------------------------------------------------------
# Generate Application Cryptogram AAC
if args.verbose:
    print 'Generate Application Cryptogram AAC...'
cdol2_data = cdol_filling(tlv_cdol2, tlv_aid, transaction_value, unpredictable_number, args.debug)
if cdol2_data is None:
    sys.exit()
CAPDU='80AE0000%02X%s' % (len(cdol2_data)/2, cdol2_data)
(RAPDU, sw1, sw2) = myTransmit(connection, CAPDU, args.debug)
parsedRAPDU = TLVparser(RAPDU)
if args.debug:
    print parsedRAPDU
if 0x80 in parsedRAPDU:
    # Answer is not TLV encoded, we only get values according to a template
    if args.verbose:
        print 'Warning: answer to GenerateAC is not TLV, attempting to reconstruct it...'
    parsedRAPDU=reconstruct_generatearqc(parsedRAPDU)
    if args.debug:
        print parsedRAPDU

# ---------------------------------------------------------------------------------------------------
# From here no more interaction with the card needed

# ---------------------------------------------------------------------------------------------------
# Mixing TDS with cryptogram if Mode2 with TDS
if args.mode == 2 and len(args.mdata) > 0:
    if args.verbose:
        print 'Mixing TDS with cryptogram...'
    hex_ac = mix_tds(hex_ac, args.mdata, args.debug)

# ---------------------------------------------------------------------------------------------------
# Display OTP
if args.verbose:
    print 'Computing OTP...'
if psn_to_be_used:
    otp=generate_otp(hex_cid, hex_atc, hex_ac, hex_iad, hex_ipb, hex_psn, debug=args.debug)
else:
    otp=generate_otp(hex_cid, hex_atc, hex_ac, hex_iad, hex_ipb, debug=args.debug)
print 'Response: %i' % otp
