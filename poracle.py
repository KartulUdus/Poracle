#!/usr/bin/python
# -*- coding: utf-8 -*-
import logging
import os
import subprocess
from collections import OrderedDict
from alarm import filter
from utils.args import args as get_args
from utils.mysql import verify_database_schema
from gevent import wsgi, spawn
from flask import Flask, request, abort
import sys
import Queue
import ujson as json


app = Flask(__name__)
data_queue = Queue.Queue()

# create logger
log = logging.getLogger('Poracle')
log.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s [%(threadName)18s][%(module)14s]' +
                              '[%(levelname)8s] %(message)s')
ch.setFormatter(formatter)
log.addHandler(ch)

args = get_args()

def make_configs():
    template = json.loads(open('utils/discord/config.json').read())
    template['token'] = args.token
    template['bot']['commands_prefix'] = args.prefix
    with open('config.json', 'w') as config:
        json.dump(template, config, indent=4, sort_keys=False)

def potato():

    log.info("Poracle is running on: http://{}:{}".format(args.host, args.port))
    server = wsgi.WSGIServer((args.host, args.port), app, log=logging.getLogger('Webserver'))
    server.serve_forever()

def run_bot():
    subprocess.Popen('python -m disco.cli ', shell=True)

@app.route('/', methods=['GET'])
def index():
    return "Schwing!"

@app.route('/', methods=['POST'])
def accept_webhook():
    try:
        log.debug("{} Sent me something.".format(request.remote_addr))
        data = json.loads(request.data)
        if type(data) == dict: # older webhook style
            filter(data)
        else:   # For RM's frame
            for frame in data:
                filter(frame)
    except Exception as e:
        log.error("I am unhappy! computer says: {}: {}".format(type(e).__name__, e))
        abort(400)
    return "OK"  # request ok

if __name__ == '__main__':
     log.info("Poracle initializing.")
     verify_database_schema()
     make_configs()
     run_bot()
     potato()
