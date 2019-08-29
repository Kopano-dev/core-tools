#!/usr/bin/env python3
import kopano
import hashlib
from MAPI.Tags import PR_SUBJECT, PR_START_DATE, PR_END_DATE, PR_HTML, PR_BODY

def opt_args():
    parser = kopano.parser('skpcUPm')
    parser.add_option('--user', dest='user', action='store', help='username')
    parser.add_option('--folder', dest='folder', action='store', help='foldername')
    return parser.parse_args()

def main():
    options, args = opt_args()
    user = kopano.Server(options).user(options.user)
    if not options.folder:
        folder = user.store.calendar
    else:
        folder = user.store.folder(options.folder)
    
    read_items = []
    num = 0
    for item in folder.items():
        md5 = hashlib.md5(item.prop(PR_SUBJECT).value)
        if item.get_prop(PR_START_DATE):
            md5.update(item.prop(PR_START_DATE).value.strftime(("%m/%d/%Y, %H:%M:%S")).encode())
        if item.get_prop(PR_END_DATE):
            md5.update(item.prop(PR_END_DATE).value.strftime(("%m/%d/%Y, %H:%M:%S")).encode())
        if item.get_prop(PR_BODY):    
            md5.update(item.prop(PR_BODY).value)
        if item.get_prop(PR_HTML):    
            md5.update(item.prop(PR_HTML).value)
        md5 = md5.hexdigest()
        if md5 in read_items: 
            num += 1
            folder.delete(item)
        else:
            read_items.append(md5)

    print('deleted {} items in folder {}'.format(num, folder.name))

if __name__ == '__main__':
    main()
