contact2csv
======

contact2csv can export and import contacts to/from  a csv file.


Features
========


* Export contacts to csv
* Import contacts from csv
* Use a custom delimiter (default is ,)
* Purge the contacts folder before the import



Dependencies
============

contact2csv depends on a few Python libraries:

* python-kopano
* python-mapi


Optional

* [python-progressbar](https://github.com/niltonvolpato/python-progressbar)

Usage
=====


Export
=====

    python contact2csv.py --user <username> --export --delimiter "<delimiter>"*

Export from public store
========================

    python contact2csv.py --public --folder foldername --export --delimiter "<delimiter>"*

Import
======

    python contact2csv.py --user <username> --import <csv file>  --delimiter "<delimiter>"*  --purge**


With progessbar
===============

    python contact2csv.py --user <username> --export --delimiter "<delimiter>"*
    python contact2csv.py --user <username> --import <csv file>  --progressbar --delimiter "<delimiter>"*  --purge**



\*  is optional (default delimiter is ,)

\*\* is optional(will remove all contact before starting the import)


Notice
======

PR_WEDDING_ANNIVERSARY and PR_BIRTHDAY need to be converted to Epoch timestamp.
