#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4


try:
    import kopano
except ImportError:
    import zarafa as kopano
import itertools
import json
import os
import sys

def opt_args():
    parser = kopano.parser('skpcuf')
    parser.add_option("--public", dest="public", action="store_true",
                      help="Run script for public folder")
    parser.add_option("--list", dest="list", action="store_true",
                      help="List all folders that is missing the PR_CONTAINER_CLASS property")
    parser.add_option("--restore", dest="restore", action="store_true", help="Restore the json file")
    parser.add_option("--auto", dest="auto", action="store_true", help="Try to auto fix the PR_CONTAINER_CLASS")
    parser.add_option("--mail", dest="mail", action="store_true",
                      help="Change all the missing PR_CONTAINER_CLASS property to IPF.Note(mail folder) ")

    return parser.parse_args()


def fix_folders(store, user, options):

    storefolders = []
    if options.restore:
        if os.path.isfile('%s.json' % user.name):
            with open('%s.json' % user.name) as json_data:
                data = json.load(json_data)
                for restorefolder in data:
                    if restorefolder['folder-type']:
                        folder = user.store.folder(entryid=restorefolder['entryid'])
                        folder.container_class = 'IPF.%s' % restorefolder['folder-type']
                        try:
                            print 'Changed %s folder-type to IPF.%s ' % (
                                folder.name.encode('utf-8'), restorefolder['folder-type'])
                        except Exception as e:
                            print 'Changed %s folder-type to IPF.%s ' % (
                                folder.name, restorefolder['folder-type'])

    for folder in store.folders():
        if not folder.container_class:
            if options.list:
                storefolders.append({'name': folder.name, 'entryid': folder.entryid, 'folder-type': ''})

            if options.mail:
                folder.container_class = 'IPF.Note'

            if options.auto:
                messageclass = {}
                for item in itertools.islice(folder.items(), 10):
                    if item.message_class not in messageclass:
                        messageclass.update({item.message_class: 1})
                    else:
                        messageclass[item.message_class] += 1
                if len(messageclass) == 0:
                    storefolders.append({'name': folder.name, 'entryid': folder.entryid, 'folder-type': ''})
                elif len(messageclass) > 1:
                    folder.container_class = 'IPF.Note'
                else:
                    folder.container_class = messageclass.popitem()[0].replace('IPM', 'IPF')

    if options.list or len(storefolders) > 0:
        if len(storefolders) > 0:
            with open('%s.json' % user.name, 'w') as outfile:
                json.dump(storefolders, outfile, indent=4)
            print '%s.json created' % user.name
            if options.list:
                print 'Following folders are broken:'
            else:
                print 'Can\'t fix the following folders,  please fix them manually:'
            print '{:50} {:5}'.format('Folder name', 'Entryid')
            for folder in storefolders:
                print '{:50} {:5}'.format(folder['name'].encode('utf8'), folder['entryid'])
        else:
            print 'No broken folders found'

def main():
    options, args = opt_args()
    server = kopano.Server(options)
    if options.public:
        store = server.public_store
        if not store:
            print 'No public store found'
            sys.exit(1)
        user = 'Public'
        fix_folders(store, user, options)
        sys.exit(0)

    for user in server.users(options.users):
        store = user.store
        if not store:
            continue
        print user.name
        fix_folders(store, user, options)

if __name__ == "__main__":
    main()