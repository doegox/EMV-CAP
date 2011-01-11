ApplicationsList = [

    # From attempts by a Fortis Vasco810 when presenting e.g. an empty JCOP:
    { 'name':'VisaRemAuthen',        'description':'VisaRemAuthen = VISA DEP ~ CAP',
      'AID':'A0000000038002',        'onVasco810?':True },
    { 'name':'SecureCode Aut',       'description':'SecureCode Aut = MasterCard CAP',
      'AID':'A0000000048002',        'onVasco810?':True },
    { 'name':'BANCONTACT',           'description':'BANCONTACT',
      'AID':'D056000666111010',      'onVasco810?':True },
    { 'name':'VISA electron',        'description':'VISA Electron (Debit)',
      'AID':'A0000000032010',        'onVasco810?':True },
    { 'name':'VISA credit',          'description':'Standard VISA credit card',
      'AID':'A0000000031010',        'onVasco810?':True },
    { 'name':'MasterCard credit',    'description':'MasterCard credit (or debit?)',
      'AID':'A0000000041010',        'onVasco810?':True },
    { 'name':'MAESTRO',              'description':'MAESTRO',
      'AID':'A0000000043060',        'onVasco810?':True },

    # Other sources of AID:
    # http://globalblindspot.blogspot.com/2010/06/emvcap-application-ids.html
    # https://spreadsheets.google.com/pub?key=0Aulc2eB5eBHZdDRIU0Zva2U2NWY4N0ppNFFrN3hEVVE
    { 'name':'VISA V-PAY?',          'description':'VISA V-PAY?',
      'AID':'A0000000032020',        'onVasco810?':False },
    { 'name':'VISA Interlink',       'description':'VISA Interlink',
      'AID':'A0000000033010',        'onVasco810?':False },
    { 'name':'VISA Specific(1)',     'description':'VISA Specific(1)',
      'AID':'A0000000034010',        'onVasco810?':False },
    { 'name':'VISA Specific(2)',     'description':'VISA Specific(2)',
      'AID':'A0000000035010',        'onVasco810?':False },
    { 'name':'VISA Plus',            'description':'VISA Plus',
      'AID':'A0000000038010',        'onVasco810?':False },
    { 'name':'MasterCard unknown1',  'description':'MasterCard unknown1',
      'AID':'A00000000410101213',    'onVasco810?':False },
    { 'name':'MasterCard unknown2',  'description':'MasterCard unknown2',
      'AID':'A00000000410101215',    'onVasco810?':False },
    { 'name':'MasterCard Specific3', 'description':'MasterCard Specific3',
      'AID':'A0000000042010',        'onVasco810?':False },
    { 'name':'MasterCard Specific4', 'description':'MasterCard Specific4',
      'AID':'A0000000043010',        'onVasco810?':False },
    { 'name':'MasterCard Specific5', 'description':'MasterCard Specific5',
      'AID':'A0000000044010',        'onVasco810?':False },
    { 'name':'MasterCard Specific6', 'description':'MasterCard Specific6',
      'AID':'A0000000045010',        'onVasco810?':False },
    { 'name':'MasterCard Cirrus',    'description':'MasterCard Cirrus (interbank network)',
      'AID':'A0000000046000',        'onVasco810?':False },
    { 'name':'UK Maestro',           'description':'UK Domestic Maestro - Switch (debit card)',
      'AID':'A0000000050001',        'onVasco810?':False },
    { 'name':'UK Maestro Solo',      'description':'UK Domestic Maestro - Switch (debit card) Solo',
      'AID':'A0000000050001',        'onVasco810?':False },
    { 'name':'American Express',     'description':'American Express credit/debit',
      'AID':'A0000000250000',        'onVasco810?':False },
    { 'name':'American Express 2',   'description':'American Express 2',
      'AID':'A00000002501',          'onVasco810?':False },
# TODO:
# A0000000291010		ATM cardLINK (UK) ATM network
# A0000001410001		Consorzio BANCOMATPagobancomatItalian domestic debit card
# A0000001510000
# A0000002040000?
# A0000002281010		SAMASaudi Arabia domestic credit/debit card (Saudi Arabia Monetary Agency)
# A0000002771010		INTERACCanadian domestic credit/debit card
# A000000308000010000100
# A0000003591010028001	ZKAGirocard

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
        self.known_in_cdol = False
        if T in TLVdict:
            self.name = TLVdict[T]['name']
            if 'known_in_cdol' in TLVdict[T]:
                self.known_in_cdol = TLVdict[T]['known_in_cdol']
        else:
            self.name = 'Unknown tag %0X' % T
        if V is None:
            self.V = None
        else:
            if T in TLVdict and 'parse' in TLVdict[T]:
                self.V = TLVdict[T]['parse'](V)
            else:
                if self.type == 0x01: # constructed
                    self.V = TLVparser(V)
                else:
                    self.V = ''.join(["%02X" % i for i in V])

    def __cmp__(self, tlv2):
        if isinstance(tlv2, int):
            return tlv2 == self.T
        elif isinstance(tlv2, str):
            return tlv2 == self.name
        else:
            raise 'Comparison only with T as int or with name, sorry'
    def __iter__(self):
        return self.V.__iter__()
    def get(self, name):
        if name in self:
            return self.V[self.V.index(name)]
        else:
            return None
    def __eq__(self, tlv2):
        return self.__cmp__(tlv2)
    def __repr__(self):
        r = "<TLV\n"
        r += "    Tag:    %02X (%s)\n" % (self.T, self.name)
        classnames=['universal', 'application', 'context specific', 'private']
        r += "            %s class\n" % classnames[self.tclass]
        typenames=['primitive', 'constructed']
        r += "            %s\n" % typenames[self.type]
        r += "    Length: %i bytes\n" % self.L
        r += "    Value:  "
        if isinstance(self.V, list):
            r += '\n    %s\n' % repr(self.V).replace('\n','\n    ')
        else: 
            r += "%s\n" % self.V
        r += ">"
        return r

def TLVparser(raw, hasdata=True):
    if len(raw) == 0:
        return False
    # EMV 2000 only supports tagnames of length 1 or 2 (from book, ch4.2)
    # should we support lengths > 127 (and length coded on more than one byte)?
    if raw[0] & 0x1F == 0x1F:
        T = (raw[0]<<8) + raw[1]
        L = raw[2]
        raw = raw[3:]
    else:
        T = raw[0]
        L = raw[1]
        raw = raw[2:]

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

# TODO get some more TLV from https://cardpeek.googlecode.com/svn-history/trunk/dot_cardpeek_dir/scripts/emv.lua
# and from http://www.emvlab.org/emvtags/all/
# and from http://cheef.ru/docs/HowTo/TAG.info
TLVdict = {
    0x42:  {'name':'issuer authority',
            'parse':lambda x:''.join([chr(i) for i in x])}, 
    0x50:  {'name':'Application Label', #TODO
            'parse':lambda x:''.join([chr(i) for i in x])}, 
    0x57:  {'name':'track2 equivalent data',},
    0x5A:  {'name':'application Primary Account Number (PAN)',},
    0x5F24:{'name':'application expiration date',
            'parse':lambda x:'YY=%02X MM=%02X DD=%02X' % (x[0], x[1], x[2])}, 
    0x5F25:{'name':'application effective date',
            'parse':lambda x:'YY=%02X MM=%02X DD=%02X' % (x[0], x[1], x[2])}, 
    0x5F28:{'name':'issuer country code',},
    0x5F2A:{'name':'Transaction Currency Code',
            'known_in_cdol':True},
    0x5F2C:{'name':'Cardholder nationality',},
    0x5F2D:{'name':'language preference',
            'parse':lambda x :''.join([chr(i) for i in x])}, 
    0x5F34:{'name':'application PAN sequence number',},
    0x5F55:{'name':'Issuer Country Code (alpha2 format)',
            'parse':lambda x :''.join([chr(i) for i in x])}, 
    0x6F:  {'name':'fci template',},
    0x70:  {'name':'aef data template',},
    0x77:  {'name':'response message template format 2',},
    0x80:  {'name':'Command Template',},
    0x82:  {'name':'application interchange profile (AIP)',},
    0x83:  {'name':'Command Template',},
    0x84:  {'name':'dedicated file (df) name',
            'parse':lambda x: ''.join(["%02X" % i for i in x])}, 
    0x8A:  {'name':'Authorization Response Code',
            'known_in_cdol':True},
    0x8C:  {'name':'card risk management dol 1 (cdol1)',
            'parse':lambda x: TLVparser(x, False)},
    0x8D:  {'name':'card risk management dol 2 (cdol2)',
            'parse':lambda x: TLVparser(x, False)},
    0x8E:  {'name':'cardholder verification method (CMV) list',},
    0x91:  {'name':'issuer authentication data',
            'known_in_cdol':True},
    0x94:  {'name':'application file locator',},
    0x95:  {'name':'Terminal Verification Results',
            'known_in_cdol':True},
    0x9A:  {'name':'Transaction Date',
            'known_in_cdol':True},
    0x9C:  {'name':'Transaction Type',
            'known_in_cdol':True},
    0x9F02:{'name':'Authorized Amount (AA)',
            'known_in_cdol':True},
    0x9F03:{'name':'Other Amount',
            'known_in_cdol':True},
    0x9F10:{'name':'Issuer Application Data',},
    0x9F12:{'name':'Application Preferred Name',
            'parse':lambda x:''.join([chr(i) for i in x])}, 
    0x9F17:{'name':'PIN Retry Counter',
            'parse':lambda x: x[0]},
    0x9F1A:{'name':'Terminal Country Code',
            'known_in_cdol':True},
    0x9F26:{'name':'Application Cryptogram (AC)',},
    0x9F27:{'name':'cryptogram information data',},
    0x9F36:{'name':'Application Transaction counter (ATC)',},
    0x9F34:{'name':'cardholder verification method (cvm) results',
            'known_in_cdol':True},
    0x9F35:{'name':'terminal type',},
    0x9F37:{'name':'Unpredictable Number (UN)',
            'known_in_cdol':True},
    0x9F38:{'name':'processing options dol (pdol)',
            'parse':lambda x: TLVparser(x, False)},
    0x9F42:{'name':'application currency code',},
    0x9F44:{'name':'application currency exponent',
            'parse':lambda x :("%i (0." % x[0]) + ("0" * x[0]) + ")"}, 
    0x9F4C:{'name':'ICC dynamic number',
            'known_in_cdol':True},
    0x9F55:{'name':'Issuer Authentication Flag',},
    0x9F56:{'name':'Issuer Authentication Indicator / IPB',},
    0xA5:  {'name':'fci proprietary template',},
    0xBF0C:{'name':'fci issuer discretionary data',},
    0xDF07:{'name':'unknown tag DF07 (Banksys ID??)',
            'parse':lambda x :''.join([chr(i) for i in x])}, 
}

def cdol_filling(tlv_cdol, tlv_aid, transaction_value = 0, unpredictable_number = 0, debug = False):
    # From book, ch 8.6.1.2
    # Most of them are null for EMV-CAP so we only check if there are not some unknown stuff in the template
    cdol_data=''
    for t in tlv_cdol.V:
        if t.known_in_cdol:
            data = '00' * t.L
            if t == 0x8A:
                # Authorization Response Code: Z3: Unable to go online (offline declined)
                data = '5A33'
            if t == 0x95:
                # Terminal verification results: offline data authentication was not performed
                data = '80' + '00' * (t.L -1)
            elif t == 0x9A and tlv_aid.V == 'A0000000038002': # VisaRemAuthen
                data = '010101'
            elif t == 0x9F02 and transaction_value != 0: # TODO
                print 'Error CAP Sign not yet implemented'
                return None
            elif t == 0x9F37 and unpredictable_number != 0:
                data = '%08i' % unpredictable_number
            elif t == 0x9F34:
                # cardholder verification method (cvm) results
                  # 01 = ICC Plain PIN verification - Fail cardholder verification if...
                  # 00 = Always
                  # 02 = Successful (e.g. for offline PIN)
                assert t.L == 3
                data = '010002'
            cdol_data += data
            if debug:
                print 'Will use %s for tag %s' % (data, t.hex_T)
        else:
            print 'Error I dont know how to handle %s in cdol' % t.hex_T
            return None
    return cdol_data
