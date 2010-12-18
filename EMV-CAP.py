#!/usr/bin/env python

import sys
import argparse
import smartcard
from Crypto.Cipher import DES


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
group3 = parser.add_argument_group('Modes and data')
group3.add_argument('-m', '--mode', dest='mode',
                   action='store',
                   type=int,
                   choices=[1, 2],
                   help='M1/M2 mode selection (mandatory, unless -l is used)')
group3.add_argument('m2data', metavar='N', type=int, nargs='*', \
                   help='number(s) as M1/M2 data: max one 8-digit number for M1 and max 10 10-digit numbers for M2')

args = parser.parse_args()
reader=None
try:
    readers=smartcard.System.readers()
    if args.listreaders:
        print 'Available readers:'
        for i in range(len(readers)):
            print i, ':', readers[i]
        sys.exit()
except smartcard.pcsc.PCSCExceptions.EstablishContextException:
    print 'Cannot connect to PC/SC daemon!'
    sys.exit()

if len(readers) == 0:
    print 'error: no reader found!'

if args.mode is None:
    print 'error: argument -m/--mode is required'
    parser.print_usage()
    sys.exit()

if args.reader_match is not None:
    try:
        reader_index=int(args.reader_match)
        reader=readers[reader_index]
    except:
        for r in readers:
            if args.reader_match in repr(r):
                reader=r
                break
    if reader is None:
        print 'error: no reader found according to option -r', args.reader_match
        sys.exit()
if reader is None:
    reader=readers[0]
try:
    connection=reader.createConnection()
except:
    print 'Fail connecting to', reader
try:
    connection.connect()
except smartcard.Exceptions.CardConnectionException:
    print 'No card found!'

#if args.debug:
# TODO: how??
#    observer=smartcard.CardConnection.Observer()
#    connection.addObserver(observer)

# Tests
print connection.getATR()
print connection.transmit([ord(c) for c in '00A4040007A000000004800200'.decode('hex')])
sys.exit()

#args.m2data=[11, 22, 33]
#args.mode=2
#verbose=False
