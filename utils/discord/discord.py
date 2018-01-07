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
        pmintro = re.sub('<DESPAWN>', d['time'], legend['time'])
        pmintro = re.sub('<TTH>', d['tth'], pmintro)

        description = pmintro
        if d['geo_enabled']:
            adreu = d['street'] + d['street_num']
            adrus = d['street_num'] + d['street']
            address = legend['address']
            address = re.sub('<CITY>', d['city'], address)
            address = re.sub('<SUB>', d['suburb'], address)
            address = re.sub('<STR>', d['street'], address)
            address = re.sub('<STR_NUM>', d['street_num'], address)
            address = re.sub('<ADDR_EU>', adreu, address)
            address = re.sub('<ADDR_US>', adrus, address)
            description += address
        if 'atk' in d and d['iv_enabled']:
            stats = legend['iv']
            stats = re.sub('<IV>',  str(d['perfection']), stats)
            stats = re.sub('<ATK>', str(d['atk']), stats)
            stats = re.sub('<DEF>', str(d['def']), stats)
            stats = re.sub('<STA>', str(d['sta']), stats)
            stats = re.sub('<LVL>', str(d['level']), stats)
            stats = re.sub('<CP>', str(d['cp']), stats)
            description += stats
        if 'atk' in d and d['moves_enabled']:
            moves = legend['moves']
            moves = re.sub('<MOVE1>', d['move1'], moves)
            moves = re.sub('<MOVE2>', d['move2'], moves)
            description += moves
        if 'boost' in d and d['weather_enabled']:
            boost = legend['weather']
            boost = re.sub('<WEA>', d['boost'], boost)
            description += boost
        if args.mapurl:
            rmlinkfield = re.sub('<RM>', d['mapurl'], legend['RM'])
            description += rmlinkfield

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
        rlfield = re.sub('<DESPAWN>', d['time'], legend['time'])
        rlfield = re.sub('<TTH>', d['tth'], rlfield)

        description = rlfield


        if d['geo_enabled']:
            adreu = d['street'] + d['street_num']
            adrus = d['street_num'] + d['street']
            address = legend['address']
            address = re.sub('<CITY>', d['city'], address)
            address = re.sub('<SUB>', d['suburb'], address)
            address = re.sub('<STR>', d['street'], address)
            address = re.sub('<STR_NUM>', d['street_num'], address)
            address = re.sub('<ADDR_EU>', adreu, address)
            address = re.sub('<ADDR_US>', adrus, address)
            description += address
        if d['iv_enabled']:
            gyminfo = re.sub('<GYM>', d['gym_name'], legend['gyminfo'])
            gyminfo = re.sub('<INFO>', d['description'], gyminfo)
            description += gyminfo
        if d['moves_enabled']:
            moves = legend['moves']
            moves = re.sub('<MOVE1>', d['move1'], moves)
            moves = re.sub('<MOVE2>', d['move2'], moves)
            description += moves
        if 'boost' in d and d['weather_enabled']:
            boost = legend['weather']
            boost = re.sub('<WEA>', d['boost'], boost)
            description += boost
        if args.mapurl:
            rmlinkfield = re.sub('<RM>', d['mapurl'], legend['RM'])
            description += rmlinkfield


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
        rlfield = re.sub('<HATCH>', d['time'], legend['time'])
        rlfield = re.sub('<TTH>', d['tth'], rlfield)
        description = rlfield
        if d['geo_enabled']:
            adreu = d['street'] + d['street_num']
            adrus = d['street_num'] + d['street']
            address = legend['address']
            address = re.sub('<CITY>', d['city'], address)
            address = re.sub('<SUB>', d['suburb'], address)
            address = re.sub('<STR>', d['street'], address)
            address = re.sub('<STR_NUM>', d['street_num'], address)
            address = re.sub('<ADDR_EU>', adreu, address)
            address = re.sub('<ADDR_US>', adrus, address)
            description += address
        if d['iv_enabled']:
            gyminfo = re.sub('<GYM>', d['gym_name'], legend['gyminfo'])
            gyminfo = re.sub('<INFO>', d['description'], gyminfo)
            description += gyminfo
        if 'boost' in d and d['weather_enabled']:
            boost = legend['weather']
            boost = re.sub('<WEA>', d['boost'], boost)
            description += boost
        if args.mapurl:
            rmlinkfield = re.sub('<RM>', d['mapurl'], legend['RM'])
            description += rmlinkfield

        embed = MessageEmbed(color=d['color'], description=description)
        embed.title = '{}'.format(d['mon_name'])
        embed.url = d['gmapurl']
        embed.author = MessageEmbedAuthor(icon_url=d['thumb'].lower(),
                                          name=rmtitle)
        embed.thumbnail = MessageEmbedThumbnail(url=d['img'])

        if d['map_enabled']:
            embed.image = MessageEmbedImage(url=d['static'])

        self.channels_messages_create(d['channel'], embed=embed)
