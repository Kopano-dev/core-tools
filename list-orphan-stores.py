#!/usr/bin/python3

'''
List orphan private stores on two conditions:

1. User is moved to a different homeserver, but his store is still hooked.
2. User is deleted.

Determining guessed user if the user has been removed by looking at the following properties:
- Outbox folder: PR_SENDER_EMAIL_ADDRESS_W property
- Inbox folder: PR_RECEIVED_BY_EMAIL_ADDRESS_W property

Calling server.stores (GetMailboxTable) and looking up orphans does initiate LDAP queries to look up usernames

Possible python-kopano performance improvements:
- server.stores() has a SetColumns on PR_DISPLAY_NAME_W which is never used afterwards
- store.orphan opens stores twice by calling self.user.store and self.user.store.guid
- store.type_ in python-kopano is inefficient
'''
from datetime import timezone

import pytz

import json

import kopano

from MAPI.Tags import PR_RECEIVED_BY_EMAIL_ADDRESS_W, PR_SENDER_EMAIL_ADDRESS_W


# Amount of items to check the username of in inbox and sent items folder
CHECK_ITEMS = 25


def guess_store_owner_by_folder(folder, proptag):
    usernames = []

    for item in folder.items(page_limit=CHECK_ITEMS):
        try:
            usernames.append(item.prop(proptag).value)
        except kopano.errors.NotFoundError:
            continue

    # Return unique usernames
    return list(set(usernames))


def guess_store_owner(store):
    '''
    Retrieve an unique set of usernames based on the
    PR_RECEIVED_BY_EMAIL_ADDRESS_W property for items in the inbox
    folder and the PR_SENDER_EMAIL_ADDRESS_W property for items in the outbox
    folder.
    '''

    inbox = store.inbox
    outbox = store.outbox

    inbox_usernames = []
    outbox_usernames = []

    if inbox:
        inbox_usernames = guess_store_owner_by_folder(inbox, PR_RECEIVED_BY_EMAIL_ADDRESS_W)

    if outbox:
        outbox_usernames = guess_store_owner_by_folder(outbox, PR_SENDER_EMAIL_ADDRESS_W)

    return list(set(inbox_usernames + outbox_usernames))


def main():
    stores = []
    # parse_args=False does not seem to play well with /etc/kopano/admin.cfg..
    #server = kopano.Server(parse_args=False)
    server = kopano.Server()

    for store in server.stores():
        if not store.orphan:
            continue

        data = {
            'guid': store.guid,
            'size': store.size,
            'empty': False,
        }

        if store.last_logon:
            data['last_logon'] = store.last_logon.astimezone(pytz.UTC).isoformat(timespec='minutes')
        if store.last_logoff:
            data['last_logoff'] = store.last_logoff.astimezone(pytz.UTC).isoformat(timespec='minutes')

        user = store.user

        if sum(folder.count for folder in store.folders()) == 0:
            data['empty'] = True

        if user:
            data['owner'] = {
                'username': user.name,
                'email': user.email,
                'deleted': False,
            }
            # For some reason store.type_ is null when a user is attached, so set it to private
            data['type'] = 'private'
        else:  # Removed user cannot be resolved
            if store.public:
                data['type'] = 'public'
            else:
                data['type'] = 'private'

                guessed_usernames = guess_store_owner(store)
                data['owner'] = {
                        'deleted': True,
                        'guessed_usernames': guessed_usernames,
                }

        stores.append(data)

    print(json.dumps(stores, indent=4))


if __name__ == "__main__":
    main()
