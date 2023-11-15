import kopano
from MAPI.Tags import *
from kopano.errors import *
from datetime import datetime
import binascii
def opt_args():
    parser = kopano.parser('skpcufUP')
    parser.add_option("--all", dest="all", action="store_true", help="Run script for all users")
    parser.add_option("--until", dest="until", action="store", help="Only search for mails younger then yyyy-mm-dd")
    return parser.parse_args()

def main():
    options, args = opt_args()
    server = kopano.Server(options)
    if not options.users and not options.all:
        print('please use\n{} --user <username>\nor\n{} --all'.format(sys.argv[0], sys.argv[0]))
        sys.exit(1)

    for user in server.users():
        print(user.name)
        if not user.store:
            continue
        blacklist = [user.calendar.name, user.notes.name, user.tasks.name, user.contacts.name]
        for folder in user.store.folders():
            if folder.name not in blacklist:
                for item in folder.items():
                    if options.until:
                        submit_time = item.prop(PR_LAST_MODIFICATION_TIME).value
                        check = datetime.strptime('{} 00:00:00'.format(options.until), '%Y-%m-%d 00:00:00')
                        if submit_time < check:
                            break
                    if item.message_class == u'IPM.Schedule.Meeting.Request':
                        try:
                            print('changing item {}'.format(item.subject))
                        except UnicodeEncodeError:
                            print('changing item unknown')
                        if item.get_prop(PR_SENT_REPRESENTING_ADDRTYPE_W) and item.prop(PR_SENT_REPRESENTING_ADDRTYPE_W).value == 'SMTP':
                            try:
                                username = server.user(email=item.prop(PR_SENT_REPRESENTING_SEARCH_KEY).value.replace('SMTP:',''))
                                item.create_prop(PR_SENT_REPRESENTING_SEARCH_KEY,'ZARAFA:{}'.format(username.email))
                                item.create_prop(PR_SENT_REPRESENTING_ADDRTYPE_W, u'ZARAFA')
                                item.create_prop(PR_SENT_REPRESENTING_EMAIL_ADDRESS_W, username.name)
                                item.create_prop(PR_SENT_REPRESENTING_ENTRYID, binascii.unhexlify(username.entryid))
                            except NotFoundError:
                                pass

                        if item.get_prop(PR_SENDER_ADDRTYPE_W) and item.prop(PR_SENDER_ADDRTYPE_W).value == 'SMTP':
                            try:
                                username = server.user(
                                    email=item.prop(PR_SENDER_SEARCH_KEY).value.replace('SMTP:', ''))
                                item.create_prop(PR_SENDER_SEARCH_KEY,'ZARAFA:{}'.format(username.email))
                                item.create_prop(PR_SENDER_ADDRTYPE_W, u'ZARAFA')
                                item.create_prop(PR_SENDER_EMAIL_ADDRESS_W, username.name)
                                item.create_prop(PR_SENDER_ENTRYID, binascii.unhexlify(username.entryid))
                            except NotFoundError:
                                pass
                        if item.get_prop(PR_RECEIVED_BY_ADDRTYPE_W) and item.prop(PR_RECEIVED_BY_ADDRTYPE_W).value == 'SMTP':
                            try:
                                username = server.user(
                                    email=item.prop(PR_RECEIVED_BY_SEARCH_KEY).value.replace('SMTP:', ''))
                                item.create_prop(PR_RECEIVED_BY_SEARCH_KEY,'ZARAFA:{}'.format(username.email))
                                item.create_prop(PR_RECEIVED_BY_ADDRTYPE_W, u'ZARAFA')
                                item.create_prop(PR_RECEIVED_BY_EMAIL_ADDRESS_W, username.name)
                                item.create_prop(PR_RECEIVED_BY_ENTRYID, binascii.unhexlify(username.entryid))

                            except NotFoundError:
                                pass
                        if item.get_prop(PR_RCVD_REPRESENTING_ADDRTYPE_W) and item.prop(PR_RCVD_REPRESENTING_ADDRTYPE_W).value == 'SMTP':
                            try:
                                username = server.user(
                                    email=item.prop(PR_RCVD_REPRESENTING_SEARCH_KEY).value.replace('SMTP:', ''))
                                item.create_prop(PR_RCVD_REPRESENTING_SEARCH_KEY,'ZARAFA:{}'.format(username.email))
                                item.create_prop(PR_RCVD_REPRESENTING_ADDRTYPE_W, u'ZARAFA')
                                item.create_prop(PR_RCVD_REPRESENTING_EMAIL_ADDRESS_W, username.name)
                                item.create_prop(PR_RCVD_REPRESENTING_ENTRYID, binascii.unhexlify(username.entryid))

                            except NotFoundError:
                                pass


if __name__ == "__main__":
    main()
