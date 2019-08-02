#!/usr/bin/python

import argparse

import ldap
import ldap.modlist as modlist


URI = 'ldap://localhost:389'
ADMIN = 'cn=admin,dc=farmer,dc=lan'
PASSWORD = 'kopano'
GROUP = 'cn={},ou=groups,dc=farmer,dc=lan'
USER = 'uid=user1,ou=users,dc=farmer,dc=lan'
BASEDN = 'dc=farmer,dc=lan'
TOTAL = 20


def main():
    parser = argparse.ArgumentParser(description='create groups for given user')
    parser.add_argument('--uri', default=URI, help='the LDAP URI (default: {})'.format(URI))
    parser.add_argument('--admin', default=ADMIN, help='the LDAP Admin user (default: {})'.format(ADMIN))
    parser.add_argument('--password', default=PASSWORD, help='the LDAP Admin password (default: {})'.format(PASSWORD))
    parser.add_argument('--basedn', default=BASEDN, help='the LDAP basedn (default: {})'.format(BASEDN))
    parser.add_argument('--user', default=USER, help='the LDAP User (DN) to create groups for (default: {})'.format(USER))
    parser.add_argument('--total-groups', default=TOTAL, help='the amount of groups to create (default: {})'.format(TOTAL), type=int)

    args = parser.parse_args()

    conn = ldap.initialize(URI)
    conn.simple_bind(ADMIN, PASSWORD)

    result = conn.search(args.basedn, ldap.SCOPE_SUBTREE, '(uidNumber=*)', ['uidNumber'])
    lastuid = 0

    while True:
        result_type, result_data = conn.result(result, 0)
        if result_data == []:
            break
        else:
            if result_type != ldap.RES_SEARCH_ENTRY:
                continue
            uidnumber = int((result_data[0][1]['uidNumber'])[0])
            if uidnumber > lastuid:
                lastuid = uidnumber

    if lastuid == 0:
        lastuid = 2000


    groups = ['group{}'.format(i) for i in range(0, args.total_groups)]
    for group in groups:
        lastuid += 1
        attrs = {}
        attrs['objectclass'] = [b'posixGroup', b'top', b'kopano-group']
        attrs['memberUid'] = [b'user1']
        attrs['mail'] = '{}@kopano.com'.format(group).encode()
        attrs['description'] = 'test {} group for user1'.format(group).encode()
        attrs['cn'] = group.encode()
        attrs['gidNumber'] = str(lastuid).encode()

        ldif = modlist.addModlist(attrs)
        dn = GROUP.format(group)

        try:
            conn.add_s(dn, ldif)
        except ldap.LDAPError as e:
            print(e)


    conn.unbind()


if __name__ == "__main__":
    main()
