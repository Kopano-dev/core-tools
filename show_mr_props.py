#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import kopano
import json
try:
    from tabulate import tabulates
except ImportError:
    def tabulate(iterable, header, tablefmt=None):
        max_len = [len(x) for x in header]
        for row in iterable:
            row = [row] if type(row) not in (list, tuple) else row
            for index, col in enumerate(row):
                if max_len[index] < len(str(col)):
                    max_len[index] = len(str(col))
        output = '-' * (sum(max_len) + 1) + '\n'
        output += '|' + ''.join([h + ' ' * (l - len(h)) + '|' for h, l in zip(header, max_len)]) + '\n'
        output += '-' * (sum(max_len) + 1) + '\n'
        for row in iterable:
            row = [row] if type(row) not in (list, tuple) else row
            output += '|' + ''.join([str(c) + ' ' * (l - len(str(c))) + '|' for c, l in zip(row, max_len)]) + '\n'
        output += '-' * (sum(max_len) + 1) + '\n'
        return output

def opt_args():
    parser = kopano.parser('skpcuf')
    return parser.parse_args()


def main():
    options, args = opt_args()
    server = kopano.Server(options)
    table_header = ["User", 'Enabled', 'decline conflict', 'decline recurring']
    table_data =[]
    for user in kopano.Server(options).users(parse=True):
        table_data.append([user.name, user.autoaccept.enabled, user.autoaccept.recurring,user.autoaccept.conflicts])

    print(tabulate(table_data, table_header, tablefmt="grid"))

if __name__ == '__main__':
    main()
