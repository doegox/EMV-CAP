# coding: utf-8
from Crypto.Cipher import DES

# Copyright 2011, 2012
#   Philippe Teuwen <phil@teuwen.org>
#   Jean-Pierre Szikora <jean-pierre.szikora@uclouvain.be>
# Cette création est mise à disposition selon
# le Contrat Attribution-NoDerivs 2.0 Belgium
# disponible en ligne http://creativecommons.org/licenses/by-nd/2.0/be/
# ou par courrier postal à Creative Commons, 171 Second Street,
# Suite 300, San Francisco, California 94105, USA.

# Little conversion fcts
# APDUs will be either hex strings or lists of integers


def hex2lint(hex):
    return [ord(c) for c in hex.decode('hex')]


def lint2hex(lint):
    return ''.join(["%02X" % i for i in lint])


def lint2ascii(lint):
    return ''.join([chr(i) for i in lint])

ApplicationsList = [

    # From attempts by a Fortis Vasco810 when presenting e.g. an empty JCOP:
    {'name':'VisaRemAuthen',
     'description':'VisaRemAuthen = VISA DEP ~ CAP',
     'AID':'A0000000038002',
     'onVasco810?':True,
     'mode':'DPA'},
    {'name':'SecureCode Aut',
     'description':'SecureCode Aut = MasterCard CAP',
     'AID':'A0000000048002',
     'onVasco810?':True,
     'mode':'CAP'},
    {'name':'BANCONTACT',
     'description':'BANCONTACT',
     'AID':'D056000666111010',
     'onVasco810?':True,
     'mode':'BANCONTACT'},
    {'name':'VISA electron',
     'description':'VISA Electron (Debit)',
     'AID':'A0000000032010',
     'onVasco810?':True,
     'mode':'VISA'},
    {'name':'VISA credit',
     'description':'Standard VISA credit card',
     'AID':'A0000000031010',
     'onVasco810?':True,
     'mode':'VISA'},
    {'name':'MasterCard credit',
     'description':'MasterCard credit (or debit?)',
     'AID':'A0000000041010',
     'onVasco810?':True,
     'mode':'MC'},
    {'name':'MAESTRO',
     'description':'MAESTRO',
     'AID':'A0000000043060',
     'onVasco810?':True,
     'mode':'MAESTRO'},

    # Other sources of AID:
    # http://globalblindspot.blogspot.com/2010/06/emvcap-application-ids.html
    # https://spreadsheets.google.com/pub?\
    #     key=0Aulc2eB5eBHZdDRIU0Zva2U2NWY4N0ppNFFrN3hEVVE
    {'name':'VISA V-PAY?',
     'description':'VISA V-PAY?',
     'AID':'A0000000032020',        'onVasco810?':False},
    {'name':'VISA Interlink',
     'description':'VISA Interlink',
     'AID':'A0000000033010',        'onVasco810?':False},
    {'name':'VISA Specific(1)',
     'description':'VISA Specific(1)',
     'AID':'A0000000034010',        'onVasco810?':False},
    {'name':'VISA Specific(2)',
     'description':'VISA Specific(2)',
     'AID':'A0000000035010',        'onVasco810?':False},
    {'name':'VISA Plus',
     'description':'VISA Plus',
     'AID':'A0000000038010',        'onVasco810?':False},
    {'name':'MasterCard unknown1',
     'description':'MasterCard unknown1',
     'AID':'A00000000410101213',    'onVasco810?':False},
    {'name':'MasterCard unknown2',
     'description':'MasterCard unknown2',
     'AID':'A00000000410101215',    'onVasco810?':False},
    {'name':'MasterCard Specific3',
     'description':'MasterCard Specific3',
     'AID':'A0000000042010',        'onVasco810?':False},
    {'name':'MasterCard Specific4',
     'description':'MasterCard Specific4',
     'AID':'A0000000043010',        'onVasco810?':False},
    {'name':'MasterCard Specific5',
     'description':'MasterCard Specific5',
     'AID':'A0000000044010',        'onVasco810?':False},
    {'name':'MasterCard Specific6',
     'description':'MasterCard Specific6',
     'AID':'A0000000045010',        'onVasco810?':False},
    {'name':'MasterCard Cirrus',
     'description':'MasterCard Cirrus (interbank network)',
     'AID':'A0000000046000',        'onVasco810?':False},
    {'name':'UK Maestro',
     'description':'UK Domestic Maestro - Switch (debit card)',
     'AID':'A0000000050001',        'onVasco810?':False},
    {'name':'UK Maestro Solo',
     'description':'UK Domestic Maestro - Switch (debit card) Solo',
     'AID':'A0000000050001',        'onVasco810?':False},
    {'name':'American Express',
     'description':'American Express credit/debit',
     'AID':'A0000000250000',        'onVasco810?':False},
    {'name':'American Express 2',
     'description':'American Express 2',
     'AID':'A00000002501',          'onVasco810?':False},
    {'name':'ATM cardLINK',
     'description':'ATM cardLINK (UK) ATM network',
     'AID':'A0000000291010',        'onVasco810?':False},
    {'name':'Consorzio BANCOMAT',
     'description':'Consorzio BANCOMAT Pagobancomat Italian ' +\
                   'domestic debit card',
     'AID':'A0000001410001',        'onVasco810?':False},
    {'name':'SAMA',
     'description':'SAMA Saudi Arabia domestic credit/debit card ' +\
                   '(Saudi Arabia Monetary Agency)',
     'AID':'A0000002281010',        'onVasco810?':False},
    {'name':'INTERAC',
     'description':'INTERAC Canadian domestic credit/debit card',
     'AID':'A0000002771010',        'onVasco810?':False},
    {'name':'ZKAGirocard',          'description':'ZKAGirocard',
     'AID':'A0000003591010028001',  'onVasco810?':False},
    # French CB
    {'name':'Carte Bleue',          'description':'Carte Bleue',
     'AID':'A0000000421010',        'onVasco810?':False},
    # From emv-cards_and_internet_banking_-_michael_schouwenaar.pdf
    # special selects on few files?
    # BCA4000002 2901		(?)
    # BCA4000002 2F00		(?)
    # BCA4000002 2FFD		(?)
]


