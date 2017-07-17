import kopano
from MAPI.Util import *
import sys
import types
import json
import csv

def opt_args():
    parser = kopano.parser('skpcf')
    parser.add_option("--user", dest="user", action="store", help="Run script for user ")
    parser.add_option("--file", dest="file", action="store", help="NK2/CSV file")

    parser.add_option("--csv", dest="csv", action="store_true", help="Use csv file instead")
    parser.add_option("--delimiter", dest="delimiter", action="store", help="Change delimiter (default is ,)")
    return parser.parse_args()

def isString(s):
    "True if it's a python or Unicode string"
    return type(s) in (types.StringType, types.UnicodeType)

class nk2addr:

    name = u'' # pretty-printable name
    charset = None # charset of name
    address = u'' # email address

    _type = None # SMTP or xxx
    domaincheck = False
    _origlines = []
    _data = []

    def __init__(self):
        self.name = u''
        self.address = u''

    def parseFirstLine(self, b):
        self._origlines.append(b)
        B = self.strp(b)
        i = B.find('\x03\x15')
        assert(i > 0)
        self.setAddress(B[1:i])

    def parseLine(self, b):
        "parse a record full of hodge-podge bytes and email data and try to make some sense of it"
        self._origlines.append(b)
        #[f.replace(n, '') for f in c.split(n*3)]
        r = [self.strp(z) for z in b.split(NUL*3)]
        self._data.append(r)
        try:
            self.setName(unicode(r[0][1:], 'latin1'))
        except:

            print "BONK!",repr(r[0])
            raise
        self._type = r[1]

    def setName(self, name):
        assert(isString(name))
        #name = name.strip()
        self.name = self.strpApos(name)

    def setAddress(self, address):
        assert(isString(address))
        a = u''
        for z in address:
            if ord(z) < 20 or ord(z) > 128:
                break
            a += z
        self.address = self.strpApos(a)


    def strp(self, s):
        "Return string stripped of NUL bytes and unprintable characters"
        return s.replace(NUL, '')  # .replace('\x00', '')


    def strpApos(self, s):
        if len(s) == 0:
            return None
        for apo in ('"', "'"):
            if s[0] == apo and s[-1] == apo:
                s = s[1:-1]  # remove apostrophes
        return s


    def fieldSeparatedValues(self, fieldsep=u';'):
        "Return record fields separated by fieldsep. Ideal for import into some other program"
        self.sep = fieldsep
        try:
            return u'%(address)s%(sep)s%(name)s' % (dict(vars(self)))  # vars(self)
        except:
            raise


    def __str__(self):
        if self.address is None: return u''
        # try:
        # return u'"%s" <%s>' % (self.name, self.address) #'"%(name)s" <%(address)s>' % vars(self)
        # except:
        # print "KKA", type(self.address), repr(self.address)
        # raise
        try:
            return u'"%(name)s" <%(address)s>' % {'name': self.name, 'address': self.address}  # vars(self)
        except:
            print self.name
            print vars(self)
            raise


def getnk2_list(options):

    f = open(options.file, 'rb')
    filedata = f.read()
    f.close()
    NUL = '\x00'
    contactlist = []
    sep1 = '\x04H\xfe\x13'  # record separator
    sep2 = '\x00\xdd\x01\x0fT\x02\x00\x00\x01'  # record separator

    for z in filedata.split(sep1):
        for y in z.split(sep2):
            split1 = [x.replace(NUL, '') for x in
                      y.split(NUL * 3)]  # SPLIT1: split record into something useful by separating at triple NULs

            rec = nk2addr()
            if split1[1] != 'SMTP':  # SPLIT1 failed
                split2 = [x.replace(NUL, '') for x in
                          y.split(NUL * 1)]  # SPLIT2: split again, this time using single NULs as delimiter
                split1 = split2[
                         1:]  # adapt (hack) the list so the SPLIT2 fields have the same order and structure as SPLIT1
                split1[0] = ' ' + split1[0]  # more hacking of SPLIT2

            rec._type = split1[1]
            if rec._type != 'SMTP':
                continue  # couldn't find any email address in this record

            contactlist.append({'smtp_address': split1[2], 'email_address': split1[2], 'address_type':'SMTP',
                                "count": 1, "object_type": 6, 'display_name':unicode(split1[0][1:], "latin1")})
    return contactlist

def csv_list(options):
    contactlist = []
    if options.delimiter:
        delimiter = options.delimiter
    else:
        delimiter = ','
    cr = csv.reader(open(options.file, "rb"), delimiter=delimiter)
    headers = next(cr)
    total = len(headers)
    for num in range(0, total, 1):
        if headers[num] == 'address_type':
            address_type = num
        if headers[num] == 'display_name':
            display_name = num
        if headers[num] == 'email_address':
            email_address = num

    for contact in cr:

        contactlist.append({'smtp_address': contact[email_address], 'email_address': contact[email_address], 'address_type': contact[address_type],
                           "count": 1, "object_type": 6, 'display_name': contact[display_name]})

    return contactlist


def main():
    options, args = opt_args()
    if not options.csv:
        contactlist = getnk2_list(options)
    else:
        contactlist = csv_list(options)
    user = kopano.Server(options).user(options.user)
    history = user.store.prop(0X6773001F).value
    history = json.loads(history)
    for contact in contactlist:
        try:
            if contact['email_address'] not in str(history['recipients']):
                print contact
                history['recipients'].append(contact)
        except kopano.NotFoundError:
            continue

    user.store.mapiobj.SetProps([SPropValue(0X6773001F, u'%s' % json.dumps(history))])
    user.store.mapiobj.SaveChanges(KEEP_OPEN_READWRITE)

if __name__ == "__main__":
    DEBUGLEVEL = sys.argv.count('-d')
    main()