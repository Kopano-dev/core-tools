#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4


try:
    import kopano
except ImportError:
    import zarafa as kopano
from MAPI.Util import *
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.Utils import COMMASPACE, formatdate
from time import sleep
from subprocess import call

def opt_args():
    parser = kopano.parser('skpc')
    parser.add_option("--from-user", dest="from_user", action="store", help="user to send form")
    parser.add_option("--to-user", dest="to_user", action="store", help="Receiving user")
    parser.add_option("--subject", dest="subject", action="store", help="subject")
    parser.add_option("--script", dest="script", action="store", help="subject")
    parser.add_option("--sleep", dest="sleep", action="store", help="Time to wait to check mail (in seconds)")
    parser.add_option("--remove", dest="remove", action="store_true", help="Remove sent item")
    parser.add_option("--folder", dest="folder", action="store", help="Folder name (default Inbox)")

    return parser.parse_args()

def main():
    options, args = opt_args()
    server = kopano.Server(options)
    from_user = server.user(options.from_user)
    to_user = server.user(options.to_user)

    msg = MIMEMultipart()
    msg['From'] = from_user.email
    msg['To'] = to_user.email
    msg['Date'] = formatdate(localtime=True)
    msg['Subject'] = options.subject
    msg.attach(MIMEText('Test', 'plain'))
    from_user.store.outbox.create_item(eml=msg.as_string()).send()
    if options.sleep:
        sleep(int(options.sleep))
    start_script = None
    if options.folder:
        folder = to_user.store.folder(options.folder)
    else:
        folder = to_user.inbox
    for item in folder.items():
        if item.subject == u'%s' % options.subject:
            start_script = True
            print item
            if options.remove:
                to_user.inbox.delete(item)
            break

    if start_script:
        call(options.script.split())
if __name__ == "__main__":
    main()