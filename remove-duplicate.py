#!/usr/bin/env python
import kopano
import hashlib
from MAPI.Util import *


def opt_args():
    parser = kopano.parser('skpfcum')
    parser.add_option("--header", dest="header", action="store_true", help="check on duplicate header id")
    parser.add_option("--body", dest="body", action="store_true", help="check on duplicate body ")
    parser.add_option("--verbose", dest="verbose", action="store_true", help="verbose mode")

    return parser.parse_args()


def contacts(item):

    md5 = hashlib.md5(item.prop(PR_SUBJECT).value)
    md5.update(item.prop(0x8130001f).value)
    md5.update(item.prop(0x8133001f).value)
    md5.update(item.prop(0x80b5001f).value)
    md5.update(item.prop(PR_TITLE).value)
    md5.update(item.prop(PR_COMPANY_NAME).value)
    md5.update(item.prop(PR_BUSINESS_TELEPHONE_NUMBER).value)
    md5.update(item.prop(PR_HOME_TELEPHONE_NUMBER).value)
    md5.update(item.prop(PR_GIVEN_NAME).value)
    md5.update(item.prop(PR_DISPLAY_NAME).value)
    md5 = md5.hexdigest()
    return md5

def rest(item):
    md5 = hashlib.md5(item.body.html)
    try:
        md5.update(item.prop(0x0037001E).value)
    except MAPIErrorNotFound:
        md5.update(item.subject)
    md5 = md5.hexdigest()

    return md5

def main():
    options, args = opt_args()
    ignore = ['Deleted Items', 'Suggested Contacts', 'Quick Step Settings', 'Conversation Action Settings', 'RSS Feeds', 'Tasks', 'Notes', 'Journal', 'Drafts']
    for user in kopano.Server(options).users(parse=True, remote=True):
        print '%s' % user.name
        temp = []
        for folder in user.store.folders(parse=True):
            if not any(ex in folder.name for ex in ignore):
                print folder
                for item in folder.items():
                    if options.header:
                        if item.subject is not None:
                            header = item.header('Message-Id')
                            if header:
                                if any(header in checkheader for checkheader in temp):
                                    print 'delete %s' % item.header('subject')
                                    if options.modify:
                                        user.store.folder(folder.name).move(item,user.store.wastebasket)
                                else:
                                    temp.append(item.header('Message-Id'))

                    if options.body:
                        if item.subject is not None:
                            print item
                            if 'Contact' in item.prop(0x1a001f).value:
                                md5 = contacts(item)
                            else:
                                md5 =rest(item)

                            if any(tmp in md5 for tmp in temp):
                                if options.verbose:
                                    try:
                                        print 'delete %s' % item.prop(0x0037001E).value
                                    except UnicodeEncodeError as e:
                                        print e
                                if options.modify:
                                    user.store.folder(folder.name).move(item,user.store.wastebasket)
                            else:
                                temp.append(md5)
            else:
                if options.verbose:
                    print 'Folder \'%s\' is known in the exclude list' % folder.name


if __name__ == '__main__':

    main()