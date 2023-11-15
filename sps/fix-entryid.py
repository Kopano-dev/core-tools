#!/usr/bin/env python

import kopano
import sys
import binascii

def opt_args():
    parser = kopano.parser('skpcufm')
    parser.add_option("--all", dest="ALL", action="store_true", help="Run script for all users")
    return parser.parse_args()



def getprop(item, myprop):
    try:
        return item.prop(myprop).value
    except:
        return None

def main():
    options, args = opt_args()
    if not options.ALL and not options.users:
        sys.exit('Please use:\n %s -u <username>  or \n %s -all to run this script' % (sys.argv[0], sys.argv[0]))
    allusers=[]
    for user in kopano.Server(options).users(parse =False):
        allusers.append([user.name, user.userid])

    ignore = ['Deleted Items', 'Suggested Contacts', 'Quick Step Settings', 'Conversation Action Settings', 'RSS Feeds', 'Tasks', 'Notes', 'Journal', 'Drafts', 'Contacts']
    for user in kopano.Server(options).users(parse=True, remote=True):
        print user.name
        for folder in user.folders():
            if not any(ex in folder.name for ex in ignore):
                print folder
                for item in folder.items():
                    subject = getprop(item, 0x0037001E)
                    sendertype = getprop(item, 0x0C1E001E)
                    if str(sendertype) == 'ZARAFA':
                        try:
                            receivedID = binascii.hexlify(getprop(item,0x003F0102))  #PR_RECEIVED_BY_ENTRYID
                        except:
                            receivedID = None
                        receivedName = getprop(item,0x0076001e) #PR_RECEIVED_EMAIL_ADDRESS
                        try:
                            senderiD= binascii.hexlify(getprop(item,0x0C190102))  #PR_SENDER_ENTRYID
                        except:
                            senderiD = None
                        senderName = getprop(item,0x0C1F001E)  #PR_SENDER_EMAIL_ADDRESS
                        try:
                            sentID = binascii.hexlify(getprop(item,0x00410102))  #PR_SENT_REPRESENTING_ENTRYID
                        except:
                            sentID = None
                        sentName = getprop(item,0x0065001E) #PR_SENT_EMAIL_ADDRESS

                        if receivedName == user.name and str(receivedID).upper() != str(user.userid):
                            try:
                                item.prop(0x003F0102).set_value(binascii.unhexlify(user.userid))
                                print '[SUCCESS] Fixing RECEIVED_BY_ENTRYID for %s ' % subject
                            except:
                                print '[ERROR] Changing RECEIVED_BY_ENTRYID for %s ' % subject

                        for check in allusers:
                                if senderName == str(check[0]):
                                    if str(senderiD).upper() != check[1]:
                                        try:
                                            item.prop(0x0C190102).set_value(binascii.unhexlify(check[1]))
                                            print '[SUCCESS] Fixing  PR_SENDER_ENTRYID for %s ' % subject
                                        except:
                                            print '[ERROR] Changing PR_SENDER_ENTRYID for %s ' % subject
                                if sentName == str(check[0]):
                                    if str(sentID).upper() != check[1]:
                                        try:
                                            item.prop(0x00410102).set_value(binascii.unhexlify(check[1]))
                                            print '[SUCCESS] Fixing PR_SENT_REPRESENTING_ENTRYID for %s ' % subject
                                        except:
                                            print '[ERROR] Changing PR_SENT_REPRESENTING_ENTRYID for  %s ' % subject

if __name__ == "__main__":
    main()