class TLV():
    def __init__(self, T, L, V=None):
        self.T = T
        self.L = L
        if T > 0x100:
            T1 = T >> 8
            self.hex_T = "%04X" % T
        else:
            T1 = T
            self.hex_T = "%02X" % T
        self.tclass = T1 >> 6
        self.type = (T1 & 0x20) >> 5
        self.known_in_dol = False
        if T in TLVdict:
            self.name = TLVdict[T]['name']
            if 'known_in_dol' in TLVdict[T]:
                self.known_in_dol = TLVdict[T]['known_in_dol']
        else:
            self.name = 'Unknown tag %0X' % T
        if V is None:
            self.V = None
        else:
            if V == [] or isinstance(V[0], TLV):  # already parsed
                self.V = V
            else:
                if T in TLVdict and 'onlyTL' in TLVdict[T]:
                    self.V = TLVparser(V, False)
                else:
                    if self.type == 0x01:  # constructed
                        self.V = TLVparser(V)
                    else:
                        self.V = lint2hex(V)
                if T in TLVdict and 'parse' in TLVdict[T]:
                    self.prettyV = TLVdict[T]['parse'](V)

    def __len__(self):
        return self.L

    def __cmp__(self, tlv2):
        if isinstance(tlv2, int):
            return tlv2 == self.T
        elif isinstance(tlv2, str):
            return tlv2 == self.name
        else:
            raise 'Comparison only with T as int or with name, sorry'

    def __iter__(self):
        return self.V.__iter__()

    def get(self, name, multi=False):
        l = [v for v in self.V if v == name]
        if multi:  # return list of matching tlvs, empty list if none found
            return l
        else:
            if len(l) > 0:
                return l[0]
            else:
                return None

    def __eq__(self, tlv2):
        return self.__cmp__(tlv2)

    def __repr__(self):
        r = "<TLV\n"
        r += "    Tag:    %02X (%s)\n" % (self.T, self.name)
        classnames = ['universal', 'application',
                      'context specific', 'private']
        r += "            %s class\n" % classnames[self.tclass]
        typenames = ['primitive', 'constructed']
        r += "            %s\n" % typenames[self.type]
        r += "    Length: %i bytes\n" % self.L
        r += "    Value:  "
        if isinstance(self.V, list):
            r += '\n    %s\n' % repr(self.V).replace('\n', '\n    ')
        else:
            r += "%s\n" % self.V
            if hasattr(self, 'prettyV'):
                r += "    ==      %s\n" % self.prettyV
        r += ">"
        return r


