import kopano
from MAPI.Util import *
import sys

def opt_args():
    parser = kopano.parser('skpcfUPm')
    parser.add_option("--user", dest="user", action="store", help="Run script for user ")
    return parser.parse_args()

def loop_folders(store):
    options, args = opt_args()
    for folder in store.folders():
        print(folder)
        for item in folder.items():
            try:
                if item.prop(PR_BODY_W).value == 'This message is archived...':
                    if options.modify:
                        item.delete(item)
                    else:
                        print('Remove item {}'.format(item.subject))
            except kopano.errors.NotFoundError:
                continue
def main():
    options, args = opt_args()
    if not options.user:
        print("Usage: {} --user username -m".format(sys.argv[0]))


    user =  kopano.Server(options).user(options.user)

    #remove archived items from main store
    loop_folders(user.store)

    #Do the same for the archived store
    if user.archive_store:
        loop_folders(user.archive_store)


if __name__ == "__main__":
    main()