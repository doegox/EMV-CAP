#!/usr/bin/env python

import sys
import argparse
import smartcard
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

    #if debug:
    # TODO: how??
    #    observer=smartcard.CardConnection.Observer()
    #    connection.addObserver(observer)
    return connection

def myTransmit(connection, CAPDU, debug=False):
    if debug:
        print "CAPDU:        " + CAPDU
    (RAPDU, sw1, sw2) = connection.transmit([ord(c) for c in CAPDU.decode('hex')])
    if debug:
        print "RAPDU(%02X %02X): " % (sw1, sw2) + ''.join(["%02X" % i for i in RAPDU])
    if sw1 == 0x61: # More bytes available
        CAPDU='00C00000'+("%02X" % sw2)
        if debug:
            print "CAPDU:        " + CAPDU
        (RAPDU, sw1, sw2) = connection.transmit([ord(c) for c in CAPDU.decode('hex')])
        if debug:
            print "RAPDU(%02X %02X): " % (sw1, sw2) + ''.join(["%02X" % i for i in RAPDU])
    # TODO handle sw1=0x6c -> fix CAPDU with length = sw2
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
print "ATR: " + ''.join(["%02X" % i for i in connection.getATR()])

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
            print ''.join(["%02X" % i for i in RAPDU])
            print TLVparser(RAPDU)
if current_app is None:
    print 'No suitable app found, exiting'
    sys.exit()
if parsedRAPDU[0].name == 'fci template':
    fci_template = parsedRAPDU[0].V
    if 'fci proprietary template' in fci_template:
        fci_proprietary_template = fci_template[fci_template.index('fci proprietary template')].V
        if 0xBF0C in fci_proprietary_template:
            fci_issuer_discretionary_data = fci_proprietary_template[fci_proprietary_template.index(0xBF0C)].V
            if 0x9F55 in fci_issuer_discretionary_data:
                issuer_authentication_flag = fci_issuer_discretionary_data[fci_issuer_discretionary_data.index(0x9F55)].V
                psn_to_be_used = (ord(issuer_authentication_flag.decode('hex')) & 0x40) != 0
if 'psn_to_be_used' in vars() and psn_to_be_used:
    print 'Warning card tells to use PSN but I dont know how'

# Initiate transaction / Get Processing Options:
(RAPDU, sw1, sw2) = myTransmit(connection, '80A8000003830134', args.debug)
if args.verbose:
    print "%02X %02X" % (sw1, sw2)
    print TLVparser(RAPDU)

# TODO
# Read 0x010C = ?? & where 0x010C is in previous TLV??
CAPDU='00B2%04X00' % 0x010C
(RAPDU, sw1, sw2) = myTransmit(connection, CAPDU, args.debug)
if args.verbose:
    print "%02X %02X" % (sw1, sw2)
    print RAPDU
#    print TLVparser(RAPDU)

sys.exit()

#args.m2data=[11, 22, 33]
#args.mode=2
#verbose=False
