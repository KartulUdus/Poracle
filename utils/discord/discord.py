#!/usr/bin/python
# -*- coding: utf-8 -*-
import ujson as json
from disco.api.client import APIClient
from disco.types.message import (MessageEmbed, MessageEmbedField,
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
        embed = MessageEmbed(color=d['color'])
        img = ''
        if 'form' in d:
            embed.title = (
                d['mon_name'] + ' (form: {})'.format(d['form']))
            embed.url = d['gmapurl']
        else:
            embed.title = d['mon_name']
            embed.url = d['gmapurl']
        if not args.bottommap:
            if d['map_enabled']:
                img = ['static.png', open(d['static'], 'r')]
        embed.thumbnail = MessageEmbedThumbnail(url=d['thumb'].lower())
        embed.fields.append(
            MessageEmbedField(name=args.pmtitle.format(d['mon_name']),
                              value=args.pmintro.format(d['time'], d['tth']))
        )

        if d['geo_enabled']:
            embed.fields.append(
                MessageEmbedField(name=args.pltitle,
                                  value=args.plfield.format(d['address']))
            )

        if 'atk' in d and d['iv_enabled']:
            embed.fields.append(
                MessageEmbedField(
                    name=args.pivtitle,
                    value=args.pivfield.format(
                        d['perfection'],
                        d['atk'],
                        d['def'],
                        d['sta'],
                        d['level'],
                        d['cp'])))
        if 'atk' in d and d['moves_enabled']:
            embed.fields.append(
                MessageEmbedField(
                    name=args.pmvtitle,
                    value=args.pmvfield.format(
                        d['move1'],
                        d['move2'])))
        if args.weatheruser and 'wtemp' in d:
            embed.fields.append(
                MessageEmbedField(
                    name=args.weathertitle.format(
                        d['wdescription']), value=args.weatherbody.format(
                        d['wtemp'], d['wwind'])))
        if args.mapurl:
            embed.fields.append(
                MessageEmbedField(name=args.RMtitle,
                                  value=args.RMlink.format(d['mapurl']))
            )

        self.channels_messages_create(
            d['channel'], attachment=img, embed=embed)

        if args.bottommap and d['map_enabled']:
            img = ['static.png', open(d['static'], 'r')]
            self.channels_messages_create(d['channel'], attachment=list(img))

    def raid_alert(self, d):
        img = ''
        embed = MessageEmbed(color=d['color'])
        embed.title = (d['mon_name'])
        embed.url(d['gmapurl'])
        if not args.bottommap:
            if d['map_enabled']:
                img = ['static.png', open(d['static'], 'r')]
        embed.thumbnail = MessageEmbedThumbnail(url=d['thumb'].lower())
        embed.fields.append(
            MessageEmbedField(name=args.rmtitle.format(d['mon_name']),
                              value=args.rmintro.format(d['time'], d['tth']))
        )

        if d['geo_enabled']:
            embed.fields.append(
                MessageEmbedField(name=args.rltitle,
                                  value=args.rlfield.format(d['address']))
            )
            embed.image = MessageEmbedImage(url=d['img'], width=50, height=50)

        if d['moves_enabled']:
            embed.fields.append(
                MessageEmbedField(
                    name=args.rmvtitle,
                    value=args.rmvfield.format(
                        d['move1'],
                        d['move2'])))

        if d['iv_enabled']:
            embed.fields.append(
                MessageEmbedField(name=args.rivtitle.format(d['gym_name']),
                                  value=args.rivfield.format(d['description']))
            )

        if args.weatheruser and 'wtemp' in d:
            embed.fields.append(
                MessageEmbedField(
                    name=args.weathertitle.format(
                        d['wdescription']), value=args.weatherbody.format(
                        d['wtemp'], d['wwind'])))
        self.channels_messages_create(
            d['channel'], attachment=img, embed=embed)
        if args.bottommap and d['map_enabled']:
            img = ['static.png', open(d['static'], 'r')]
            self.channels_messages_create(d['channel'], attachment=list(img))

    def egg_alert(self, d):
        img = ''
        embed = MessageEmbed(color=d['color'])
        embed.title('Raid level {}'.format(d['level']))
        embed.url(d['gmapurl'])
        if not args.bottommap:
            if d['map_enabled']:
                img = ['static.png', open(d['static'], 'r')]

        embed.fields.append(
            MessageEmbedField(name=args.emtitle.format(d['level']),
                              value=args.emintro.format(d['time'], d['tth']))
        )
        if d['iv_enabled']:
            embed.fields.append(
                MessageEmbedField(
                    name=args.rivtitle.format(
                        d['gym_name']), value=args.rivfield.format(
                        d['description'])))
        if d['geo_enabled']:
            embed.fields.append(
                MessageEmbedField(name=args.rltitle,
                                  value=args.rlfield.format(d['address']))
            )
            embed.image = MessageEmbedImage(url=d['img'], width=50, height=50)

        if args.weatheruser and 'wtemp' in d:
            embed.fields.append(
                MessageEmbedField(
                    name=args.weathertitle.format(
                        d['wdescription']), value=args.weatherbody.format(
                        d['wtemp'], d['wwind'])))

        embed.thumbnail = MessageEmbedThumbnail(url=d['thumb'])

        self.channels_messages_create(
            d['channel'], attachment=img, embed=embed)
        if args.bottommap and d['map_enabled']:
            img = ['static.png', open(d['static'], 'r')]
            self.channels_messages_create(d['channel'], attachment=list(img))
