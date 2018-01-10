#!/usr/bin/python
# -*- coding: utf-8 -*-
import time, os
import logging
from utils.mysql import (check_if_geocoded, save_geocoding, update_team,
    who_cares, monster_any, add_alarm_counter, get_geocoded,
    raid_any, cache_exist, cache_insert, clear_cache)
from utils.discord.discord import Alert
from utils.args import args as get_args
from utils.geo import distance, revgeoloc, get_static_map_link
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

abspath = os.path.abspath(__file__)
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
    if type == 'pokemon':
        if info['verified']:
            now = int(time.time())
            if data['message']['disappear_time'] > now:
                if not cache_exist(info['encounter_id'], 'despawn'):
                    cache_insert(info['encounter_id'],
                                 info['disappear_time'], 'despawn')
                    pokemon(info)
                else:
                    log.info('I have already processed this monster')
            else:
                log.warning('Weird, the monster already disappeared')
        else:
            log.info('The monster isn\'t verified, I don\'t trust it')
    elif type == 'gym_details':
        if 'pokemon' in info:
            del info['pokemon']
        gym_info(info)
    elif type == 'raid':

        if info['pokemon_id'] is not None:
            if not cache_exist(info['gym_id'],'raid_end'):
                cache_insert(info['gym_id'], info['end'], 'raid_end')
                cache_insert(info['gym_id'], info['start'], 'hatch')
                raid(info)
        else:
            if not cache_exist(info['gym_id'],'hatch'):
                cache_insert(info['gym_id'], info['start'], 'hatch')
                raid(info)


def pokemon(info):
    lat = info['latitude']
    lon = info['longitude']
    monster_id = info['pokemon_id']
    name = get_monster_name(monster_id)

    if info['individual_attack'] is None:
        iv = 0
    else:
        iv = round(
            float(
                ((info['individual_attack'] +
                  info['individual_defense'] +
                  info['individual_stamina']) *
                 100) / float(45)), 2)
    print iv
    if iv == 100:
        perfect_alert(info)

    if monster_any(monster_id):

        someone_is_close_enough = False
        for human in who_cares('monster', info, iv):

            dis = distance([info['latitude'], info['longitude']], [
                           human['latitude'], human['longitude']])
            if dis <= human['distance']:
                someone_is_close_enough = True
                clear_cache()
                continue

        if someone_is_close_enough:
            info['googlemap'] = get_static_map_link([lat, lon])
            info['geocoded'] = revgeoloc([info['latitude'], info['longitude']])
            for human in who_cares('monster', info, iv):
                dis = distance([info['latitude'], info['longitude']], [
                    human['latitude'], human['longitude']])
                if dis <= human['distance']:
                    log.info(
                        'Alerting {} about {}'.format(human['name'], name))
                    create_message('monster', info, human)
        else:
            log.info(
                '{} has appeared, but no one was close enough'.format(name))
    else:
        log.info('{} has appeared, but no one cares'.format(name))

def perfect_alert(info):
    if monster_any(9000):
        lat = info['latitude']
        lon = info['longitude']
        monster_id = info['pokemon_id']
        name = get_monster_name(monster_id)
        someone_is_close_enough = False
        info['pokemon_id'] = 9000

        for human in who_cares('monster', info, 100):

            dis = distance([info['latitude'], info['longitude']], [
                human['latitude'], human['longitude']])
            if dis <= human['distance']:
                someone_is_close_enough = True
                clear_cache()
                continue
        if someone_is_close_enough:
            info['googlemap'] = get_static_map_link([lat, lon])
            info['geocoded'] = revgeoloc([info['latitude'], info['longitude']])
            for human in who_cares('monster', info, 100):
                human['pokemon_id'] = info['pokemon_id']
                dis = distance([info['latitude'], info['longitude']], [
                    human['latitude'], human['longitude']])
                if dis <= human['distance']:
                    human['pokemon_id'] = monster_id
                    info['pokemon_id'] = monster_id
                    log.info(
                        'Alerting {} about {}'.format(human['name'], name))
                    create_message('monster', info, human)
        else:
            log.info(
            'perfect {} has appeared, but no one was close enough'.format(
                                                                        name))

