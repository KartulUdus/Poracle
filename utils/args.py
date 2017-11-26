#!/usr/bin/python
# -*- coding: utf-8 -*-

import configargparse
import os
import sys
from . import config



def args(root_path):
    config['ROOT_PATH'] = root_path
    config_files = [get_path('../config/config.ini')] if '-cf' not in sys.argv and '--config' not in sys.argv else []
    # Webserver args
    parser = configargparse.ArgParser(description='Poracle', default_config_files=config_files)
    parser.add_argument('-cf', '--config', is_config_file=True, help='Configuration file')
    parser.add_argument('-d', '--debug', help='Debug Mode', action='store_true', default=False)
    parser.add_argument('-H', '--host', help='Set web server listening host', default='127.0.0.1')
    parser.add_argument('-P', '--port', type=int, help='Web server port', default=3030)
    # Database args
    parser.add_argument('-DH', '--dbhost', help='mysql host')
    parser.add_argument('-u', '--user', help='mysql user')
    parser.add_argument('-pw', '--password', help='database password')
    parser.add_argument('-db', '--database', help='database name')
    parser.add_argument('-dbP', '--dbport', help='mysql port', default='3306')


    args = parser.parse_args()

    config['HOST'] = args.host
    config['PORT'] = args.port
    config['DEBUG'] = args.debug

    return parser.parse_args()


def get_path(path):
    if not os.path.isabs(path):  # If not absolute path
        path = os.path.join(config['ROOT_PATH'], path)
    return path