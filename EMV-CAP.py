#!/usr/bin/env python

# All refs to "book" are from "Implementing Electronic Card Payment Systems" by Cristian Radu

import sys
import argparse
import smartcard
import getpass
from EMVCAPcore import *
from Crypto.Cipher import DES

def MyListReaders():
    try:
        readers=smartcard.System.readers()
        if len(readers) == 0:
            print 'error: no reader found!'
            return
        print 'Available readers:'
        for i in range(len(readers)):
            print i, ':', readers[i]
        return
    except smartcard.pcsc.PCSCExceptions.EstablishContextException:
        print 'Cannot connect to PC/SC daemon!'
        return

def MyConnectFoo(debug=False):
    class ConnectFooClass():
        msgs= {'00A4040007A0000000048002':'6F2E8407A0000000048002A5239F38039F35015F2D026672BF0C159F5501005F2C020056DF0709424B533035363030389000',
               '80A8000003830134':'770E82021000940808010100080404009000',
               '00B2010C00':'703E5A0967030405123456789F5F3401025F25030801015F2403121231571367030405123456789D1212221000002200009F5F280200569F420209789F4401029000',
               '00B2040C00':'70589F560B0000FF000000000003FFFF8E0A000000000000000001008C1B9F02069F03069F1A0295055F2A029A039C019F37049F4C029F34038D1F8A029F02069F03069F1A0295055F2A029A039C019F37049F4C029F3403910A9000',
               '80CA9F1700':'9F1701039000',
               '0020008008241234FFFFFFFFFF':'9000',
               '80AE80002200000000000000000000000000008000000000000000000000000000000000010002':'77269F2701809F3602005A9F2608513C1201B7DB02A09F100F06015603A4000007000300000100029000',
               '80AE00002E5A330000000000000000000000000000800000000000000000000000000000000001000200000000000000000000':'77269F2701009F3602005A9F2608AB0862BD0B5A7B8C9F100F0601560325A00007010300000100029000',
        }
        def transmit(self, CAPDU):
            hexCAPDU=''.join(["%02X" % i for i in CAPDU])
            if hexCAPDU in self.msgs:
                rawRAPDU=self.msgs[hexCAPDU].decode('hex')
                return ([ord(c) for c in rawRAPDU[:-2]], ord(rawRAPDU[-2]), ord(rawRAPDU[-1]))
            else:
                return ([], 0x6A, 0x82)
        def getATR(self):
            return ([0x3B, 0x67, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x90, 0x00])
    return ConnectFooClass()

