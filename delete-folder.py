#!/usr/bin/env python
try:
    import kopano
except ImportError:
    import zarafa as kopano

def opt_args():
    parser = kopano.parser('skpcUPm')
    parser.add_option('--user', dest='user', action='store', help='username')
    parser.add_option('--folder', dest='folder', action='store', help='foldername')

    return parser.parse_args()


def main():
    options, args = opt_args()
    user = kopano.Server(options).user(options.user)
    folder = user.store.folder(options.folder)
    if options.modify:
        print('Removing folder {} and all the subfolder'.format(folder.name))
        folder.delete(folder)
    else:
        print(folder.name)
        print('the following sub folders will be deleted:')
        for sub in folder.folders():
            print sub.name

if __name__ == '__main__':
    main()
