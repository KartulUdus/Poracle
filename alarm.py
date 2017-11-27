import numpy as np
import os
import logging
from utils.mysql import check_if_geocoded, save_geocoding, update_team
from utils.args import args as get_args
from utils.geo import distance, revgeoloc, makemap
import ujson as json


# Logging
log = logging.getLogger('alarm')
log.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s [%(threadName)18s][%(module)14s]' +
                              '[%(levelname)8s] %(message)s')
ch.setFormatter(formatter)
log.addHandler(ch)
# Globals and defaults

args = get_args(os.path.abspath(os.path.dirname(__file__)))

min_iv = 0
adress = 'NULL'
gym_name = 'NULL'
description = 'NULL'
url = 'NULL'

def filter(hook):
    data = json.loads(json.dumps(hook))
    type = data['type']
    message = data['message']
    if (type == 'pokemon'):
        pokemon(message)
    elif (type == 'gym_details'):
        if 'pokemon' in message:
            del message['pokemon']
        gym_info(message)
    elif (type == 'raid'):
        raid(messge)

def pokemon(info):
    print 'I received a pokmeon:',info

def gym_info(info):
    id = info['id']
    url = info['url']
    name = info['name']
    description = info['description']
    team = info['team']
    lat = info['latitude']
    lon = info['longitude']
    if not check_if_geocoded(id):
        log.info('Geocoding info for gym {}'.format(name))
        if args.usaddress:
            address = ' '.join(
                np.array(revgeoloc([lat, lon]))[[0, 1, 2, 3]]).encode('utf-8')
        else:
            address = ' '.join(np.array(revgeoloc([lat,lon]))[[3, 2, 1, 0]]).encode('utf-8')
        save_geocoding(id,'raid',team,address,name,description,url,lat,lon)
        makemap(lat, lon, id)
    else:
        update_team(id,team)


def raid(info):
    print 'I received a raid:',info