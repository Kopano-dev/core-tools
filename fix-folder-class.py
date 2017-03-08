#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4


try:
    import kopano
except ImportError:
    import zarafa as kopano
from MAPI.Util import *
import itertools


def opt_args():
    parser = kopano.parser('skpcuf')
    parser.add_option("--list", dest="list", action="store_true", help="List all folders that is missing the PR_CONTAINER_CLASS property")
    parser.add_option("--auto", dest="auto", action="store_true", help="Try to auto fix the PR_CONTAINER_CLASS")
    parser.add_option("--mail", dest="mail", action="store_true", help="Change all the missing PR_CONTAINER_CLASS property to IPF.Note(mail folder) ")

    return parser.parse_args()

def main():
    options, args = opt_args()

    for user in kopano.Server(options).users(options.users):
        storefolders = []
        store = user.store
        if not store:
            continue
        print user.name

        for folder in store.folders():
            if folder.container_class == '':
                if options.list:
                    storefolders.append({'name':folder.name, 'entryid': folder.entryid})

                if options.mail:
                    folder.container_class = 'IPF.Note'

                if options.auto:
                    messageclass={}
                    for item in itertools.islice(folder.items(), 10):
                        if item.message_class not in messageclass:
                            messageclass.update({item.message_class: 1})
                        else:
                            messageclass[item.message_class] += 1
                    if len(messageclass) > 1:
                        folder.container_class = 'IPF.Note'
                    else:
                        folder.container_class = messageclass.popitem()[0].replace('IPM','IPF')

        if options.list:
            if len(storefolders) > 0:
                print 'Following folders are broken:'
                print '{:50} {:5}'.format('Folder name', 'Entryid')
                for folder in storefolders:
                    print '{:50} {:5}'.format(folder['name'], folder['entryid'])
            else:
                print 'No broken folders found'

if __name__ == "__main__":
    main()
