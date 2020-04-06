#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
#
import kopano

def opt_args():
    parser = kopano.parser('skpfucmUP')
    return parser.parse_args()

def main():
    options, args = opt_args()

    if not options.users :
        print('Usage:\n{} -u <username>'.format(sys.argv[0]))
        sys.exit(1)

    for user in kopano.Server(options).users():
        if not user.store:
            print('No store detected for user {}'.format(user.name))
            continue
        if not user.reminders:
            print('No reminders folder detected for user {}'.format(user.name))
            continue
        user.store.delete(user.reminders)

        print('\nDeleted reminders folder for user {}'.format(user.name))
    
    print('Reminders folder is recreated when the user logs in into WebApp')
if __name__ == "__main__":
    main()