def MyConnect(reader_match=None, debug=False):
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
        del(connection)
    except smartcard.Exceptions.CardConnectionException:
        print 'No card found!'
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
    %(prog)s -m1 123456
    %(prog)s -m2
    %(prog)s -m2 1000 3101234567
     ''')
group1 = parser.add_argument_group('Standalone options')
group1.add_argument('-l', '--listreaders', dest='listreaders',
                   action='store_true', default=False,
                   help='print list of available readers and exit')
group2 = parser.add_argument_group('Global options')
group2.add_argument('-r', '--reader', dest='reader_match',
                   metavar='{<index>, <reader_substring>}',
                   help='select one specific reader with reader index, name string or sub-string otherwise first reader found will be used')
group2.add_argument('-d', '--debug', dest='debug',
                   action='store_true', default=False,
                   help='print exchanged APDU for debugging')
group2.add_argument('-v', '--verbose', dest='verbose',
                   action='store_true', default=False,
                   help='print APDU parsing')
group2.add_argument('-f', '--foo', dest='foo',
                   action='store_true', default=False,
                   help='fake reader, just for debugging')
group3 = parser.add_argument_group('Modes and data')
group3.add_argument('-m', '--mode', dest='mode',
                   action='store',
                   type=int,
                   choices=[1, 2],
                   help='M1/M2 mode selection (mandatory, unless -l is used)')
group3.add_argument('m2data', metavar='N', type=int, nargs='*', \
                   help='number(s) as M1/M2 data: max one 8-digit number for M1 and max 10 10-digit numbers for M2')

args = parser.parse_args()
if args.mode is None and args.listreaders is False and args.foo is False:
    print 'error: argument -m/--mode is required'
    parser.print_usage()
    sys.exit()

if args.listreaders:
    MyListReaders()
    sys.exit()

if args.foo is False:
    connection = MyConnect(args.reader_match, args.debug)
else:
    connection = MyConnectFoo(args.debug)

if connection is None:
    sys.exit()

# ATR
if args.debug:
    print "ATR:          " + ''.join(["%02X" % i for i in connection.getATR()])

# Select Application:
current_app=None
for app in ApplicationsList:
    CAPDU='00A40400'+("%02X" % (len(app['AID'])/2))+app['AID']
    (RAPDU, sw1, sw2) = myTransmit(connection, CAPDU, args.debug)
    if len(RAPDU) != 0:
        if current_app is None:
            current_app=app
            parsedRAPDU = TLVparser(RAPDU)
        if args.verbose:
            print "Application detected: " + app['description']
            if args.debug:
                print ''.join(["%02X" % i for i in RAPDU])
                print TLVparser(RAPDU)
if current_app is None:
    print 'No suitable app found, exiting'
    sys.exit()
assert 0x6F in parsedRAPDU
fci_template = parsedRAPDU[parsedRAPDU.index(0x6F)]
assert 0x84 in fci_template
aid = fci_template.get(0x84)
tlv_pdol=None
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
                print 'Warning card tells to use PSN but I dont know how'

# Initiate transaction / Get Processing Options:
if args.verbose:
    print 'Get Processing Options...'
# From book, ch 6.2.1
default_pdol_data={'9F35':'34', # From book, ch 8.6.1.2, Terminal Type = 34 (Annex A1 of Book 4 in the EMV 2000 specifications).
                  }
# Some other possible pdol contents:
# Terminal Type (tag 9F35), Terminal Capabilities (9F33), Terminal Country Code (9F1A), or the Merchant Category Code (9F15)
# Authorized Amount (tag 81)

pdol_data=''
if tlv_pdol is not None:
    for t in tlv_pdol.V:
        if t.hex_T in default_pdol_data:
            data = default_pdol_data[t.hex_T]
            assert len(data)/2 == t.L
            pdol_data += data
            if args.debug:
                print 'Will use %s for %s' % (data, t.hex_T)
        else:
            print 'Error I need to provide a value for %s and I dont know what' % t.hex_T
            sys.exit()
CAPDU = '80A80000%02X83%02X%s' % ((len(pdol_data)/2)+2, (len(pdol_data)/2), pdol_data)
if args.debug:
    print TLVparser([ord(c) for c in CAPDU[5*2:].decode('hex')])

(RAPDU, sw1, sw2) = myTransmit(connection, CAPDU, args.debug)
parsedRAPDU = TLVparser(RAPDU)
if args.debug:
    print parsedRAPDU
files=[]
assert 0x77 in parsedRAPDU
rsp_msg_template2 = parsedRAPDU[parsedRAPDU.index(0x77)]
if 0x94 in rsp_msg_template2:
    application_file_locator = rsp_msg_template2.get(0x94)
    raw_afl=application_file_locator.V.decode('hex')
    for i in range(application_file_locator.L/4):
        files.append([ord(x) for x in raw_afl[i*4:i*4+4]])

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
        if 0x9F56 in aef_data_template:
            hex_ipb = aef_data_template.get(0x9F56).V
            if args.verbose:
                print 'Issuer Proprietary Bitmap: ' + hex_ipb
            raw_ipb = hex_ipb.decode('hex')
        if 0x8C in aef_data_template:
            tlv_cdol1 = aef_data_template.get(0x8C)
        if 0x8D in aef_data_template:
            tlv_cdol2 = aef_data_template.get(0x8D)
assert raw_ipb
assert tlv_cdol1
assert tlv_cdol2

# Get PIN Try Counter
# From book, ch 6.6.4
CAPDU='80CA9F1700'
(RAPDU, sw1, sw2) = myTransmit(connection, CAPDU, args.debug)
parsedRAPDU = TLVparser(RAPDU)
if args.debug:
    print parsedRAPDU
assert 0x9F17 in parsedRAPDU
ntry = parsedRAPDU[parsedRAPDU.index(0x9F17)].V
if ntry < 3 or args.verbose:
    print 'Still %i PIN tries available!' % ntry

# Verify PIN
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

# Generate Application Cryptogram ARQC
if args.verbose:
    print 'Generate Application Cryptogram ARQC...'

# From book, ch 8.6.1.2
#The type of financial transaction performed by the cardholder system with a remote merchant server limits to the purchase of goods and services. This means that the value field of the Transaction Type (tag 9C) data object is always 00.
#The processing performed by the cardholder system is dynamically reflected in only a few bits of the TVR, the rest being statically set, since the corresponding stages of the EMV transaction are skipped.
#In the first byte of the TVR: Since the off-line data authentication is not included in the transaction profile, bit 8, "Off-line data authentication was not performed", is set to 1, while all the other bits in byte 1 of the TVR are statically set to 0.

default_cdol_data={
                  }
cdol1_data=''
for t in tlv_cdol1.V:
    if t.hex_T in default_cdol_data:
        data = default_cdol_data[t.hex_T]
        assert len(data)/2 == t.L
        cdol1_data += data
        if args.debug:
            print 'Will use %s for %s' % (data, t.hex_T)
    else:
        print 'Error I need to provide a value for %s and I dont know what' % t.hex_T
        sys.exit()


#args.m2data=[11, 22, 33]
#args.mode=2
#verbose=False
