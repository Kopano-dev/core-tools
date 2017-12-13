#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

import kopano
from MAPI.Util import *
import sys
import json
import binascii

def opt_args():
    parser = kopano.parser('skpcuf')
    parser.add_option("--share-store", dest="share", action="store", help="Username of store that needed to be shared")
    parser.add_option("--all", dest="all", action="store_true", help="Run for all users=")

    return parser.parse_args()



def main():
    options, args = opt_args()
    if not options.share:
        print('Please provided the user that need to be shared')
        sys.exit(1)
    if not options.users and not options.all:
        print('If you want to share the store for all user pass the parameter --all otherwise use -u username')
        sys.exit(1)
    server = kopano.Server(options)
    shared_store = server.user(options.share)

    for user in kopano.Server(options).users(parse=True):
        if user.store:
            if user.name != shared_store.name:
                print(user.name)
                # Check if shared store setting is set
                try:
                    settings = json.loads(user.store.prop(PR_EC_WEBACCESS_SETTINGS_JSON).value.decode())
                except kopano.NotFoundError:
                    settings = json.loads(
                        '{"settings": {"zarafa": {"v1": {"contexts": {"mail": {}, "hierarchy":{} }}}}}')

                if not settings['settings']['zarafa']['v1']['contexts']['hierarchy'].get('shared_stores'):
                    settings['settings']['zarafa']['v1']['contexts']['hierarchy']['shared_stores'] = {}

                if not settings['settings']['zarafa']['v1']['contexts']['hierarchy']['shared_stores'].get(shared_store.name):
                    settings['settings']['zarafa']['v1']['contexts']['hierarchy']['shared_stores'][shared_store.name] = {}


                # if folders is empty we assume that the complete store needs to be shared
                if len(options.folders) == 0:
                    print('Share the complete store')
                    settings['settings']['zarafa']['v1']['contexts']['hierarchy']['shared_stores'][shared_store.name]['all'] = {
                                            "folder_type": "all",
                                            "show_subfolders": False
                                        }
                else:
                    for folder in options.folders:
                        if folder.lower() in ['inbox', 'note', 'calendar', 'contact', 'task']:
                            print('Share {}'.format(folder.lower()))
                            settings['settings']['zarafa']['v1']['contexts']['hierarchy']['shared_stores'][shared_store.name][folder.lower()] ={
                                "folder_type": folder.lower(),
                                "show_subfolders": False
                            }

                user.store.mapiobj.SetProps([SPropValue(PR_EC_WEBACCESS_SETTINGS_JSON, json.dumps(settings))])
                user.store.mapiobj.SaveChanges(KEEP_OPEN_READWRITE)


if __name__ == '__main__':
    main()