def TLVparser(raw, hasdata=True):
    if len(raw) == 0:
        return False
    # EMV 2000 only supports tagnames of length 1 or 2 (from book, ch4.2)
    # should we support tagnames of lengths > 2?
    if raw[0] & 0x1F == 0x1F:
        T = (raw[0] << 8) + raw[1]
        raw = raw[2:]
    else:
        T = raw[0]
        raw = raw[1:]
    if raw[0] < 128:
        L = raw[0]
        raw = raw[1:]
    else:
        LL = raw[0] & 0x7F
        if LL == 1:
            L = raw[1]
            raw = raw[2:]
        elif LL == 2:
            L = (raw[1] << 8) + raw[2]
            raw = raw[3:]
        else:
            # length > 65535??? then it's probably still a 1-byte length
            return False
    if not hasdata:
        V = None
        # raw = raw
    else:
        V = raw[:L]
        raw = raw[L:]

    resp = [TLV(T, L, V)]
    if len(raw) > 0:
        resp.extend(TLVparser(raw, hasdata))
    return resp


def reconstruct(ct, template):
    assert 0x80 in ct
    data = ct[ct.index(0x80)].V
    offset = 0
    tlv77length = 0
    tlv77data = []
    for (tag, length) in template:
        if length >= 0:
            x = hex2lint(data[offset:offset + (2 * length)])
            offset += 2 * length
        else:
            # Length -1 in our template means all remaining data
            x = hex2lint(data[offset:])
        tlv_x = TLV(tag, len(x), x)
        tlv77data.append(tlv_x)
        tlv77length += len(tlv_x)
    return [TLV(0x77, tlv77length, tlv77data)]


template_processingoptions = \
    [(0x82, 2), (0x94, -1)]

template_generatearqc = \
    [(0x9f27, 1), (0x9f36, 2), (0x9f26, 8), (0x9f10, -1)]

