#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

import kopano

def opt_args():
    parser = kopano.parser('skpcufUP')
    parser.add_option("--print", dest="print_only", action="store_true", help="only print the kopano-cli command")

    return parser.parse_args()


def main():
    options, args = opt_args()
    for user in kopano.Server(options).users(parse=True):
        command = 'kopano-cli -u {} '.format(user.name)
        do_something = False
        # try:
        #     if user.autoprocess.enabled:
        #         command += '--mr-process YES '
        #     else:
        #         command += '--mr-process NO '
        # except AttributeError:
        #     pass
        try:
            if user.autoaccept.enabled:
                do_something = True
                command += '--mr-accept YES '

                if user.autoaccept.conflicts:
                    command += '--mr-accept-conflicts YES '
                else:
                    command += '--mr-ccept-conflicts NO '
                if user.autoaccept.recurring:
                    command += '--mr-accept-recurring YES '
                else:
                    command += '--mr-accept-recurring NO '

        except AttributeError:
            pass
        if do_something:
            if options.print_only:
                print(command)
            else:
                print('do it for real')

if __name__ == '__main__':
    main()
