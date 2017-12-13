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

    return parser.parse_args()



def main():
    options, args = opt_args()
    if not options.share:
        print('Please provided the user that need to be shared')
        sys.exit(1)
    server = kopano.Server(options)
    shared_name = server.user(options.share)

    for user in kopano.Server(options).users(parse=True):

        # Check if shared store setting is set
        settings = json.loads(user.store.prop(PR_EC_WEBACCESS_SETTINGS_JSON).value.decode())
        if not settings['settings']['zarafa']['v1']['contexts']['hierarchy'].get('shared_stores'):
            print('Create shared store setting')
            settings['settings']['zarafa']['v1']['contexts']['hierarchy']['shared_stores'] = {}

        if not settings['settings']['zarafa']['v1']['contexts']['hierarchy']['shared_stores'].get(shared_name.name):
            print('Create shared store setting for user {}'.format(shared_name.name))
            settings['settings']['zarafa']['v1']['contexts']['hierarchy']['shared_stores'][shared_name.name] = {}


        # if folders is empty we assume that the complete store needs to be shared
        if len(options.folders) == 0:
            print('Share the complete store')
            settings['settings']['zarafa']['v1']['contexts']['hierarchy']['shared_stores'][shared_name.name]['all'] = {
                                    "folder_type": "all",
                                    "show_subfolders": False
                                }
        else:
            for folder in options.folders:
                if folder.lower() in ['inbox', 'note', 'calendar', 'contact', 'task']:
                    print('Share {}'.format(folder.lower()))
                    settings['settings']['zarafa']['v1']['contexts']['hierarchy']['shared_stores'][shared_name.name][folder.lower()] ={
                        "folder_type": folder.lower(),
                        "show_subfolders": False
                    }

        user.store.mapiobj.SetProps([SPropValue(PR_EC_WEBACCESS_SETTINGS_JSON, json.dumps(settings))])
        user.store.mapiobj.SaveChanges(KEEP_OPEN_READWRITE)


if __name__ == '__main__':
    main()
