#!/usr/bin/env python

import kopano
import sys
import binascii
from MAPI.Tags import *
from datetime import datetime
from kopano.errors import *


def opt_args():
    parser = kopano.parser('skpcmUP')
    parser.add_option("--user", dest="user", action="store", help="username")
    parser.add_option("--storeid", dest="storeid", action="store", help="Store ID")
    parser.add_option("--subject", dest="subject", action="store", help="subject")
    parser.add_option("--from", dest="fromaddress", action="store", help="from address")
    parser.add_option("--sourcekey", dest="sourcekey", action="store", help="Sourcekey to look for")
    parser.add_option("--folder", dest="folder", action="store", help="folder")
    parser.add_option("--between", dest="between", action="store", help="yyyy-mm-dd yyyy-mm-dd")
    parser.add_option("--softdelete", dest="soft", action="store_true", help="search in softdelete")
    parser.add_option("--public", dest="public", action="store_true", help="Search in public store")
    parser.add_option("--company", dest="company", action="store", help="search in this company(Public store only)")
    parser.add_option("--eml", dest="eml", action="store_true", help="save as eml")
    parser.add_option("--mapi", dest="mapi", action="store_true", help="save the mapi properties")
    parser.add_option("--delete", dest="delete", action="store_true", help="Delete item")
    parser.add_option("--stop-after-first-hit", dest="stop", action="store_true", help="Stop search after first hit")
    return parser.parse_args()


def getprop(item, myprop):
    try:
        return item.prop(myprop).value
    except Exception:
        return None


def printprop(typename, item):
    if typename == 'PT_MV_BINARY':
        listItem = []
        for i in item:
            listItem.append(str(binascii.hexlify(i)).upper())
        return listItem
    if typename == 'PT_OBJECT':
        return None
    if typename == 'PT_BINARY':
        return str(binascii.hexlify(item)).upper()
    if typename == 'PT_UNICODE':
        try:
            return item.encode('utf-8')
        except Exception:
            return item
    else:
        return item


def searchitem(folder, options):
    for item in folder.items():
        subject = getprop(item, 0x0037001E)
        if options.subject:
            if item.subject:
                if options.subject in item.subject:
                    print('Found item \'{}\' in folder {}'.format(subject, folder.name))
                    if options.eml:
                        saveeml(item)
                    if options.mapi:
                        props = printmapiprops(item)
                        f = open('{}-{}.prop'.format(item.subject, item.entryid), 'w')
                        for prop in props:
                            f.write('{0:5}  {1:37}  {2:8}  {3:10}  {4:1}\n'.format(prop[0], prop[1], prop[2], prop[3],
                                                                                   prop[4]))
                        f.close()
                    if options.delete:
                        print('Deleting \'{}\''.format(subject))
                        folder.delete(item)
                    if options.stop:
                        return None

        if options.sourcekey:
            if options.sourcekey.upper() == binascii.hexlify(getprop(item, 0x65e00102)).upper():
                print('Found item \'{}\' in folder {} '.format(subject, folder.name))
                if options.eml:
                    saveeml(item)
                if options.mapi:
                    props = printmapiprops(item)
                    f = open('%s-%s.prop' % (item.subject, item.entryid), 'w')
                    for prop in props:
                        f.write(
                            '{0:5}  {1:37}  {2:8}  {3:10}  {4:1}\n'.format(prop[0], prop[1], prop[2], prop[3], prop[4]))
                    f.close()
                if options.delete:
                    print('Deleting \'{}\''.format(subject))
                    folder.delete(item)
                if options.stop:
                    return None

        if options.fromaddress:
            if str(options.fromaddress) in str(getprop(item, 0x42001f)):
                print('Found item \'{}\' in folder \'{}\' '.format(item.entryid, folder.name))
                if options.eml:
                    saveeml(item)
                if options.mapi:
                    props = printmapiprops(item)
                    f = open('{}-{}.prop'.format(item.subject, item.entryid), 'w')
                    for prop in props:
                        f.write(
                            '{0:5}  {1:37}  {2:8}  {3:10}  {4:1}\n'.format(prop[0], prop[1], prop[2], prop[3], prop[4]))
                    f.close()
                if options.delete:
                    print('Deleting \'{}\''.format(subject))
                    folder.delete(item)
                if options.stop:
                    return None
    return None


