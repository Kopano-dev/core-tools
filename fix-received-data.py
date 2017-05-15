try:
    import kopano
except ImportError:
    import zarafa as kopano
    print 'You are running a Kopano script in a Zarafa environment\n' \
          'Please be aware that any kind of error handling is not working as expected'
from MAPI.Util import *
from time import mktime
from dateutil.parser import parse

def opt_args():
    parser = kopano.parser('skpcufm')
    parser.add_option("--dry-run", dest="dryrun", action="store_true", help="run the script without executing any actions")
    return parser.parse_args()

def main():
    options, args = opt_args()
    if not options.users:
        print 'pleas use %s -u <username> ' % sys.argv[0]
        sys.exit(1)

    for user in kopano.Server(options).users():
        print user.name
        total_count = 0
        for folder in user.store.folders():
            folder_item_count = 0
            for item in folder.items():
                get_date = item.headers().get('date')
                if get_date:
                    new_date = MAPI.Time.unixtime(mktime(parse(get_date).timetuple()))
                    if not options.dryrun:
                        item.mapiobj.SetProps([SPropValue(PR_MESSAGE_DELIVERY_TIME, new_date)])
                        item.mapiobj.SaveChanges(KEEP_OPEN_READWRITE)
                    total_count += 1
                    folder_item_count += 1
            print 'Changed %s item(s) in folder \'%s\'' % (folder_item_count, folder.name)


    print '\nChanged %s items(s) for user \'%s\'\n' % (folder_item_count,  user.name)

if __name__ == "__main__":
    main()