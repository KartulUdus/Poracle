#!/usr/bin/python
# -*- coding: utf-8 -*-
import logging
import os, sys
import errno
import subprocess
from alarm import filter
from utils.args import args as get_args
from utils.mysql import verify_database_schema
from gevent import wsgi, spawn
from flask import Flask, request, abort
import Queue
import ujson as json


app = Flask(__name__)
hook_q = Queue.Queue()

# create logger

reload(sys)
sys.setdefaultencoding('UTF8')

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
    try:
        os.remove('config.json')
    except OSError as e:
        if e.errno != errno.ENOENT:
            raise
    template = json.loads(open('utils/discord/config.json').read())
    template['token'] = args.token
    template['bot']['commands_prefix'] = args.prefix
    with open('config.json', 'w') as config:
        json.dump(template, config, indent=4, sort_keys=False)


def runserver():

    log.info("Poracle is running on: http://{}:{}".format(args.host,
                                                          args.port))
    server = wsgi.WSGIServer(
        (args.host, args.port), app, log=logging.getLogger('Webserver'))
    server.serve_forever()


def run_bot():
    subprocess.Popen('python -m disco.cli ', shell=True)


@app.route('/', methods=['GET'])
def index():
    return "Schwing!"


@app.route('/', methods=['POST'])
def accept_webhook():
    try:
        data = json.loads(request.data)
        for frame in data:
            if args.debug:
                di = json.dumps(frame, indent=4, sort_keys=True)
                log.debug("{} Sent me:\n{}".format(request.remote_addr, di))
            hook_q.put(frame)
        spawn(send_hooks_to_filter, hook_q)
    except Exception as e:
        log.error(
            "I am unhappy! computer says: {}: {}".format(
                type(e).__name__, e))
        abort(400)
    return "OK"  # request ok

hook_q.join()


def send_hooks_to_filter(q):
    while not q.empty():
        if q.qsize() > 300:
            log.warning("Not cool, I have {} jobs to do".format(q.qsize()))
        data = q.get()
        filter(data)
        q.task_done()


if __name__ == '__main__':
    log.info("Poracle initializing.")
    verify_database_schema()
    make_configs()
    run_bot()
    runserver()


