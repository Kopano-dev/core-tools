import kopano
from MAPI.Tags import *


def opt_args():
    parser = kopano.parser('skpcufUP')
    return parser.parse_args()


def main():
    options, args = opt_args()
    server = kopano.Server(options)
    if not options.users:
        print('{} -u username'.format(sys.argv[0]))
    if not options.folders:
        options.folders = ['Calendar']
    for user in server.users():
        for folder in user.folders():
            for item in folder.items():
                # start date
                if not item.get_prop(0x81b60040):
                    item.create_prop(0x81b60040, item.prop(0x800d0040).value)
                # end date
                if not item.get_prop(0x81b70040):
                    item.create_prop(0x81b70040, item.prop(0x800e0040).value)

                # duration
                if not item.get_prop(0x80130003):
                    diff = item.prop(0x800e0040).value - item.prop(0x800d0040).value
                    item.create_prop(0x80130003, diff.seconds / 60)


if __name__ == "__main__":
    main()
