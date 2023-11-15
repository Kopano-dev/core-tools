#!/usr/bin/env python3

import kopano
from MAPI.Tags import ATTACH_BY_VALUE, PR_ATTACH_METHOD, PR_ATTACHMENT_HIDDEN
import binascii
from kopano.utils import _save

def opt_args():
    parser = kopano.parser('skpcfUFPu')
    return parser.parse_args()

def main():
    options, args = opt_args()

    for user in kopano.Server(options).users():
        print("running for user {}".format(user.name))

        for folder in user.folders():
            print("checking folder {}".format(folder.name))
            for item in folder.items():
                if item.has_attachments:
                    for at in item.attachments():
                        if at.prop(PR_ATTACH_METHOD).value == ATTACH_BY_VALUE and at.prop(PR_ATTACHMENT_HIDDEN).value == True:
                            print('fixing attachemnt {} for item {}'.format(at.name, item.name))
                            at.create_prop(PR_ATTACHMENT_HIDDEN, False) 
                            _save(item.mapiobj)


                            
if __name__ == "__main__":
    main()