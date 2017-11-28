#!/usr/bin/python
# -*- coding: utf-8 -*-

import configargparse
import os
import sys


def args():

    configfile = []
    if '-cf' not in sys.argv and '--config' not in sys.argv:
        configfile = [os.getenv('CONFIG', os.path.join(
            os.path.dirname(__file__), '../config/config.ini'))]
    parser = configargparse.ArgParser(
        default_config_files=configfile)

    # Webserver args
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
    # Discord args
    parser.add_argument('-t', '--token', help='Discord bot token')
    parser.add_argument('-ch', '--channel', help='channel where registration is enabled', default='something')
    parser.add_argument('-us', '--usaddress', help='address order reversed from eu format',action='store_true', default=False)
    parser.add_argument('-pxf', '--prefix', help='what to start discord commands with', default='!')


    return parser.parse_args()


