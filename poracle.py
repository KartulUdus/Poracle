#!/usr/bin/python
# -*- coding: utf-8 -*-
import os, sys, logging, errno, subprocess, Queue, time
from alarm import filter
from utils.args import args as get_args
from utils.mysql import verify_database_schema
from gevent import wsgi, spawn, pool
from flask import Flask, request, abort
import ujson as json
from threading import Thread


app = Flask(__name__)
hook_q = Queue.Queue()
abspath = os.path.abspath(__file__)

reload(sys)
sys.setdefaultencoding('UTF8')

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
    if not os.path.isfile('./config/monsters.json'):
        log.info('Creating monster dts config')
        template = json.loads(open(os.path.join(os.path.dirname(
            abspath), 'config/monsters.json.example')).read())
        with open('./config/monsters.json', 'w') as monconf:
            json.dump(template, monconf, indent=4, sort_keys=False)

    if not os.path.isfile('./config/raid.json'):
        log.info('Creating raids dts config')
        template = json.loads(open(os.path.join(os.path.dirname(
            abspath), 'config/raid.json.example')).read())
        with open('./config/raid.json', 'w') as raidconf:
            json.dump(template, raidconf, indent=4, sort_keys=False)

    if not os.path.isfile('./config/egg.json'):
        log.info('Creating egg dts config')
        template = json.loads(open(os.path.join(os.path.dirname(
            abspath), 'config/egg.json.example')).read())
        with open('./config/egg.json', 'w') as eggconf:
            json.dump(template, eggconf, indent=4, sort_keys=False)
    try:
        os.remove('config.json')
    except OSError as e:
        if e.errno != errno.ENOENT:
            raise
    template = json.loads(open(os.path.join(os.path.dirname(abspath),'utils/discord/config.json')).read())
    template['token'] = args.token
    template['bot']['commands_prefix'] = args.prefix
    with open('config.json', 'w') as config:
        json.dump(template, config, indent=4, sort_keys=False)


def runserver():

    t = Thread(target=provision_bot,)
    t.daemon = True
    t.start()   # Start thread for discord bot

    log.info("Poracle is running on: http://{}:{}".format(args.host,
                                                          args.port))
    threads = pool.Pool(args.concurrency)
    server = wsgi.WSGIServer(
        (args.host, args.port), app, log=logging.getLogger('Webserver'),
        spawn = threads)
    server.serve_forever()


def provision_bot():

    p = run_bot()
    while True:

        res = p.poll()
        if res is not None:
            log.warn("Discord bot {} was killed, restarting it.".format(p.pid))
            p = run_bot()
        time.sleep(1)


def run_bot():
    return subprocess.Popen('python -m disco.cli', shell=True)


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
    runserver()
