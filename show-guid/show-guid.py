import kopano

def main():
    kopano.parser('skpcu').parse_args()
    print '{:50} {:50} {:50}'.format('username name', 'Store GUID', 'Archive GUID')
    for user in kopano.Server().users(parse=True):
        if user.store.guid:
            store_id = user.store.guid.upper()
        else:
            store_id = None
        if user.archive_store:
            archive_id = user.archive_store.guid.upper()
        else:
            archive_id = None
        print '{:50} {:50} {:50}'.format(user.name.encode('utf8'), store_id, archive_id)


if __name__ == "__main__":
    main()
