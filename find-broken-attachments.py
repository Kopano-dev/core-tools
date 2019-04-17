import kopano
from MAPI.Tags import PR_ATTACH_METHOD, PR_ATTACH_MIME_TAG_W, PR_ATTACHMENT_HIDDEN
import csv

def opt_args():
    parser = kopano.parser('skpcUP')
    return parser.parse_args()


def main():
    csv_file = open("missing_attachments.csv", 'w')
    wr = csv.writer(csv_file)
    wr.writerow(['userid', 'folderid', 'attachment_id', 'attachment_name', 'attachment_type',
                 'attachment_method', 'attachment_hidden'])
    options, args = opt_args()
    for user in kopano.Server(options).users():
        for folder in user.store.folders():
            for item in folder.items():
                if item.has_attachments:
                    for attach in item.attachments():
                        try:
                            if attach.data:
                                continue
                        except:
                            pass

                        mime_tag =''
                        attach_method= ''
                        attach_hidden =''
                        if attach.get_prop(PR_ATTACH_MIME_TAG_W):
                            mime_tag =  attach.prop(PR_ATTACH_MIME_TAG_W).value
                        if attach.get_prop(PR_ATTACH_METHOD):
                            attach_method = attach.prop(PR_ATTACH_METHOD).value
                        if attach.get_prop(PR_ATTACHMENT_HIDDEN):
                            attach_hidden = attach.prop(PR_ATTACHMENT_HIDDEN).value
                        wr.writerow([user.userid, folder.entryid, attach.entryid, attach.name,
                                     mime_tag, attach_method, attach_hidden])

    csv_file.close()


if __name__ == "__main__":
    main()