# If more EMV tags are needed, some sources are:
# * http://cheef.ru/docs/HowTo/TAG.info
# * http://www.emvlab.org/emvtags/all/
# * https://cardpeek.googlecode.com/svn-history/trunk/dot_cardpeek_dir\
#     /scripts/emv.lua
TLVdict = {
    0x42:   {'name': 'issuer authority',
             'parse': lint2ascii},
    0x4F:   {'name': 'AID', },
    0x50:   {'name': 'Application Label',
             'parse': lint2ascii},
    0x57:   {'name': 'track2 equivalent data', },
    0x5A:   {'name': 'application Primary Account Number (PAN)', },
    0x5F20: {'name': 'Cardholder Name',
             'parse': lint2ascii},
    0x5F24: {'name': 'application expiration date',
             'parse':
                 lambda x: 'YY=%02X MM=%02X DD=%02X' % (x[0], x[1], x[2])},
    0x5F25: {'name': 'application effective date',
             'parse':
                 lambda x: 'YY=%02X MM=%02X DD=%02X' % (x[0], x[1], x[2])},
    0x5F28: {'name': 'issuer country code', },
    0x5F30: {'name': 'Service Code', },
    0x5F2A: {'name': 'Transaction Currency Code',
             'known_in_dol': True},
    0x5F2C: {'name': 'Cardholder nationality', },
    0x5F2D: {'name': 'language preference',
             'parse': lint2ascii},
    0x5F34: {'name': 'application PAN sequence number', },
    0x5F55: {'name': 'Issuer Country Code (alpha2 format)',
             'parse': lint2ascii},
    0x61:   {'name': 'Application Template'},
    0x6F:   {'name': 'fci template', },
    0x70:   {'name': 'aef data template', },
    0x77:   {'name': 'response message template format 2', },
    0x80:   {'name': 'Command Template', },
    0x82:   {'name': 'application interchange profile (AIP)', },
    0x83:   {'name': 'Command Template', },
    0x84:   {'name': 'dedicated file (df) name', },
# can be bin (AID) or ascii...
#            'parse': lint2ascii},
    0x87:   {'name': 'Application Priority Indicator', },
    0x88:   {'name': 'Short File Identifier (SFI)', },
    0x8A:   {'name': 'Authorization Response Code',
             'known_in_dol': True},
    0x8C:   {'name': 'card risk management dol 1 (cdol1)',
             'onlyTL': True, },
    0x8D:   {'name': 'card risk management dol 2 (cdol2)',
             'onlyTL': True, },
    0x8E:   {'name': 'cardholder verification method (CMV) list', },
    0x8F:   {'name': 'Certification Authority Public Key Index', },
    0x90:   {'name': 'Issuer Public Key Certificate', },
    0x91:   {'name': 'issuer authentication data',
             'known_in_dol': True},
    0x92:   {'name': 'Issuer Public Key Remainder', },
    0x93:   {'name': 'Signed Static Application Data', },
    0x94:   {'name': 'application file locator', },
    0x95:   {'name': 'Terminal Verification Results',
             'known_in_dol': True},
    0x9A:   {'name': 'Transaction Date',
             'known_in_dol': True},
    0x9C:   {'name': 'Transaction Type',
             'known_in_dol': True},
    0x9F02: {'name': 'Authorized Amount (AA)',
             'known_in_dol': True},
    0x9F03: {'name': 'Other Amount',
             'known_in_dol': True},
    0x9F07: {'name': 'AUC - Application Usage Control', },
    0x9F08: {'name': 'Application Version Number', },
    0x9F0D: {'name': 'IAC - Default', },
    0x9F0E: {'name': 'IAC - Denial', },
    0x9F0F: {'name': 'IAC - Online', },
    0x9F10: {'name': 'Issuer Application Data', },
    0x9F11: {'name': 'Issuer Code Table Index', },
    0x9F12: {'name': 'Application Preferred Name',
             'parse': lint2ascii},
    0x9F14: {'name': 'Lower Consecutive Offline Limit', },
    0x9F15: {'name': 'Merchant Category Code',
             'known_in_dol': True},
    0x9F17: {'name': 'PIN Retry Counter',
             'parse':
                 lambda x: x[0]},
    0x9F1A: {'name': 'Terminal Country Code',
             'known_in_dol': True},
    0x9F1F: {'name': 'Track 1 Discretionary Data',
             'parse': lint2ascii},
    0x9F23: {'name': 'Upper Consecutive Offline Limit', },
    0x9F26: {'name': 'Application Cryptogram (AC)', },
    0x9F27: {'name': 'cryptogram information data', },
    0x9F32: {'name': 'Issuer Public Key Exponent', },
    0x9F33: {'name': 'Terminal Capabilities',
             'known_in_dol': True},
    0x9F34: {'name': 'cardholder verification method (cvm) results',
             'known_in_dol': True},
    0x9F35: {'name': 'terminal type',
             'known_in_dol': True,
             'known_in_dol': True},
    0x9F36: {'name': 'Application Transaction counter (ATC)', },
    0x9F37: {'name': 'Unpredictable Number (UN)',
             'known_in_dol': True},
    0x9F38: {'name': 'processing options dol (pdol)',
             'onlyTL': True, },
    0x9F40: {'name': 'Additional Terminal Capabilities',
            # Indicates the data input and output capabilities of the terminal
            # (see Annex A3 in Book 4 [3])
             'known_in_dol': True,
            },
    0x9F42: {'name': 'application currency code', },
    0x9F44: {'name': 'application currency exponent',
             'parse':
                 lambda x: ("%i (0." % x[0]) + ("0" * x[0]) + ")"},
    0x9F45: {'name': 'Data Authentication Code',
             'known_in_dol': True},
    0x9F46: {'name': 'ICC Public Key Certificate', },
    0x9F47: {'name': 'ICC Public Key Exponent', },
    0x9F48: {'name': 'ICC Public Key Remainder', },
    0x9F49: {'name': 'DDOL',
             'onlyTL': True, },
    0x9F4A: {'name': 'SDA Tag List', },
    0x9F4C: {'name': 'ICC dynamic number',
             'known_in_dol': True},
    0x9F4D: {'name': 'Log entry', },
    0x9F55: {'name': 'Issuer Authentication Flag', },
    0x9F56: {'name': 'Issuer Proprietary Bitmap (IPB)', },
    0xA5:   {'name': 'fci proprietary template', },
    0xBF0C: {'name': 'fci issuer discretionary data', },
    0xDF07: {'name': 'unknown tag DF07 (Banksys ID??)',
             'parse': lint2ascii},
    0xDF40: {'name': 'unknown tag DF40',
             'known_in_dol': True},
}


