import kopano
from kopano.errors import *
from MAPI.Util import  *
import sys

ARCH_ATT = ['archive:flags', 'archive:ref-item-entryid', 'archive:ref-store-entryid',
            'archive:item-entryids', 'archive:original-sourcekey', 'archive:store-entryids',
            'archive:stubbed', 'PR_ICON_INDEX']

def opt_args():
    parser = kopano.parser('skpcufmv')
    parser.add_option("--all", dest="all", action="store_true", help="Run script for all users ")
    return parser.parse_args()


def main():
    options, args = opt_args()
    if not options.users and not options.all:
        print('pleas use:'
              '{} -u <username>'
              '{} --all'.format(sys.argv[0], sys.argv[0]))
        sys.exit(1)
    server = kopano.Server(options)

    for user in server.users(options.users):
        num=0
        if not user.archive_store:
            if options.verbose:
                print('Skip {}:  has no archive store'.format(user.name))
            continue
        print('Running for {}'.format(user))

        archive_store =  user.archive_store
        store =  user.store
        for folder  in archive_store.folders():
            if options.verbose:
                print(folder)
            if folder.count == 0:
                if options.verbose:
                    print('folder does not contain item ')
                    continue
            try:
                store_folder =  store.folder(folder.path)
            except NotFoundError:
                store_folder = store.create_folder(folder.path)

            for item in folder.items():
                for aprop in ARCH_ATT:
                    if item.get_prop(aprop):
                        try:
                            item.delete(item.prop(aprop))
                        except:
                            continue

                    folder.move(item, store_folder)
                    num = num + 1

        print('Restore done for user {}, restored {} items'.format(user.name, num))
        print('Removing stubbed message\'s from primary store one moment')
        num_stubbed =0
        for folder in user.store.folders():
            for item in folder.items():
                if item.stubbed:
                    num_stubbed = num_stubbed +1
                    folder.delete(item)

        print('A total of {} stubbed items are removed'.format(num_stubbed))



if __name__ == "__main__":
    main()