def raid(info):
    id = info['gym_id']
    lat = info['latitude']
    lon = info['longitude']
    if info['pokemon_id'] is not None:
        if check_if_geocoded(id):
            if raid_any(info['pokemon_id'], 0):
                someone_is_close_enough = False
                for human in who_cares('raid', info, 100):
                    dis = distance([info['latitude'], info['longitude']], [
                        human['latitude'], human['longitude']])
                    if dis <= human['distance']:
                        someone_is_close_enough = True
                        clear_cache()
                        continue
                if someone_is_close_enough:
                    info['googlemap'] = get_static_map_link([lat, lon])
                    info['geocoded'] = revgeoloc(
                        [info['latitude'], info['longitude']])
                    for human in who_cares('raid', info, 100):
                        dis = distance([info['latitude'], info['longitude']], [
                            human['latitude'], human['longitude']])
                        if dis <= human['distance']:
                            create_message('raid', info, human)
                            log.info(
                                "Alerting {} about {} raid".format(
                                    human['name'], get_monster_name(
                                        info['pokemon_id'])))
            else:
                log.info(
                    'Raid against {} has appeared, but no one cares'.format(
                        get_monster_name(
                            info['pokemon_id'])))
        else:
            log.warn(
                'Raid against {} appeared, but gym has not been saved'.format(
                get_monster_name(info['pokemon_id'])
            ))

    else:
        if check_if_geocoded(id):
            if raid_any(info['level'], 1):
                someone_is_close_enough = False
                for human in who_cares('raid', info, 100):
                    dis = distance([info['latitude'], info['longitude']], [
                        human['latitude'], human['longitude']])
                    if dis <= human['distance']:
                        someone_is_close_enough = True
                        clear_cache()
                        continue
                if someone_is_close_enough:
                    info['googlemap'] = get_static_map_link([lat, lon])
                    info['geocoded'] = revgeoloc(
                        [info['latitude'], info['longitude']])
                    for human in who_cares('raid', info, 100):
                        dis = distance(
                            [info['latitude'], info['longitude']], [
                                human['latitude'], human['longitude']])
                        if dis <= human['distance']:
                            create_message('egg', info, human)

            else:
                log.info(
                    'Egg level {} has appeared, but no one cares'.format(
                        info['level']))


def gym_info(info):
    id = info['id']
    url = info['url']
    name = info['name']
    description = info['description']
    team = info['team']
    lat = info['latitude']
    lon = info['longitude']
    if not check_if_geocoded(id):
        log.info('Saving gym info for {}'.format(name))

        save_geocoding(id, team, 'None', name, description, url, lat, lon)

    else:
        update_team(id, team)



def get_weather_name(id):
    legend = json.loads(open('utils/dict/gameweather.json').read())
    return legend['{}'.format(int(id))]

def get_monster_name(id):
    legend = json.loads(open('utils/dict/pokemon.json').read())
    return legend['{}'.format(int(id))]['name']


def get_monster_move(id):
    legend = json.loads(open('utils/dict/moves.json').read())
    return legend['{}'.format(int(id))]['name']


def get_monster_color(id):
    legend = json.loads(open('utils/dict/pokemon.json').read())
    return legend['{}'.format(int(id))]['types'][0]['color']


def get_team_color(id):
    legend = json.loads(open('utils/dict/teams.json').read())
    return legend['{}'.format(int(id))]['color']


def get_monster_form(id, form):
    legend = json.loads(open('utils/dict/forms.json').read())
    return legend[str(id)][str(form)]