def dol_filling(tlv_dol, mode, country="any", transaction_value=0,
                 unpredictable_number=0, debug=False):
    # From book, ch 8.6.1.2
    # Most of them are null for EMV-CAP so we only check if
    # there are not some unknown stuff in the template
    dol_data = ''
    if tlv_dol is None:
        return dol_data
    for t in tlv_dol.V:
        if t.known_in_dol:
            data = '00' * t.L
            if t == 0x8A:
                # Authorization Response Code:
                if (mode == 'MAESTRO' or mode == 'BANCONTACT' or \
                    mode == 'VISA') and country == "BE":
                    # Z1: Offline declined
                    data = 'Z1'.encode('hex').upper()
                else:
                    # Z3: Unable to go online (offline declined)
                    data = 'Z3'.encode('hex').upper()
            elif t == 0x95:
                # Terminal verification results:
                if (mode == 'MAESTRO' or mode == 'BANCONTACT' or \
                    mode == 'VISA') and country == "BE":
                    # Offline data authentication was not performed
                    # Merchand forced transaction online
                    data = '8000000800'
                else:
                    # Offline data authentication was not performed
                    data = '8000000000'
            elif t == 0x9A and (mode == 'DPA' or \
                (mode == 'VISA' and not country == "BE")):
                data = '010101'
            elif t == 0x9F02 and transaction_value != 0:
                data = '%%0%ii' % (t.L * 2) % transaction_value
            elif t == 0x9F33:
                # terminal capabilities
                # 20 = Card Data Input Capability
                #      - IC with contacts
                # 80 = CVM Capability
                #      - Plaintext PIN for offline ICC verification
                # 00 = Security Capability
                data = '208000'
            elif t == 0x9F34:
                # cardholder verification method (cvm) results
                if mode == 'CAP' or mode == 'DPA':
                  # 01 = ICC Plain PIN verification
                  #      - Fail cardholder verification if...
                  # 00 = Always
                  # 02 = Successful (e.g. for offline PIN)
                    data = '010002'
                else:
                  # 00 = Fail CVM Processing
                  #      - Fail cardholder verification if CVM is unsucces...
                  # 00 = Always
                  # 00 = Unknown (for example, for signature)
                    data = '000000'
            elif t == 0x9F35:
                # terminal type
                # in [schouwenaar] it's in cdol rather than pdol
                if mode == 'CAP' or mode == 'DPA' or \
                   (mode == 'MAESTRO' and country != 'BE'):
                  # 3  = operated by cardholder
                  # 4  = Unattended, online only
                    data = '34'
                else:
                  # 3  = operated by cardholder
                  # 7  = ??
                    data = '37'
            elif t == 0x9F37 and unpredictable_number != 0:
                data = '%%0%ii' % (t.L * 2) % unpredictable_number
            assert len(data) / 2 == t.L
            dol_data += data
            if debug:
                print 'Will use %s for tag %s' % (data, t.hex_T)
        else:
            print 'Error I dont know how to handle tag %s in dol' % t.hex_T
            print 'If you want to fill it with null value,',
            print 'add a known_in_dol flag in TLVdict for that tag'
            return None
    return dol_data


def generate_otp(cid, atc, ac, iad, ipb, psn=None, debug=False):
    # Expecting arguments as hex strings
    if psn is not None:
        hex_data = psn
    else:
        hex_data = ''
    hex_data += cid + atc + ac + iad
    if debug:
        print 'Data:  ' + hex_data
        print 'Filter:' + ipb
    # Right trim hex_data to same length as ipb:
    hex_data = hex_data[:len(ipb)]
    # From http://stackoverflow.com/questions/1054116\
    #          /printing-bit-representation-of-numbers-in-python
    binary = lambda n: n > 0 and binary(n >> 1) + [int(n & 1)] or []
    # Note that created binary lists are.
    bin_data = binary(int("01" + hex_data, 16))[1:]
    bin_ipb = binary(int("01" + ipb, 16))[1:]
    # Left trim bin_data to same length as bin_ipb
    bin_data = bin_data[len(bin_data) - len(bin_ipb):]
    if debug:
        print 'Data:  ' + ''.join([str(b) for b in bin_data])
        print 'Filter:' + ''.join([str(b) for b in bin_ipb])
    otp = 0
    debug_otp = ''
    for i in range(len(bin_ipb)):
        if bin_ipb[i]:
            otp = (otp << 1) + bin_data[i]
            debug_otp += str(bin_data[i])
        else:
            debug_otp += ' '
    if debug:
        print 'OTP:   ' + debug_otp
    return otp


def generate_otp_be(atc, ac, debug=False):
    # Expecting arguments as hex strings
    #  AC_byte2 & 0x3 | AC_byte1 | ATC_byte0 | AC_byte0
    #  +report of unit to the left
    #  +truncation 8 digits
    otp = (int(ac[-6:-2], 16) & 0x3FF) << 16
    otp += int(atc[-2:], 16) << 8
    otp += int(ac[-2:], 16)
    otp += (otp % 10) * 10000000
    otp %= 100000000
    return otp


def mix_tds(ac, mdata, debug=False):
    des = DES.new(key=ac.decode('hex'), mode=DES.MODE_CBC, IV='\x00'*8)
    data = 'F'.join([str(i) for i in mdata])
    if len(data) % 2:
        data += 'F'
    # bit padding:
    data += '80'
    data += '00' * ((8 - ((len(data) / 2) % 8)) % 8)
    if debug:
        print 'TDS:   ' + data
    return des.encrypt(data.decode('hex'))[-8:].encode('hex')
