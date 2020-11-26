#!/usr/bin/env python3
import argparse
import json
import logging
import os

import requests
from jinja2 import Environment, FileSystemLoader

logger = logging.getLogger(__name__)


class InvalidConfigException(Exception):
    pass


def parse_arguments():
    parser = argparse.ArgumentParser()
    # base arguments
    parser.add_argument('-v', '--verbose', dest='loglevel', action='store_const', const=logging.INFO,
                        help='Print more output')
    parser.add_argument('-d', '--debug', dest='loglevel', action='store_const', const=logging.DEBUG,
                        default=logging.WARNING, help='Print even more output')
    parser.add_argument('-c', '--config', help='Configuration file location', required=True)
    parser.add_argument('-o', '--logfile', help='Logging file location')
    subparsers = parser.add_subparsers(title='commands', dest='command', help='Nagios notification type')

    # host notifications
    host_parser = subparsers.add_parser('host')
    host_parser.add_argument('--notification-type', help='Nagios $NOTIFICATIONTYPE$', required=True)
    host_parser.add_argument('--service-desc', help='Nagios $SERVICEDESC$', required=True)
    host_parser.add_argument('--host-name', help='Nagios $HOSTNAME$', required=True)
    host_parser.add_argument('--host-state', help='Nagios $HOSTSTATE$', required=True)
    host_parser.add_argument('--host-address', help='Nagios $HOSTADDRESS$', required=True)
    host_parser.add_argument('--host-output', help='Nagios $HOSTOUTPUT$', required=True)
    host_parser.add_argument('--long-date-time', help='Nagios $LONGDATETIME$', required=True)

    # service notifications
    service_parser = subparsers.add_parser('service')
    service_parser.add_argument('--notification-type', help='Nagios $NOTIFICATIONTYPE$', required=True)
    service_parser.add_argument('--service-desc', help='Nagios $SERVICEDESC$', required=True)
    service_parser.add_argument('--host-alias', help='Nagios $HOSTALIAS$', required=True)
    service_parser.add_argument('--host-address', help='Nagios $HOSTADDRESS$', required=True)
    service_parser.add_argument('--service-state', help='Nagios $SERVICESTATE$', required=True)
    service_parser.add_argument('--long-date-time', help='Nagios $LONGDATETIME$', required=True)
    service_parser.add_argument('--service-output', help='Nagios $SERVICEOUTPUT$', required=True)

    args = parser.parse_args()
    return args


def read_config(filename=None):
    if filename and os.path.isfile(filename):
        with open(filename, 'r') as fd:
            return json.load(fd)
    else:
        return {}


def validate_config(config):
    if config is None:
        raise InvalidConfigException('Config is not a dict')
    for key in ['chat_id', 'auth_key']:
        if key not in config:
            raise InvalidConfigException(f'Missing "{key}" key in config')


def setup_logging(args):
    log_format = '%(asctime)s %(levelname)s: %(message)s' if args.logfile else '%(levelname)s: %(message)s'
    logging.basicConfig(format=log_format, level=args.loglevel, filename=args.logfile)


def markdown_escape(text):
    for special_char in ['\\', '`', '*', '_', '{', '}', '[', ']', '(', ')', '#', '+', '-', '.', '!']:
        text = text.replace(special_char, fr'\{special_char}')
    return text


def generate_host_payload(chat_id, args):
    payload = {'chat_id': chat_id, 'parse_mode': 'MarkdownV2'}
    absolute_path = os.path.split(os.path.abspath(__file__))[0]
    loader = FileSystemLoader(os.path.join(absolute_path, 'templates'))
    env = Environment(loader=loader)
    template = env.get_template('host.md.j2')
    text = template.render(notification_type=markdown_escape(args.notification_type),
                           host_name=markdown_escape(args.host_name), host_state=markdown_escape(args.host_state),
                           host_address=markdown_escape(args.host_address),
                           host_output=markdown_escape(args.host_output),
                           long_date_time=markdown_escape(args.long_date_time))
    payload['text'] = text
    return payload


def generate_service_payload(chat_id, args):
    payload = {'chat_id': chat_id, 'parse_mode': 'MarkdownV2'}
    absolute_path = os.path.split(os.path.abspath(__file__))[0]
    loader = FileSystemLoader(os.path.join(absolute_path, 'templates'))
    env = Environment(loader=loader)
    template = env.get_template('service.md.j2')
    text = template.render(notification_type=markdown_escape(args.notification_type),
                           service_desc=markdown_escape(args.service_desc), host_alias=markdown_escape(args.host_alias),
                           host_address=markdown_escape(args.host_address),
                           service_state=markdown_escape(args.service_state),
                           long_date_time=markdown_escape(args.long_date_time),
                           service_output=markdown_escape(args.service_output))
    payload['text'] = text
    return payload


def send_message(auth_key, payload):
    r = requests.post(f'https://api.telegram.org/bot{auth_key}/sendMessage', json=payload)
    if r.status_code != requests.codes.ok:
        description = r.json().get('description')
        logger.error(f'{r.status_code}: {description}')
        logger.debug(payload)


def main():
    args = parse_arguments()
    setup_logging(args)
    logger.info(f'reading configuration file {args.config}')
    config = read_config(args.config)
    logger.info('validating configuration')
    validate_config(config)

    logger.info('generating payload')
    if args.command == 'host':
        payload = generate_host_payload(chat_id=config['chat_id'], args=args)
    elif args.command == 'service':
        payload = generate_service_payload(chat_id=config['chat_id'], args=args)
    else:
        raise NotImplementedError(f'Command {args.command} not supported')

    logger.info('sending message to telegram api')
    send_message(auth_key=config['auth_key'], payload=payload)


if __name__ == '__main__':
    main()