def saveeml(item):
    print('Saving \'{}\' as eml file'.format(item.subject))
    f = open('{}-{}.eml'.format(item.subject, item.entryid), 'w')
    f.write(item.eml())
    f.close()
    return None


def printmapiprops(item):
    props = []
    for prop in item.props():
        if hex(prop.proptag) == "0x10130102":
            props.append([prop.id_, prop.idname, hex(prop.proptag), prop.typename, printprop(prop.typename, prop.value),
                          prop.value])
        else:
            props.append(
                [prop.id_, prop.idname, hex(prop.proptag), prop.typename, printprop(prop.typename, prop.value)])

    return props


def softdelete(user, subject):
    for folder in user.store.folders():
        # print folder
        table = folder.mapiobj.GetContentsTable(SHOW_SOFT_DELETES)
        table.SetColumns([PR_SUBJECT, PR_ENTRYID, PR_MESSAGE_SIZE], 0)
        rows = table.QueryRows(-1, 0)

        for row in rows:
            for tag in row:
                if tag.ulPropTag == PR_SUBJECT:
                    if subject.lower() in tag.Value.lower():
                        print('found \'{}\' in softdelete {}'.format(tag.Value, folder.name))
    return None


def publicstore(options, company):
    for folder in kopano.Server(options).company(company).public_store.folders():
        for item in folder.items():
            subject = getprop(item, 0x0037001E)
            if options.subject:
                if item.subject:
                    if options.subject in item.subject:
                        print('Found item \'{}\' in folder {} '.format(subject, folder.name))
                        if options.eml:
                            saveeml(item)
                        if options.mapi:
                            props = printmapiprops(item)
                            f = open('{}-{}.prop'.format(item.subject, item.entryid), 'w')
                            for prop in props:
                                f.write(
                                    '{0:5}  {1:37}  {2:8}  {3:10}  {4:1}\n'.format(prop[0], prop[1], prop[2], prop[3],
                                                                                   prop[4]))
                            f.close()
            if options.sourcekey:
                if options.sourcekey.upper() == binascii.hexlify(getprop(item, 0x65e00102)).upper():
                    print('Found item \'{}\' in folder {} '.format(subject, folder.name))
                    if options.eml:
                        saveeml(item)
                    if options.mapi:
                        props = printmapiprops(item)
                        f = open('{}-{}.prop'.format(item.subject, item.entryid), 'w')
                        for prop in props:
                            f.write('{0:5}  {1:37}  {2:8}  {3:10}  {4:1}\n'.format(prop[0], prop[1], prop[2], prop[3],
                                                                                   prop[4]))
                        f.close()


def findbetween(options):
    user = kopano.Server(options).user(options.user)

    begin = datetime.strptime('{} 00:00:00'.format(options.between.split()[0]), '%Y-%m-%d 00:00:00')
    end = datetime.strptime('{} 00:00:00'.format(options.between.split()[1]), '%Y-%m-%d 00:00:00')
    print('{0:20}    {1:150}   {2:10} '.format('Folder', 'Subject', 'Date'))
    for folder in user.store.folders():
        for item in folder.items():
            try:
                if item.prop(PR_CLIENT_SUBMIT_TIME).value >= begin and item.prop(PR_CLIENT_SUBMIT_TIME).value <= end:
                    print('{0:20}    {1:150}   {2:10} '.format(folder.name, item.subject,
                                                               str(item.prop(PR_CLIENT_SUBMIT_TIME).value)))
            except NotFoundError:
                continue


def main():
    options, args = opt_args()
    if options.user:
        user = kopano.Server(options).user(options.user)
    elif options.storeid:
        user = kopano.Server(options).store(options.storeid).user
    else:
        print('Use either --user or --storeid')
        sys.exit(1)

    if options.soft:
        print('Searching in softdelete')
        softdelete(user, options.subject)
        sys.exit(0)
    if options.public:
        if not options.company:
            company = 'Default'
        else:
            company = options.company
        print('Searching in public store')
        publicstore(options, company)
        sys.exit(0)
    if options.between:
        print('find item between {} and {}'.format(options.between.split()[0], options.between.split()[1]))
        findbetween(options)
        sys.exit(0)
    if options.folder:
        folder = user.store.folder(options.folder)
        print('Searching in folder {}'.format(options.folder))
        searchitem(folder, options)
    else:
        print('Searching in all folders')
        for folder in user.store.folders():
            searchitem(folder, options)


if __name__ == "__main__":
    main()
