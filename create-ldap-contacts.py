#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
#
import sys
import json
import os
import argparse
try:
    import ldap
    import ldap.modlist as modlist
except ImportError:
    print 'please install python-ldap'
    sys.exit(1)
try:
    from faker import Factory
except ImportError:
    print 'please install Faker (pip install Faker)'
    sys.exit(1)

homedir = os.path.dirname(os.path.realpath(__file__))

def opt_args():
    parser = argparse.ArgumentParser(description='create contacts')
    parser.add_argument('--server', type=str, help='server')
    parser.add_argument('--basedn', type=str, help='basedn')
    parser.add_argument('--user', type=str, help='user (cn=admin,dc=farmer,dc=lan)')
    parser.add_argument('--password', type=str, help='password')
    parser.add_argument('--newou', type=str, help='create new organisation unit')
    parser.add_argument('--totalcontacts', type=int, help='number of contacts')

    args = parser.parse_args()

    return args


def ldapconnect(option):

    l = ldap.initialize('ldap://%s:389'  % option.server)
    binddn = option.user
    pw = option.password
    l.protocol_version = ldap.VERSION3
    l.simple_bind_s(binddn, pw)

    return l

def searchldap(option, basedn, searchFilter, searchAttribute):
    l = ldapconnect(option)
    searchScope = ldap.SCOPE_SUBTREE

    try:
        ldap_result_id = l.search(basedn, searchScope, searchFilter, searchAttribute)
        result_set = []
        while 1:
            result_type, result_data = l.result(ldap_result_id, 0)
            if (result_data == []):
                break
            else:
                if result_type == ldap.RES_SEARCH_ENTRY:
                    result_set.append(result_data[0][1])
    except ldap.LDAPError, e:
        print e.message['desc']
    l.unbind_s()
    return result_set


def add_entry(config, json_data):
    l = ldapconnect(config)

    data = json.loads(json_data)
    attrs = {}
    for line in data:
        if str(line) == 'dn':
            dn = str(data[line])
        else:
            if type(data[line]) is list:
                newlist = []
                for datalist in data[line]:
                    newlist.append(str(datalist))
                attrs[line] = newlist
            else:
                attrs[line] = str(data[line])

    ldif = modlist.addModlist(attrs)
    try:
        l.add_s(dn, ldif)
    except ldap.LDAPError, e:
        print '%s %s' % (dn, e.message['desc'])

def delete_user(basedn, uid):

    l = ldapconnect()
    deletedn = 'uid=%s,%s' %(uid, basedn)
    print deletedn
    try:
        l.delete_s(deletedn)
    except ldap.LDAPError, e:
        print e.message['desc']


def main():
    option = opt_args()

    if not option.server or not option.user or not option.password:
        print 'pleas use %s --server --user --password' % sys.argv[0]
        sys.exit(1)

    if option.server == '192.168.10.41':
        print 'Please use an other ldap server.'
        sys.exit(1)

    if option.newou:
        orgunit = option.newou
    else:
        orgunit = 'contacts'
    #check if ou exist
    result = searchldap(option, option.basedn, "(ou=%s)" % orgunit, None)
    if not result:
        print 'create'
        ou = {}
        ou['dn'] = 'ou=%s,%s' % (orgunit, option.basedn)
        ou['objectClass'] = ['top', 'organizationalUnit']
        ou['ou'] = orgunit
        json_data = json.dumps(ou)
        add_entry(option, json_data)

    for number in range(option.totalcontacts):
        result = searchldap(option, 'ou=%s,%s' % (orgunit, option.basedn), "(uidNumber=*)", None)

        try:
            lastuid = result[-1]['uidNumber'][0]
        except IndexError as e:
            if e.message == 'list index out of range':
                lastuid = 1000

        fake = Factory.create('en_US')
        firstname = fake.first_name()
        lastname = fake.last_name()

        uid = '%s %s' % (firstname, lastname)
        user = {}
        user['dn'] = 'uid=%s,ou=%s,%s' % (uid, orgunit, option.basedn)
        user['objectClass'] = ['top', 'kopano-contact', 'inetOrgPerson']
        user['cn'] = '%s %s' % (firstname, lastname)
        user['uid'] = uid
        user['mail'] = '%s@%s' % (firstname, fake.domain_name())
        user['uidNumber'] = str(int(lastuid) + 1)
        user['givenName'] = firstname
        user['sn'] = lastname

        json_data = json.dumps(user)

        print 'Add contact %s' % uid
        add_entry(option, json_data)

if __name__ == "__main__":
    main()