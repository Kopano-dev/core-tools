import kopano
from MAPI.Tags import *


def opt_args():
    parser = kopano.parser('skpcufmUP')
    parser.add_option("--dry-run", dest="dryrun", action="store_true", help="run the script without executing any actions")
    return parser.parse_args()

def main():
    options, args = opt_args()
    if not options.users:
        print('pleas use %s -u <username> ' % sys.argv[0])
        sys.exit(1)

    for user in kopano.Server(options).users():
        try:
            print(user.name)
        except UnicodeEncodeError:
            print(user.name.encode('utf-8'))
        store = user.store
        common = store.root.folder('IPM_COMMON_VIEWS')
        subtree = store.root.folder('IPM_SUBTREE')
        for folder in common.folders():
            try:
                print('Copying folder {} to root directory'.format(folder.name))
            except UnicodeEncodeError:
                print('Copying folder {} to root directory'.format(folder.name.encode('utf-8')))
            if not options.dryrun:
                common.move(folder, subtree)


if __name__ == "__main__":
    main()