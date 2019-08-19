import kopano
from MAPI.Util import PR_SOURCE_KEY
import sys 
import binascii

def opt_args():
    parser = kopano.parser('skpcufmUP')
    parser.add_option("--id", dest="item_id", action="store", help="ID to search for")
    return parser.parse_args()

def main():
    options, _ = opt_args()
    if len (options.users) == 0 or not options.item_id: 
        print('No user or item id specified')
        sys.exit(1)
    for user in kopano.Server(options).users():
        try:
            item = user.item(options.item_id)
            print('Found item {} in folder {}'.format(item.subject, item.folder.path))
            sys.exit(0)
        except (kopano.errors.ArgumentError, kopano.errors.NotFoundError):
            print('ID is not an entryid searching for sourcekey, this can take a while')
        for folder in user.store.folders():
            for item in folder.items():
                sourcekey  = binascii.hexlify(item.prop(PR_SOURCE_KEY).value).lower()
                item_id = options.item_id.encode('utf-8').lower()
                if sourcekey == item_id:
                    print('Found item {} in folder {}'.format(item.subject, item.folder.path))
                    sys.exit(0)

    print('Item ID not found')
if __name__ == "__main__":
    main()