def create_message(type, data, human):

    if type == 'monster':
        now = int(time.time())
        seconds_until_despawn = data['disappear_time'] - now
        d = {}
        d['channel'] = human['id']
        d['mon_name'] = get_monster_name(data['pokemon_id']).encode('utf-8')
        d['color'] = get_monster_color(data['pokemon_id'])
        d['map_enabled'] = human['map_enabled']
        d['iv_enabled'] = human['iv_enabled']
        d['moves_enabled'] = human['moves_enabled']
        d['geo_enabled'] = human['address_enabled']
        d['iv_enabled'] = human['iv_enabled']
        d['weather_enabled'] = human['weather_enabled']
        d['street_num'] = data['geocoded'][0]['short_name']
        d['street'] = data['geocoded'][1]['short_name']
        d['suburb'] = data['geocoded'][2]['short_name']
        d['city'] = data['geocoded'][3]['short_name']
        d['tth'] = time.strftime(
            "%Mm %Ss", time.gmtime(seconds_until_despawn))

        if not args.imperial:
            d['time'] = time.strftime("%H:%M:%S",
                                  time.localtime(int(data['disappear_time'])))
        else:
            d['time'] = time.strftime("%I:%M:%S %p",
                                      time.localtime(
                                          int(data['disappear_time'])))
        d['thumb'] = args.imgurl + \
            '{}.png'.format(data['pokemon_id']).encode('utf-8')
        if data['individual_attack'] is not None:
            d['atk'] = data['individual_attack']
            d['def'] = data['individual_defense']
            d['sta'] = data['individual_stamina']
            d['cp'] = data['cp']
            d['level'] = data['pokemon_level']
            d['move1'] = get_monster_move(int(data['move_1'])).encode('utf-8')
            d['move2'] = get_monster_move(int(data['move_2'])).encode('utf-8')
            d['perfection'] = round(
                float(
                    ((data['individual_attack'] +
                      data['individual_defense'] +
                        data['individual_stamina']) *
                        100) / float(45)),  2)
        if data['form'] is not None:
            d['form'] = get_monster_form(
                int(data['pokemon_id']), data['form']).encode('utf-8')
        if args.mapurl:
            d['mapurl'] = args.mapurl + '?lat=' + \
                str(data['latitude']) + '&lon=' + str(data['longitude'])
        if args.forms and data['form'] is not None:
            d['thumb'] = args.imgurl + \
                '{}-{}.png'.format(int(data['pokemon_id']), d['form'])
        d['gmapurl'] = 'https://www.google.com/maps/search/?api=1&query=' + \
            str(data['latitude']) + ',' + str(data['longitude'])

        d['static'] = data['googlemap']

        if 'weather' in data:
            d['boost'] = get_weather_name(data['weather'])

        add_alarm_counter(human['id'])

        Alert(args.token).monster_alert(d)

    elif type == 'raid':
        now = int(time.time())
        geo = get_geocoded(data['gym_id'])
        seconds_until_despawn = data['end'] - now

        d = {}
        d['channel'] = human['id']
        d['mon_name'] = get_monster_name(data['pokemon_id']).encode('utf-8')
        d['color'] = get_team_color(geo['team'])
        d['map_enabled'] = human['map_enabled']
        d['iv_enabled'] = human['iv_enabled']
        d['weather_enabled'] = human['weather_enabled']
        d['moves_enabled'] = human['moves_enabled']
        d['geo_enabled'] = human['address_enabled']
        d['iv_enabled'] = human['iv_enabled']
        d['move1'] = get_monster_move(int(data['move_1'])).encode('utf-8')
        d['move2'] = get_monster_move(int(data['move_2'])).encode('utf-8')
        d['tth'] = time.strftime("%Mm %Ss",
                                 time.gmtime(seconds_until_despawn))
        if not args.imperial:
            d['time'] = time.strftime(
                "%H:%M:%S", time.localtime(int(data['end'])))
        else:
            d['time'] = time.strftime(
                "%I:%M:%S %p", time.localtime(int(data['end'])))

        d['street_num'] = data['geocoded'][0]['short_name']
        d['street'] = data['geocoded'][1]['short_name']
        d['suburb'] = data['geocoded'][2]['short_name']
        d['city'] = data['geocoded'][3]['short_name']
        d['gym_name'] = geo['gym_name'].encode('utf-8')
        d['description'] = geo['description'].encode('utf-8')
        d['img'] = geo['url']
        d['thumb'] = args.imgurl + '{}.png'.format(data['pokemon_id'])
        d['gmapurl'] = 'https://www.google.com/maps/search/?api=1&query=' + \
            str(data['latitude']) + ',' + str(data['longitude'])

        d['static'] = data['googlemap']
        if args.mapurl:
            d['mapurl'] = args.mapurl + '?lat=' + \
                str(geo['latitude']) + '&lon=' + str(geo['longitude'])

        if seconds_until_despawn > 0:
            Alert(args.token).raid_alert(d)
        else:
            log.warning("Weird, the raid already ended")

    elif type == 'egg':
        now = int(time.time())
        geo = get_geocoded(data['gym_id'])
        time_til_hatch = data['start'] - now
        d = {}

        d['thumb'] = args.imgurl + 'egg.png'
        d['img'] = geo['url']
        d['channel'] = human['id']
        d['level'] = data['level']
        d['color'] = get_team_color(geo['team'])
        d['map_enabled'] = human['map_enabled']
        d['geo_enabled'] = human['address_enabled']
        d['tth'] = time.strftime("%Mm %Ss", time.gmtime(time_til_hatch))

        if not args.imperial:
            d['time'] = time.strftime(
               "%H:%M:%S", time.localtime(int(data['start'])))
        else:
            d['time'] = time.strftime(
                "%I:%M:%S %p", time.localtime(int(data['start'])))

        d['gmapurl'] = 'https://www.google.com/maps/search/?api=1&query=' + \
            str(data['latitude']) + ',' + str(data['longitude'])
        d['static'] = data['googlemap']
        d['iv_enabled'] = human['iv_enabled']
        d['gym_name'] = geo['gym_name'].encode('utf-8')
        d['description'] = geo['description'].encode('utf-8')
        d['street_num'] = data['geocoded'][0]['short_name']
        d['street'] = data['geocoded'][1]['short_name']
        d['suburb'] = data['geocoded'][2]['short_name']
        d['city'] = data['geocoded'][3]['short_name']
        if args.mapurl:
            d['mapurl'] = args.mapurl + '?lat=' + \
                str(geo['latitude']) + '&lon=' + str(geo['longitude'])

        if time_til_hatch > 0:
            log.info(
                "Alerting {} about level {} raid".format(
                    human['name'], data['level']))
            Alert(args.token).egg_alert(d)
        else:
            log.warning("Weird, the egg already hatched")
