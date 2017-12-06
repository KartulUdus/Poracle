#!/usr/bin/python
# -*- coding: utf-8 -*-
import numpy as np
from xml.etree import ElementTree as ET
import requests
import time
import logging
from utils.mysql import (check_if_geocoded, save_geocoding, update_team,
    who_cares, monster_any, spawn_geocoding, get_address,
    add_alarm_counter, get_geocoded, check_if_weather,
    update_weather_path, raid_any, update_weather, get_weather,
    get_weather_updated, cache_exist, cache_insert, clear_cache)
from utils.discord.discord import Alert
from utils.args import args as get_args
from utils.geo import distance, revgeoloc, makemap, get_weather_area_name
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
now = int(time.time())
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
            if data['message']['disappear_time'] > now:
                if not cache_exist(info['encounter_id'], 'despawn'):
                    cache_insert(info['encounter_id'], info['disappear_time'], 'despawn')
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
                cache_insert(info['gym_id'], info['spawn'], 'hatch')
                raid(info)
        else:
            if not cache_exist(info['gym_id'],'hatch'):
                cache_insert(info['gym_id'], info['spawn'], 'hatch')
                cache_insert(info['gym_id'], info['end'], 'raid_end')
                raid(info)


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
            spawn_geocoding(id, address, lat, lon)
            makemap(float(lat), float(lon), id)
            log.info('Made geocoded info for {}'.format(address))

        if args.weatheruser:
            if not check_if_weather(id):
                path = get_weather_area_name([lat, lon])
                update_weather_path(id, path)

        if info['individual_attack'] is None:
            iv = 0
        else:
            iv = round(
                float(
                    ((info['individual_attack'] +
                      info['individual_defense'] +
                        info['individual_stamina']) *
                        100) /
                    float(45)),
                2)
        clear_cache()
        for human in who_cares('monster', info, iv):
            dis = distance([info['latitude'], info['longitude']], [
                           human['latitude'], human['longitude']])
            if dis <= human['distance']:
                log.info("Alerting {} about {}".format(human['name'], name))

                create_message('monster', info, human)

    else:
        log.info('{} has appeared, but no one cares'.format(name))


