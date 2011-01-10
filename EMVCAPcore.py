ApplicationsList = [

    # From attempts by a Fortis Vasco810 when presenting e.g. an empty JCOP:
    { 'name':'VisaRemAuthen',        'description':'VisaRemAuthen = VISA DEP ~ CAP',
      'AID':'A0000000038002',        'onVasco810?':True },
    { 'name':'SecureCode Aut',       'description':'SecureCode Aut = MasterCard CAP',
      'AID':'A0000000048002',        'onVasco810?':True },
    { 'name':'Unknown(1)',           'description':'Unknown app, BANCONTACT??',
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
        if T in TLVdict:
            self.V = TLVdict[T]['parse'](V)
            self.name = TLVdict[T]['name']
        else:
            if V is not None:
                self.V = ''.join(["%02X" % i for i in V])
            else:
                self.V = None
            self.name = 'Unknown tag %0X' % T
    def __cmp__(self, tlv2):
        if isinstance(tlv2, int):
            return tlv2 == self.T
        elif isinstance(tlv2, str):
            return tlv2 == self.name
        else:
            raise 'Comparison only with T as int or with name, sorry'
    def __eq__(self, tlv2):
        return self.__cmp__(tlv2)
    def __repr__(self):
        r = "<TLV\n"
        r += "    Tag:    %02X (%s)\n" % (self.T, self.name)
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
    #TODO: only supporting tag IDs of length 1 or 2 at the moment
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

TLVdict = {
    0x42:  {'name':'issuer authority',
            'parse':lambda x:''.join([chr(i) for i in x])}, 
    0x50:  {'name':'unknown tag 50: App Name??', #TODO
            'parse':lambda x:''.join([chr(i) for i in x])}, 
    0x57:  {'name':'track2 equivalent data',
            'parse':lambda x: ''.join(["%02X" % i for i in x])}, #TODO
    0x5A:  {'name':'application Primary Account Number (PAN)',
            'parse':lambda x: ''.join(["%02X" % i for i in x])},
    0x5F24:{'name':'application expiration date',
            'parse':lambda x:'YY=%02X MM=%02X DD=%02X' % (x[0], x[1], x[2])}, 
    0x5F25:{'name':'application effective date',
            'parse':lambda x:'YY=%02X MM=%02X DD=%02X' % (x[0], x[1], x[2])}, 
    0x5F28:{'name':'issuer country code',
            'parse':lambda x: ''.join(["%02X" % i for i in x])}, #TODO 
    0x5F2C:{'name':'Cardholder nationality',
            'parse':lambda x: ''.join(["%02X" % i for i in x])}, #TODO 
    0x5F2D:{'name':'language preference',
            'parse':lambda x :''.join([chr(i) for i in x])}, 
    0x5F34:{'name':'application PAN sequence number',
            'parse':lambda x: ''.join(["%02X" % i for i in x])}, #TODO 
    0x5F55:{'name':'unknown 5F55: country sth?',
            'parse':lambda x :''.join([chr(i) for i in x])}, 
    0x6F:  {'name':'fci template',
            'parse':TLVparser},
    0x70:  {'name':'aef data template',
            'parse':TLVparser},
    0x77:  {'name':'response message template format 2',
            'parse':TLVparser},
    0x82:  {'name':'application interchange profile (AIP)',
            'parse':lambda x: ''.join(["%02X" % i for i in x])}, #TODO
    0x84:  {'name':'dedicated file (df) name',
            'parse':lambda x: ''.join(["%02X" % i for i in x])}, 
    0x8C:  {'name':'card risk management dol 1 (cdol1)',
            'parse':lambda x: TLVparser(x, False)},
    0x8D:  {'name':'card risk management dol 2 (cdol2)',
            'parse':lambda x: TLVparser(x, False)},
    0x8E:  {'name':'cardholder verification method (CMV) list',
            'parse':lambda x: ''.join(["%02X" % i for i in x])}, #TODO
    0x94:  {'name':'application file locator',
            'parse':lambda x: ''.join(["%02X" % i for i in x])}, #TODO
    0x9F38:{'name':'processing options dol (pdol)',
            'parse':lambda x: ''.join(["%02X" % i for i in x])}, #TODO
    0x9F42:{'name':'application currency code',
            'parse':lambda x: ''.join(["%02X" % i for i in x])}, #TODO 
    0x9F44:{'name':'application currency exponent',
            'parse':lambda x :("%i: 0." % x) + ("0" * x)}, 
    0x9F55:{'name':'Issuer Authentication Flag',
            'parse':lambda x: ''.join(["%02X" % i for i in x])}, #TODO
    0x9F56:{'name':'Issuer Authentication Indicator / IPB',
            'parse':lambda x: ''.join(["%02X" % i for i in x])},
    0xA5:  {'name':'fci proprietary template',
            'parse':TLVparser}, 
    0xBF0C:{'name':'fci issuer discretionary data',
            'parse':TLVparser}, 
    0xDF07:{'name':'unknown tag DF07 (Banksys ID??)',
            'parse':lambda x :''.join([chr(i) for i in x])}, 
}

