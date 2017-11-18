#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
from args import args as get_args
import logging
import pymysql
from . import config

# Logging

log = logging.getLogger('mysql')
log.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s [%(threadName)18s][%(module)14s]' +
                              '[%(levelname)8s] %(message)s')
ch.setFormatter(formatter)
log.addHandler(ch)

# Test Db Connection

def connect_db():

    try:
        args = get_args(os.path.abspath(os.path.dirname(__file__)))
        return pymysql.connect(host="{}".format(
            args.host), port=int("{}".format(
                args.port)), user="{}".format(
            args.user), passwd="{}".format(
            args.password), database='{}'.format(args.database),
            connect_timeout=10)
    except pymysql.Error as e:
        log.critical("% d: % s\n" % (e.args[0], e.args[1]))
        exit(1)
        return False