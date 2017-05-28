'''Try to send-email a set of recent images captured by a webcam.

Called from 'motion' service.
'''
import datetime
import pathlib
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
import argparse
import os
import glob
import smtplib
import logging as log
import time

to_ = 'robb.kc.jones@gmail.com'
from_ = 'nookie.kc.jones+hyperion@gmail.com'
smtp_address_ = 'smtp.gmail.com:587'


def get_stamp(stamp_filename):
    ''' Get file's mtime. '''
    t = os.path.getmtime(stamp_filename)
    return datetime.datetime.fromtimestamp(t)


def update_stamp(stamp_filename):
    ''' Update file's mtime. '''
    with open(stamp_filename, 'a'):
        log.debug('updating ' + stamp_filename)
        os.utime(stamp_filename, None)


def get_images(img_dir, n):
    ''' Get list of image files sorted by mtime. '''
    files = glob.glob(img_dir + '/*.jpg')
    files.sort(key=os.path.getmtime)
    return files[(-1)*n:-1]


def send_mail(image_list, secret_file):
    msg = MIMEMultipart()
    msg['Subject'] = 'Hyperion reporting visual alert'
    msg['From'] = from_
    msg['To'] = to_

    text = MIMEText("Visual alert!")
    msg.attach(text)

    found = False
    for img in get_images(image_list, 5):
        found = True
        fp = open(img, 'rb')
        image = MIMEImage(fp.read(), 'jpeg')
        fp.close()
        msg.attach(image)

    if found:
        with open(secret_file) as sec:
            pwd = sec.readline().strip()
            server = smtplib.SMTP(smtp_address_)
            server.ehlo()
            server.starttls()
            server.login(from_, pwd)

            log.info('from='+from_)
            log.info('to='+to_)
            server.sendmail(from_, to_, msg.as_string())
            log.info('Mail sent')
            server.quit()
    else:
        log.info("No files to send!")


def is_expired(stamp, now, timeout_mins):
    return stamp < now - datetime.timedelta(minutes = timeout_mins)


def try_send(stamp_filename, image_path, timeout_mins, secret_file):
    ''' Send recent image files if enough time has elapsed since the last send. '''

    d = get_stamp(stamp_filename)
    now = datetime.datetime.now()
    expired = is_expired(d, now, timeout_mins)
    log.info('last={}'.format(d.isoformat()))
    log.info('current={}'.format(now.isoformat()))
    log.info('expired={}'.format(expired))
    if (expired):
        log.debug('Wait time expired.')
        update_stamp(stamp_filename) # update the stamp file early to prevent subsequent files from triggering/seeing an old date
        time.sleep(6) # sleep for a few seconds to let some new files queue up
        send_mail(image_path, secret_file)


def parse_cli_args():
    parser = argparse.ArgumentParser(description='Hyperion motion capture/mailer')
    parser.add_argument('-i', '--image_path', default='/var/lib/motion', type=os.path.expanduser)
    parser.add_argument('-l', '--log_file', default='~/log/hyperion.log', type=os.path.expanduser)
    parser.add_argument('-p', '--secret_file', default='~/.secret', type=os.path.expanduser)
    parser.add_argument('-s', '--stamp_file', default='~/.stamp', type=os.path.expanduser)
    parser.add_argument('-t', '--timeout_mins', type=int, default=5)
    args = parser.parse_args()
    return args


def init(args):
    try:
        log_file_path = os.path.split(args.log_file)[0]
        os.mkdir(log_file_path)
        log.info(f'Created log_file path, {args.log_file}')
    except FileExistsError as e1:
        pass  # Bury

    log.basicConfig(filename=args.log_file,
                    filemode='a',
                    level=log.DEBUG,
                    format='%(asctime)s %(levelname)-8s %(name)-15s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')
    log.info(f'image path: {args.image_path}')
    log.info(f'log_file: {args.log_file}')
    log.info(f'stamp file: {args.stamp_file}')
    log.info(f'timeout_mins: {args.timeout_mins}')

    try:
        os.mkdir(args.image_path)  # defaults to 0o666
        log.info(f'Created image_path, {args.image_path}')
    except FileExistsError as e1:
        pass  # Bury

    if not os.path.exists(args.stamp_file):
        with open(args.stamp_file, 'w') as sf:
            sf.write(f'Hyperion stamp file initialized: {args.stamp_file}')


def main():
    args = parse_cli_args()
    init(args)
    try_send(args.stamp_file, args.image_path, args.timeout_mins, args.secret_file)


if __name__ == '__main__':
    main()
