#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

try:
    import kopano
except ImportError:
    import zarafa as kopano
from MAPI.Util import *
import sqlite3 as lite
from pathlib import Path
from datetime import datetime
import csv

def opt_args():
    parser = kopano.parser('skpc')
    parser.add_option("--location", dest="location", action="store", help="database location")
    parser.add_option("--export-csv", dest="csv", action="store_true", help="export to csv")
    parser.add_option("--delimiter", dest="delimiter", action="store", help="use other delimiter  for csv export (default is ,)")
    parser.add_option("--ignore-system", dest="system", action="store_true", help="Ignore sessions that are created by the user SYSTEM ")

    return parser.parse_args()

def new_db(db):
    try:
        con = lite.connect(db)
        cur = con.cursor()
        cur.execute("""CREATE TABLE devices
                (date text, ipaddress text, name text, client_version text,
                 client_app text, client_app_version text, client_name text)
             """)
        return con
    except lite.Error, e:
        print "Error %s:" % e.args[0]
        sys.exit(1)

def get_sessions(options, con):
    current_date = datetime.now().strftime('%Y-%m-%d')
    session = kopano.Server(options).table(PR_EC_STATSTABLE_SESSIONS)
    for row in session.rows():
        for prop in row:
            if prop.idname == 'PR_EC_STATS_SESSION_IPADDRESS':
                ipaddress = prop.value
            if prop.idname == 'PR_EC_USERNAME':
                name = prop.value
            if prop.idname == 'PR_EC_STATS_SESSION_CLIENT_VERSION':
                client_version = prop.value
            if prop.idname == 'PR_EC_STATS_SESSION_CLIENT_APPLICATION':
                client_app = prop.value
            if prop.idname == 'PR_EC_STATS_SESSION_CLIENT_APPLICATION_VERSION':
                client_app_version = prop.value
            if prop.idname == 'PR_EC_STATS_SESSION_CLIENT_APPLICATION_MISC':
                client_name = prop.value

        con.execute('''INSERT into devices(date, ipaddress, name, client_version, client_app, client_app_version, client_name)
        SELECT '%s', '%s','%s','%s','%s','%s','%s'
        WHERE NOT EXISTS(SELECT 1 FROM devices where date = '%s', ipaddress = '%s' AND name = '%s' AND client_app = '%s'
        AND client_app_version = '%s' AND client_name = '%s')'''
                    % (current_date, ipaddress, name, client_version, client_app, client_app_version, client_name,
                       current_date, ipaddress, name, client_app, client_app_version, client_name))
        con.commit()

        #print 'ip:', ipaddress, 'name:', name, 'version:', client_version, 'app:', client_app, 'app_version:', client_app_version, 'name:', client_name


def main():
    options, args = opt_args()
    if options.location:
        db_file = '%s/sessions.db' % options.location
    else:
        db_file = 'sessions.db'
    if not Path(db_file).is_file():
        con = new_db(db_file)
    else:
        con = lite.connect(db_file)

    get_sessions(options, con)

    if options.csv:
        if options.system:
            exception = "WHERE name != 'SYSTEM'"
        else:
            exception = ''
        cur = con.cursor()
        result = cur.execute('SELECT date, ipaddress, name, client_version, client_app, client_app_version, client_name from devices %s' % exception)
        rows = result.fetchall()
        if options.delimiter:
            delimiter = options.delimiter
        else:
            delimiter = ','
        resultFile = open("sessions.csv", 'w')
        wr = csv.writer(resultFile, delimiter=delimiter)
        wr.writerow(['date', 'ipaddress', 'name', 'client_version', 'client_app', 'client_app_version', 'client_name'])

        for device in rows:
            for index, item in enumerate(device):
                device[index].replace(delimiter, '_')
            wr.writerows([device])

if __name__ == "__main__":
    main()