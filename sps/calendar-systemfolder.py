import kopano
from MAPI.Tags import PR_IPM_APPOINTMENT_ENTRYID, PR_ENTRYID
import binascii

def opt_args():
    parser = kopano.parser('skpcUP')
    parser.add_option("--user", dest="user", action="store", help="username")
    parser.add_option("--folder", dest="folder", action="store", help="foldername")

    return parser.parse_args()


def main():
    options, args = opt_args()
    user = kopano.Server().user(options.user)
    print(user)
    folder = user.store.folder(options.folder)
    if folder.container_class != 'IPF.Appointment':
        print('folder {} is not an calendar folder'.format(folder.name))
    print(folder.entryid, binascii.unhexlify(folder.entryid.encode('utf-8')))
    user.store.root.create_prop(PR_IPM_APPOINTMENT_ENTRYID, binascii.unhexlify(folder.entryid.encode('utf-8')))

    print('folder {} is now the default calendar folder'.format(folder.name))

if __name__ == "__main__":
    main()
