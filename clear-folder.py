import kopano
from MAPI.Util import  *

def opt_args():
    parser = kopano.parser('skpcufm')
    return parser.parse_args()

def main():
    options, args = opt_args()
    if not options.users or not options.folders:
        print 'pleas use %s -u <username> -f <foldername>' % sys.argv[0]
        sys.exit(1)
    for user in kopano.Server(options).users():
        print user.name
        for folder in user.store.folders():
            print 'Clearing folder \'%s\'' % folder.name
            folder.empty()

if __name__ == "__main__":
    main()