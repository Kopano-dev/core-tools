#!/usr/bin/python3

import argparse

from concurrent.futures import ThreadPoolExecutor
from multiprocessing import cpu_count
from email.message import EmailMessage
from imghdr import what
from smtplib import LMTP

HOST = 'localhost'
PORT = 2003
TO = 'user1@domain.com'
EMAILS = 100


def sendmail(msg, host, port):
    with LMTP(host, port) as server:
        server.send_message(msg)


def main():
    parser = argparse.ArgumentParser(description='kopano-dagent stress test tool')
    parser.add_argument('--processes', default=cpu_count() * 2, help='number of parallel processes (default: {})'.format(cpu_count()*2))
    parser.add_argument('--host', default=HOST, help='the dagent host (default: {})'.format(HOST))
    parser.add_argument('--port', default=PORT, help='the dagent port (default: {})'.format(PORT), type=int)
    parser.add_argument('--emails', default=EMAILS, help='the number of emails to deliver (default: {})'.format(EMAILS), type=int)
    parser.add_argument('--attachment', help='add an (image) attachment to the delivered email (default: None)', type=argparse.FileType('rb'))
    parser.add_argument('--to', default=TO, help='the receiver of the emails (default: {})'.format(TO))

    args = parser.parse_args()

    msg = EmailMessage()
    msg['From'] = args.to
    msg['To'] = args.to
    msg['Subject'] = 'dagent stress test email email'

    if args.attachment:
        msg.preamble = 'Stress test body!'
        img_data = args.attachment.read()
        msg.add_attachment(img_data, maintype='image', subtype=what(None, img_data))
    else:
        msg.set_content('Stress test body!')


    with ThreadPoolExecutor(max_workers=args.processes) as executor:
        for _ in range(0, args.emails):
            executor.submit(sendmail(msg, args.host, args.port))


if __name__ == "__main__":
    main()
