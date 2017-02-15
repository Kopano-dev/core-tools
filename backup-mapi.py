import kopano
from MAPI.Util import  *
import binascii
import json
import datetime
import time

def opt_args():
    parser = kopano.parser('skpcfm')
    parser.add_option("--user", dest="user", action="store", help="username")
    parser.add_option("--subject", dest="subject", action="store", help="subject")
    parser.add_option("--backup", dest="backup", action="store_true", help="backup the mapi properties")
    parser.add_option("--restore", dest="restore", action="store_true", help="restore the mapi properties")

    return parser.parse_args()


def printprop(typename, item):
    if typename == 'PT_MV_BINARY':
        listItem = []
        for i in item:
            listItem.append(str(binascii.hexlify(i)).upper())
        return listItem
    elif typename == 'PT_OBJECT':
        return None
    elif typename == 'PT_BINARY':
        return str(binascii.hexlify(item)).upper()
    elif typename == 'PT_UNICODE':
        try:
            return item.encode('utf-8')
        except:
            return item
    elif typename == 'PT_SYSTIME':
        epoch = datetime.datetime.utcfromtimestamp(0)
        return (item - epoch).total_seconds()

    else:
        return item

def convertback(prop):

    if prop['typename'] == 'PT_SYSTIME':
        epoch = long(prop['value'])
        datetime_date = datetime.datetime.fromtimestamp(epoch)
        return  MAPI.Time.unixtime(time.mktime(datetime_date.timetuple()))
    elif prop['typename'] == 'PT_BINARY':
        return str(binascii.unhexlify(prop['value']))

    return prop['value']

def printmapiprops(item):
    props = []
    for prop in item.props():
        props.append({'id_':prop.id_, 'idname':prop.idname, 'proptag':hex(prop.proptag), 'typename':prop.typename, 'value':printprop(prop.typename, prop.value)})
    return props


def main():
    options, args = opt_args()
    emails = {}
    if not options.user :
        print 'pleas use %s --user  <username>' % sys.argv[0]
        sys.exit(1)
    user = kopano.Server(options).user(options.user)
    folder = user.store.calendar
    if options.backup:
        for item in folder.items():
            emails[item.subject] = printmapiprops(item)

        with open('calendaritems.json', 'w') as outfile:
            json.dump(emails, outfile)

    if options.restore:
        json_data = open('calendaritems.json').read()
        restoreitems = json.loads(json_data)
        for item in restoreitems:
            injectitem = folder.create_item()
            for prop in restoreitems[item]:
                value = convertback(prop)
                if prop['proptag']:
                    injectitem.mapiobj.SetProps([MAPI.Util.SPropValue(int(prop['proptag'][:-1], 16),value)])
                    injectitem.mapiobj.SaveChanges(MAPI.Util.KEEP_OPEN_READWRITE)
                else:
                    print prop

if __name__ == "__main__":
    main()