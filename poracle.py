#!/usr/bin/python
# -*- coding: utf-8 -*-
import logging
import os
import subprocess
from utils.geo import geoloc, revgeoloc, makemap
from utils.args import args
from utils.mysql import verify_database_schema
from gevent import wsgi, spawn
from utils import config
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
args(os.path.abspath(os.path.dirname(__file__)))

def potato():

    log.info("Poracle is running on: http://{}:{}".format(config['HOST'], config['PORT']))
    server = wsgi.WSGIServer((config['HOST'], config['PORT']), app, log=logging.getLogger('Webserver'))
    server.serve_forever()

def run_bot():
    subprocess.Popen('python -m disco.cli --config utils/discord/config.yaml --log-level debug', shell=True)

@app.route('/', methods=['GET'])
def index():
    return "Schwing!"

@app.route('/', methods=['POST'])
def accept_webhook():
    try:
        log.debug("{} Sent me something.".format(request.remote_addr))
        data = json.loads(request.data)
        if type(data) == dict: # older webhook style
            log.debug(data)
        else:   # For RM's frame
            for frame in data:
                log.debug(frame)
    except Exception as e:
        log.error("I am unhappy, computer says: {}: {}".format(type(e).__name__, e))
        abort(400)
    return "OK"  # request ok

if __name__ == '__main__':
     log.info("Poracle initializing.")
 #    verify_database_schema()
     #run_bot()
 #    potato()
#    makemap(59.436816, 24.7427470,'potato')

