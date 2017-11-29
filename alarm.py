import numpy as np
import time
import logging
from utils.mysql import check_if_geocoded, save_geocoding, update_team, \
                        who_cares, monster_any, spawn_geocoding
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

args = get_args()

min_iv = 0
adress = 'NULL'
gym_name = 'NULL'
description = 'NULL'
url = 'NULL'

def filter(hook):
    data = json.loads(json.dumps(hook))
    type = data['type']
    info = data['message']
    if data['message']['disappear_time'] > int(time.time()):
        if (type == 'pokemon'):
            pokemon(info)
        elif (type == 'gym_details'):
            if 'pokemon' in info:
                del info['pokemon']
            gym_info(info)
        elif (type == 'raid'):
            raid(info)
    else:
        log.warning("Weird, the thing already expired")

def pokemon(info):
    id = info['spawnpoint_id']
    lat = info['latitude']
    lon = info['longitude']
    monster_id = info['pokemon_id']
    name = get_monster_name(monster_id)
    if monster_any(monster_id):
        if not check_if_geocoded(id):
            if args.usaddress:
                address = ' '.join(
                    np.array(revgeoloc([lat, lon]))[[0, 1, 2, 3]]).encode(
                    'utf-8')
            else:
                address = ' '.join(
                    np.array(revgeoloc([lat, lon]))[[3, 2, 1, 0]]).encode(
                    'utf-8')
            spawn_geocoding(id,address,lat,lon)
            makemap(lat, lon, id)
            log.info('Made geocoded info for {}'.format(address))

        if 'individual_attack' not in info:
            iv = 0
        else:
            iv = round(float(((info['individual_attack'] + info['individual_defense'] + info['individual_stamina']) * 100) / float(45)),2)
        for human in who_cares('monster', info, iv):
            dis = distance([info['latitude'],info['longitude']], [human['latitude'], human['longitude']])
            if dis <= human['distance']:
                log.info("Alerting {} about {}".format(human['name'], name))   ### TODOO function to construct message and send

    else:
        log.info('{} has appeared, but no one cares'.format(name))


def raid(info):
    id = info['id']
    if check_if_geocoded(id):
        for human in who_cares('raid',info, 100):
            print human

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
        save_geocoding(id,team,address,name,description,url,lat,lon)
        makemap(lat, lon, id)
    else:
        update_team(id,team)


def get_monster_name(id):
    legend = json.loads(open('utils/dict/pokemon.json').read())
    return legend['{}'.format(int(id))]['name']