def raid(info):
    id = info['gym_id']
    if info['pokemon_id'] is not None:
        if check_if_geocoded(id):
            if raid_any(info['pokemon_id'], 0):
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
                    'Raid agains {} has appeared, but no one cares'.format(
                        get_monster_name(
                            info['pokemon_id'])))
    else:
        if check_if_geocoded(id):
            if raid_any(info['level'], 1):
                for human in who_cares('raid', info, 100):
                    dis = distance([info['latitude'], info['longitude']], [
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
        log.info('Geocoding info for gym {}'.format(name))
        if args.usaddress:
            address = ' '.join(
                np.array(revgeoloc([lat, lon]))[[0,1,2]]).encode('utf-8')
        else:
            address = ' '.join(np.array(revgeoloc([lat, lon]))[
                               [2,1,0]]).encode('utf-8')
        save_geocoding(id, team, address, name, description, url, lat, lon)
        makemap(lat, lon, id)

    else:
        update_team(id, team)
    if args.weatheruser:
        if not check_if_weather(id):
            path = get_weather_area_name([lat, lon])
            update_weather_path(id, path)


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


def get_forecast(area):
    if now - get_weather_updated(area) > 21600:
        weatherurl = 'https://www.yr.no/place/{}/forecast.xml'.format(area)
        weather = requests.get(weatherurl, timeout=5)
        tree = ET.fromstring(weather.content)[5][0][0]
        for tag in tree.iter('windSpeed'):
            wind = '{}: {}mps'.format(tag.attrib['name'], tag.attrib['mps'])
        for tag in tree.iter('symbol'):
            description = tag.attrib['name']
        for tag in tree.iter('temperature'):
            temp = tag.attrib['value']
        log.info('getting new weather forecast for {}'.format(area))
        update_weather(area, description, wind, temp)
    return get_weather(area)


def create_message(type, data, human):

    if type == 'monster':

        d = {}
        d['channel'] = human['id']
        d['mon_name'] = get_monster_name(data['pokemon_id']).encode('utf-8')
        d['color'] = get_monster_color(data['pokemon_id'])
        d['map_enabled'] = human['map_enabled']
        d['iv_enabled'] = human['iv_enabled']
        d['moves_enabled'] = human['moves_enabled']
        d['geo_enabled'] = human['address_enabled']
        d['iv_enabled'] = human['iv_enabled']
        d['address'] = get_address(data['spawnpoint_id'])[
            0]['address'].encode('utf-8')
        d['tth'] = time.strftime(
            "%Mm %Ss", time.gmtime(
                data['seconds_until_despawn']))
        d['time'] = time.strftime("%H:%M:%S",
                                  time.localtime(int(data['disappear_time'])))
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
                        100) /
                    float(45)),
                2)
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
        d['static'] = 'utils/images/geocoded/' + \
            data['spawnpoint_id'] + '.png'.encode('utf-8')
        if args.weatheruser and human['weather_enabled']:
            areaname = get_geocoded(data['spawnpoint_id'])['weather_path']
            weather = get_forecast(areaname)
            d['wdescription'] = weather['description']
            d['wtemp'] = weather['temperature']
            d['wwind'] = weather['windspeed']

        add_alarm_counter(human['id'])

        Alert(args.token).monster_alert(d)

    elif type == 'raid':
        geo = get_geocoded(data['gym_id'])
        seconds_until_despawn = data['end'] - now

        d = {}
        d['channel'] = human['id']
        d['mon_name'] = get_monster_name(data['pokemon_id']).encode('utf-8')
        d['color'] = get_team_color(geo['team'])
        d['map_enabled'] = human['map_enabled']
        d['iv_enabled'] = human['iv_enabled']
        d['moves_enabled'] = human['moves_enabled']
        d['geo_enabled'] = human['address_enabled']
        d['iv_enabled'] = human['iv_enabled']
        d['move1'] = get_monster_move(int(data['move_1'])).encode('utf-8')
        d['move2'] = get_monster_move(int(data['move_2'])).encode('utf-8')
        d['tth'] = time.strftime("%Mm %Ss", time.gmtime(seconds_until_despawn))
        d['time'] = time.strftime("%H:%M:%S", time.localtime(int(data['end'])))
        d['address'] = geo['address'].encode('utf-8')
        d['gym_name'] = geo['gym_name'].encode('utf-8')
        d['description'] = geo['description'].encode('utf-8')
        d['img'] = geo['url']
        d['thumb'] = args.imgurl + '{}.png'.format(data['pokemon_id'])
        d['gmapurl'] = 'https://www.google.com/maps/search/?api=1&query=' + \
            str(data['latitude']) + ',' + str(data['longitude'])
        d['static'] = 'utils/images/geocoded/' + data['gym_id'] + '.png'
        if args.mapurl:
            d['mapurl'] = args.mapurl + '?lat=' + \
                str(geo['latitude']) + '&lon=' + str(geo['longitude'])
        if args.weatheruser and human['weather_enabled']:
            areaname = get_geocoded(data['gym_id'])['weather_path']
            weather = get_forecast(areaname)
            d['wdescription'] = weather['description']
            d['wtemp'] = weather['temperature']
            d['wwind'] = weather['windspeed']
        if seconds_until_despawn > 0:
            Alert(args.token).raid_alert(d)
        else:
            log.warning("Weird, the raid already ended")

    elif type == 'egg':
        geo = get_geocoded(data['gym_id'])
        time_til_hatch = data['spawn'] - now
        d = {}

        d['thumb'] = args.imgurl + 'egg.png'
        d['img'] = geo['url']
        d['channel'] = human['id']
        d['level'] = data['level']
        d['color'] = get_team_color(geo['team'])
        d['map_enabled'] = human['map_enabled']
        d['geo_enabled'] = human['address_enabled']
        d['tth'] = time.strftime("%Mm %Ss", time.gmtime(time_til_hatch))
        d['time'] = time.strftime(
            "%H:%M:%S", time.localtime(int(data['start'])))
        d['gmapurl'] = 'https://www.google.com/maps/search/?api=1&query=' + \
            str(data['latitude']) + ',' + str(data['longitude'])
        d['static'] = 'utils/images/geocoded/' + data['gym_id'] + '.png'
        d['iv_enabled'] = human['iv_enabled']
        d['gym_name'] = geo['gym_name'].encode('utf-8')
        d['description'] = geo['description'].encode('utf-8')
        d['address'] = geo['address'].encode('utf-8')
        if args.mapurl:
            d['mapurl'] = args.mapurl + '?lat=' + \
                str(geo['latitude']) + '&lon=' + str(geo['longitude'])
        if args.weatheruser and human['weather_enabled']:
            areaname = get_geocoded(data['gym_id'])['weather_path']
            weather = get_forecast(areaname)
            d['wdescription'] = weather['description']
            d['wtemp'] = weather['temperature']
            d['wwind'] = weather['windspeed']
        if time_til_hatch > 0:
            log.info(
                "Alerting {} about level {} raid".format(
                    human['name'], data['level']))
            Alert(args.token).egg_alert(d)
        else:
            log.warning("Weird, the egg already hatched")
