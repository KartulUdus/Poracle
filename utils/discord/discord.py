#!/usr/bin/python
# -*- coding: utf-8 -*-
import re
import ujson as json
from disco.api.client import APIClient
from disco.types.message import (MessageEmbed,
                                 MessageEmbedThumbnail, MessageEmbedAuthor,
                                 MessageEmbedImage)
from utils.args import args as get_args


args = get_args()
if args.owner:
    runner = args.owner.replace("$","#")

def get_monster_id_from_name(id):
    num = False
    legend = json.loads(open('utils/dict/pokemon.json').read())
    for key, mon in legend.iteritems():
        if mon['name'].upper() == id.upper():
            num = key
    return num


class Alert(APIClient):
    def monster_alert(self, d):
        legend = json.loads(open('config/monsters.json').read())

        if 'form' in d:
            pmtitle = re.sub('<MON>', d['mon_name']+'({})'.format(d['form']),
                             legend['mon'])
        else:
            pmtitle = re.sub('<MON>', d['mon_name'], legend['mon'])
        pmintro = legend['time']

        description = pmintro

        adreu = d.get('street','') + d.get('street_num', '')
        adrus = d.get('street_num', '') + d.get('street', '')
        address = legend.get('address', '')
        stats = legend.get('iv', '')
        moves = legend.get('moves', '')
        boost = legend.get('weather', '')
        rmlinkfield = legend.get('RM', '')


        if d['geo_enabled']:
            description += address
        if 'atk' in d and d['iv_enabled']:
            description += stats
        if 'atk' in d and d['moves_enabled']:
            description += moves
        if 'boost' in d and d['weather_enabled']:
            description += boost
        if args.mapurl:
           description += rmlinkfield

        description = re.sub('<DESPAWN>', d.get('time', ''), description)
        description = re.sub('<TTH>', d.get('tth', ''), description)
        description = re.sub('<CITY>', d.get('city', ''), description)
        description = re.sub('<SUB>', d.get('suburb', ''), description)
        description = re.sub('<STR>', d.get('street', ''), description)
        description = re.sub('<STR_NUM>', d.get('street_num', ''), description)
        description = re.sub('<ADDR_EU>', adreu, description)
        description = re.sub('<ADDR_US>', adrus, description)
        description = re.sub('<IV>', str(d.get('perfection', '')), description)
        description = re.sub('<ATK>', str(d.get('atk', '')), description)
        description = re.sub('<DEF>', str(d.get('def', '')), description)
        description = re.sub('<STA>', str(d.get('sta', '')), description)
        description = re.sub('<LVL>', str(d.get('level', '')), description)
        description = re.sub('<CP>', str(d.get('cp', '')), description)
        description = re.sub('<MOVE1>', d.get('move1', ''), description)
        description = re.sub('<MOVE2>', d.get('move2', ''), description)
        description = re.sub('<WEA>', d.get('description', ''), description)
        description = re.sub('<RM>', d.get('mapurl', ''), description)

        embed = MessageEmbed(color=d['color'], description=description)

        if d['map_enabled']:
            embed.image = MessageEmbedImage(url=d['static'])

        embed.author = MessageEmbedAuthor(url=d['gmapurl'],
                                              name=pmtitle)
        embed.title = '{}'.format(d['mon_name'])
        embed.url = d['gmapurl']
        embed.thumbnail = MessageEmbedThumbnail(url=d['thumb'].lower())

        self.channels_messages_create(d['channel'], embed=embed)

    def raid_alert(self, d):
        legend = json.loads(open('config/raid.json').read())

        rmtitle = re.sub('<MON>', d['mon_name'], legend['raid'])
        rlfield = legend['time']
        adreu = d.get('street','') + d.get('street_num', '')
        adrus = d.get('street_num', '') + d.get('street', '')
        address = legend.get('address', '')
        gyminfo = legend['gyminfo']
        moves = legend['moves']
        boost = legend['weather']
        rmlinkfield = legend.get('RM', '')
        description = rlfield

        if d['geo_enabled']:
            description += address
        if d['iv_enabled']:
            description += gyminfo
        if d['moves_enabled']:
            description += moves
        if 'boost' in d and d['weather_enabled']:
            description += boost
        if args.mapurl:
            description += rmlinkfield

        description = re.sub('<DESPAWN>', d.get('time', ''), description)
        description = re.sub('<TTH>', d.get('tth', ''), description)
        description = re.sub('<CITY>', d.get('city', ''), description)
        description = re.sub('<SUB>', d.get('suburb', ''), description)
        description = re.sub('<STR>', d.get('street', ''), description)
        description = re.sub('<STR_NUM>', d.get('street_num', ''), description)
        description = re.sub('<ADDR_EU>', adreu, description)
        description = re.sub('<ADDR_US>', adrus, description)
        description = re.sub('<GYM>', d.get('gym_name', ''), description)
        description = re.sub('<INFO>', d.get('description', ''), description)
        description = re.sub('<MOVE1>', d.get('move1', ''), description)
        description = re.sub('<MOVE2>', d.get('move2', ''), description)
        description = re.sub('<WEA>', d.get('boost', ''), description)
        description = re.sub('<RM>', d.get('mapurl', ''), description)

        embed = MessageEmbed(color=d['color'], description=description)
        embed.url = (d['gmapurl'])
        embed.thumbnail = MessageEmbedThumbnail(url=d['img'])
        embed.author = MessageEmbedAuthor(icon_url=d['thumb'].lower(),
                                          name=rmtitle)
        embed.title = '{}'.format(d['mon_name'])
        embed.url = d['gmapurl']
        if d['map_enabled']:
            embed.image = MessageEmbedImage(url=d['static'])

        self.channels_messages_create(d['channel'], embed=embed)

    def egg_alert(self, d):

        legend = json.loads(open('config/egg.json').read())

        rmtitle = re.sub('<LVL>', str(d['level']), legend['raid'])
        rlfield = legend['time']
        adreu = d.get('street', '') + d.get('street_num', '')
        adrus = d.get('street_num', '') + d.get('street', '')
        address = legend.get('address', '')
        gyminfo = legend['gyminfo']
        boost = legend['weather']
        rmlinkfield = legend.get('RM', '')
        description = rlfield

        if d['geo_enabled']:
            description += address
        if d['iv_enabled']:
            description += gyminfo
        if 'boost' in d and d['weather_enabled']:
            description += boost
        if args.mapurl:
            description += rmlinkfield

        description = re.sub('<HATCH>', d.get('time', ''), description)
        description = re.sub('<TTH>', d.get('tth', ''), description)
        description = re.sub('<CITY>', d.get('city', ''), description)
        description = re.sub('<SUB>', d.get('suburb', ''), description)
        description = re.sub('<STR>', d.get('street', ''), description)
        description = re.sub('<STR_NUM>', d.get('street_num', ''), description)
        description = re.sub('<ADDR_EU>', adreu, description)
        description = re.sub('<ADDR_US>', adrus, description)
        description = re.sub('<GYM>', d.get('gym_name', ''), description)
        description = re.sub('<INFO>', d.get('description', ''), description)
        description = re.sub('<WEA>', d.get('boost', ''), description)
        description = re.sub('<RM>', d.get('mapurl', ''), description)

        embed = MessageEmbed(color=d['color'], description=description)
        embed.title = 'Raid level {}'.format(d['level'])
        embed.url = d['gmapurl']
        embed.author = MessageEmbedAuthor(icon_url=d['thumb'].lower(),
                                          name=rmtitle)
        embed.thumbnail = MessageEmbedThumbnail(url=d['img'])

        if d['map_enabled']:
            embed.image = MessageEmbedImage(url=d['static'])

        self.channels_messages_create(d['channel'], embed=embed)
