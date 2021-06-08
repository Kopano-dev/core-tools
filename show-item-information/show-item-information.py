#!/usr/bin/env python3

import sys
from uuid import UUID
from datetime import datetime
try:
    from MAPI.Tags import *
    import kopano
    from kopano.errors import *
except ImportError:
    print("Kopano python packages are needed")
    sys.exit(1)
try:
    from tabulate import tabulate
except ImportError:
    print('tabulate package need: pip3 install tabulate')
    sys.exit(1)


def opt_args():
    parser = kopano.parser('skpcmUPufv')
    parser.add_option("--search", dest="search", action="store", help="string to search for ")
    parser.add_option("--loop", dest="loop", action="store_true", help="Do not use the search engine")
    parser.add_option("--public", dest="public", action="store_true", help="search in public store")

    return parser.parse_args()

def loop_over_items(folder, subject):
    items = []

    for item in folder.items():
        if subject in item.subject:
            items.append(item)

    return items
def main():
    options, args = opt_args()
    
    server = kopano.Server(options)
    users = []
    if options.public:
        users = [server.public_store]
    
    if len(options.users) > 0:
        users = users + list(server.users())
    
    for user in users:
        try:
            store = user.store
            print('Running script for user {}'.format(user.name))
        except AttributeError:
            store = user
            print('Running script for public store')
        
        if len(options.folders) > 0:
            folders = list(store.folders())
        else:
            # In the public store your are unable to directly search on the subtree so we collect all the top folders instead
            if options.public:
                folders  = store.subtree.folders(recurse=False)
                print('Doing a global search on the public store takes time, please be patient')
            else:
                folders = [store.subtree]
        
        found_items = []
        for folder in folders:
            if options.verbose:
                print('searching in folder {}'.format(folder.name))
            if not options.loop:
                try:
                    found_items =  found_items + list(folder.search(options.search, recurse=True))
                except UnicodeDecodeError:
                    found_items =  found_items + list(folder.search(options.search.decode('utf-8'), recurse=True))
            else:
                found_items = found_items +  loop_over_items(folder, options.search)

        table_header = ["Subject", 'Folder', 'Time/Date', 'Owner', 'Created', 'Last modified', 'Last modified user']
        table_data = []
        errors = 0
        for item in found_items:

            # item.start is only available for appointment
            if item.start:
                date = "{} - {}".format(item.start, item.end) 
            else:
                date = "None"

            ## We use search folders and therefore we do not know the original folder, here we open the item again
            folder_name = store.item(entryid=item.entryid).folder.path
 

            try:
               owner = item.prop(PR_SENDER_NAME_W).value
            except NotFoundError as e:
                try:
                    owner = item.prop(PR_RECEIVED_BY_NAME_W).value
                except NotFoundError as e:
                    owner = 'Unkown'
                
            try :
                table_data.append([item.subject, folder_name, date, owner, item.created, item.prop(PR_LAST_MODIFIER_NAME_W).value, item.prop(PR_LAST_MODIFICATION_TIME).value])
            except Exception as e:
                errors += 1
                if options.verbose:
                    print("error: {} {} ({})".format(item.subject, item.entryid, str(e)))
        
        if errors > 0:
            if not options.verbose:
                print('Unable to parse {} items. Run in verbose mode to show more information'.format(errors))
                
        print(tabulate(table_data, headers=table_header,tablefmt="grid"))

if __name__ == "__main__":
    main()
