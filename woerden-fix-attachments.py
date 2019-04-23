import kopano
from MAPI.Tags import *

def opt_args():
    parser = kopano.parser('skpcUPu')
    parser.add_option("--zarafa-server", dest="zarafa_url", action="store", help="zarafa url ")
    parser.add_option("--zarafa-admin-user", dest="admin_user", action="store", help="zarafa admin user ")
    parser.add_option("--zarafa-admin-pass", dest="admin_pass", action="store", help="zarafa admin password")

    return parser.parse_args()


def main():
    options, args = opt_args()
    kopano_server = kopano.Server(options)
    zarafa_server = kopano.Server(server_socket=options.zarafa_url, auth_user=options.admin_user, auth_pass=options.admin_pass)
    for kopano_user in kopano_server.users(parse=True):
        print(kopano_user.name)
        zarafa_user = zarafa_server.user(kopano_user.name)
        for kopano_folder in kopano_user.folders():
            try:
                zarafa_folder = zarafa_user.store.folder(kopano_folder.path)
            except kopano.errors.NotFoundError:
                continue

            for kopano_item in kopano_folder.items():
                if kopano_item.has_attachments and kopano_item.get_prop(PR_EC_BACKUP_SOURCE_KEY):
                    zarafa_item = None
                    for attach in kopano_item.attachments():
                        try:
                            if attach.data:
                                continue
                        except:
                            pass

                        # Get same item on the Zarafa server
                        if not zarafa_item:
                            # We have no idea what the entryid is so search for items and then loop over the output
                            zarafa_items = list(zarafa_folder.search(kopano_item.subject))
                            for tmp in zarafa_items:
                                if tmp.prop(PR_SOURCE_KEY).value == kopano_item.prop(PR_EC_BACKUP_SOURCE_KEY).value:
                                    zarafa_item = tmp
                                    break
                        if not zarafa_item:
                            print('item on zarafa server is not available entryid {}'.format(kopano_item.entryid))
                            continue

                        try:  # TODO check why this is triggered
                            zar_attach = list(zarafa_item.attachments())[attach.number]
                        except IndexError:
                            continue

                        # At the moment we only support PR_ATTACH_DATA_BIN
                        # TODO check if other attachment should be restored as well
                        if zar_attach.get_prop(PR_ATTACH_DATA_BIN):
                            stream = attach.OpenProperty(PR_ATTACH_DATA_BIN, IID_IStream,
                                                         STGM_WRITE | STGM_TRANSACTED, MAPI_MODIFY | MAPI_CREATE)
                            stream.Write(zar_attach.data)
                            stream.Commit(0)
                            attach.mapiobj.SaveChanges(KEEP_OPEN_READONLY)
                            kopano_item.mapiobj.SaveChanges(KEEP_OPEN_READWRITE)

                            print('Saved attachment data {}'.format(kopano_item.entryid,
                                                                    attach.entryid))
                        else:
                            print('Attachment is not PR_ATTACH_DATA_BIN {} {}'.format(kopano_item.entryid,
                                                                                      attach.entryid))


if __name__ == "__main__":
    main()
