#!/usr/bin/python
# -*- coding: utf-8 -*-
import ujson as json
from disco.bot import Plugin
from disco.api.client import APIClient
from disco.types.message import (MessageEmbed, MessageEmbedField,
                                 MessageEmbedThumbnail, MessageEmbedAuthor,
                                 MessageEmbedImage)
from utils.args import args as get_args
from utils.geo import geoloc
from utils.mysql import (
    registered,
    register,
    unregister,
    activate,
    deactivate,
    registered_by_name,
    set_location,
    check_if_tracked,
    add_tracking,
    update_tracking,
    remove_tracking,
    check_if_location_set,
    check_if_raid_tracked,
    remove_raid_tracking,
    add_raid_tracking,
    update_raid_tracking,
    check_if_egg_tracked,
    remove_egg_tracking,
    add_egg_tracking,
    update_egg_tracking,
    switch)

args = get_args()


def get_monster_id_from_name(id):
    num = False
    legend = json.loads(open('utils/dict/pokemon.json').read())
    for key, mon in legend.iteritems():
        if mon['name'].upper() == id.upper():
            num = key
    return num


class Commands(Plugin):
    # Help

    @Plugin.command('help')
    def command_help(self, event):
        help = '''
Hello, once you have reigstered in {0}, you can use the following commands:
```
{1}register - only avaiable in #{0}, registers user to start tracking
{1}unregister - only avaiable in #{0}, unregisters user
{1}location <place> - sets your base location to the address or place entered
{1}track <pokemon name> <max distance> [<minimum IV>] - will send alarms about 
monsters that are less than <max distance> meters away from the users set 
location, minimum IV is optional and defaults to 0
{1}untrack <pokemon name> - stops tracking monster
{1}raid <pokemon name> <max distance> - sends alarms for raid boss closer than 
<max distance> to user
{1}raid remove <pokemon name> - stops alarms for raid boss
{1}egg <level> <distance>  - sends alarms for raid eggs
{1}egg remove <level> - stops alarms for raid eggs
{1}stop - stop alarms
{1}start - start alarms (true by default on first registration)
{1}switch [address, iv, moves, map, weather] - 1 option only. 
Enables or disables fields of the alarm
```
        '''.format(args.channel, args.prefix)
        event.msg.reply(help)

        # Register DM id as human

    @Plugin.command('register')
    def command_register(self, event):
        dmid = event.msg.author.open_dm().id
        name = event.msg.author
        ping = event.msg.author.mention
        if not event.msg.channel.is_dm:
            if event.msg.channel.name == args.channel:
                if not (registered(dmid)):
                    register(dmid, name)
                    event.msg.reply(args.registering.format(ping))
                else:
                    event.msg.reply(args.alreadyreg.format(ping))
            else:
                event.msg.reply(args.onlyinchannel.format(ping, args.channel))

    @Plugin.command('unregister')
    def command_unregister(self, event):
        if not event.msg.channel.is_dm:
            if event.msg.channel.name == args.channel:
                dmid = event.msg.author.open_dm().id
                ping = event.msg.author.mention
                if not (registered(dmid)):
                    event.msg.reply(
                        args.notregistered.format(ping))
                else:
                    unregister(dmid)
                    event.msg.reply(args.unregistered.format(ping))

    @Plugin.command('start')
    def command_start(self, event):
        dmid = event.msg.channel.id
        ping = event.msg.author.mention
        name = event.msg.author
        if event.msg.channel.is_dm:
            if not (check_if_location_set(dmid)):
                if registered_by_name(name):
                    activate(dmid)
                    event.msg.reply(args.start)
                else:
                    event.msg.reply(args.onlyregistered)
            else:
                event.msg.reply(args.locationfirst)
        else:
            event.msg.reply(args.dmonly.format(ping))

    @Plugin.command('stop')
    def command_stop(self, event):
        dmid = event.msg.author.open_dm().id
        ping = event.msg.author.mention
        name = event.msg.author
        if event.msg.channel.is_dm:
            if registered_by_name(name):
                deactivate(dmid)
                event.msg.reply(args.stop)
            else:
                event.msg.reply(args.registered)
        else:
            event.msg.reply(args.onlydm.format(ping))

    @Plugin.command('location', '<content:str...>')
    def command_location(self, event, content):
        name = event.msg.author
        ping = event.msg.author.mention
        content = content.encode('utf-8')
        if event.msg.channel.is_dm:
            if not (registered_by_name(name)):
                event.msg.reply(args.onlyregistered)
            else:
                loc = geoloc(content)
                if loc == 'ERROR':
                    event.msg.reply(args.notfind.format(content))
                else:
                    set_location(name, loc[0], loc[1])
                    maplink = 'https://www.google.com/maps/search/' \
                              '?api=1&query=' + \
                              str(loc[0]) + ',' + str(loc[1])
                    event.msg.reply(
                        args.locationset.format(content, maplink))
        else:
            event.msg.reply(args.onlydm.format(ping))

            # Configure alarm blocks

    @Plugin.command('switch', '<field:str>')
    def format(self, event, field):
        dmid = event.msg.channel.id
        name = event.msg.author
        if event.msg.channel.is_dm:
            if registered_by_name(name):
                if field == 'map':
                    col = 'map_enabled'
                    state = switch(dmid, col)
                elif field == 'address':
                    col = 'address_enabled'
                    state = switch(dmid, col)
                elif field == 'iv':
                    col = 'iv_enabled'
                    state = switch(dmid, col)
                elif field == 'moveset':
                    col = 'moves_enabled'
                    state = switch(dmid, col)
                elif field == 'weather':
                    col = 'weather_enabled'
                    state = switch(dmid, col)
                else:
                    event.msg.reply(args.badswitch)
                try:
                    if state:
                        event.msg.reply(args.switchyes.format(col))
                    if not state:
                        event.msg.reply(args.switchno.format(col))
                except UnboundLocalError:
                    pass
            else:
                event.msg.reply(args.onlyregistered)
        else:
            event.msg.reply(args.onlydm.format(event.msg.author.mention))

            # Set or update tracking for monster

    @Plugin.command('track', '<monster:str>, <dis:int>, [iv:int]')
    def command_track(self, event, monster, dis, **kwargs):
        iv = kwargs.get('iv', 0)
        discordid = event.msg.channel.id
        name = event.msg.author
        if event.msg.channel.is_dm:
            if get_monster_id_from_name(monster):
                id = get_monster_id_from_name(monster)
                if registered_by_name(name):
                    if not (check_if_tracked(discordid, id)):
                        add_tracking(discordid, id, dis, iv)
                        event.msg.reply(
                            args.trackingadd.format(
                                monster, dis, iv))
                    else:
                        update_tracking(discordid, id, dis, iv)
                        event.msg.reply(
                            args.trackingupd.format(
                                monster, dis, iv))
                else:
                    event.msg.reply(args.onlyregistered)
            else:
                event.msg.reply(args.monnotfound.format(monster))
        else:
            event.msg.reply(args.onlydm.format(event.msg.author.mention))

            # Untrack monster:

    @Plugin.command('untrack', '<monster:str>')
    def command_untrack(self, event, monster):
        discordid = event.msg.channel.id
        name = event.msg.author
        if event.msg.channel.is_dm:
            if get_monster_id_from_name(monster):
                id = get_monster_id_from_name(monster)
                if registered_by_name(name):
                    if not (check_if_tracked(discordid, id)):
                        event.msg.reply(args.nottracking.format(monster))
                    else:
                        remove_tracking(discordid, id)
                        event.msg.reply(args.removedtracking.format(monster))
                else:
                    event.msg.reply(args.onlyregistered)

        else:
            event.msg.reply(args.onlydm.format(event.msg.author.mention))

    @Plugin.command('raid', '<monster:str> <dis:int>')
    def command_track_raid(self, event, monster, dis):
        discordid = event.msg.channel.id
        name = event.msg.author
        if event.msg.channel.is_dm:
            if registered_by_name(name):
                if get_monster_id_from_name(monster):
                    id = get_monster_id_from_name(monster)
                    if not (check_if_raid_tracked(discordid, id)):
                        add_raid_tracking(discordid, id, dis)
                        event.msg.reply(
                            args.raidadded.format(
                                monster, dis))
                    else:
                        update_raid_tracking(discordid, id, dis)
                        event.msg.reply(
                            args.raidupd.format(monster, dis))
                else:
                    event.msg.reply(args.monnotfound.format(monster))
            else:
                event.msg.reply(args.onlyregistered)

        else:
            event.msg.reply(args.onlydm.format(event.msg.author.mention))

            # Untrack monster:

    @Plugin.command('raid remove', '<monster:str>')
    def command_raid_remove(self, event, monster):
        discordid = event.msg.channel.id
        name = event.msg.author
        if event.msg.channel.is_dm:
            if registered_by_name(name):
                if get_monster_id_from_name(monster):
                    id = get_monster_id_from_name(monster)
                    if not (check_if_raid_tracked(discordid, id)):
                        event.msg.reply(args.nottracking.format(monster))
                    else:
                        remove_raid_tracking(discordid, id)
                        event.msg.reply(args.removedtracking.format(monster))
                else:
                    event.msg.reply(args.monnotfound.format(monster))
            else:
                event.msg.reply(args.onlyregistered)
        else:
            event.msg.reply(args.onlydm.format(event.msg.author.mention))

            # Eggs

    @Plugin.command('egg', '<level:int> <dis:int>')
    def command_track_egg(self, event, level, dis):
        discordid = event.msg.channel.id
        name = event.msg.author
        if event.msg.channel.is_dm:
            if registered_by_name(name):
                if level < 1 or level > 6:
                    event.msg.reply(args.invalidraidlvl)
                else:
                    if not (check_if_egg_tracked(discordid, level)):
                        add_egg_tracking(discordid, level, dis)
                        event.msg.reply(args.eggadded.format(level, dis))
                    else:
                        update_egg_tracking(discordid, level, dis)
                        event.msg.reply(
                            args.eggupdated.format(level, dis))
            else:
                event.msg.reply(args.onlyregistered)
        else:
            event.msg.reply(args.onlydm.format(event.msg.author.mention))

    @Plugin.command('egg remove', '<level:int>')
    def command_egg_remove(self, event, level):
        discordid = event.msg.channel.id
        name = event.msg.author
        if event.msg.channel.is_dm:
            if registered_by_name(name):

                if not (check_if_egg_tracked(discordid, level)):
                    event.msg.reply(args.eggnottracked
                                    .format(level))
                else:
                    remove_egg_tracking(discordid, level)
                    event.msg.reply(args.eggremoved.format(level))
            else:
                event.msg.reply(args.onlyregistered)
        else:
            event.msg.reply(args.onlydm.format(event.msg.author.mention))


class Alert(APIClient):
    def monster_alert(self, d):
        embed = MessageEmbed(color=d['color'])
        img = ''
        if 'form' in d:
            embed.author = MessageEmbedAuthor(
                name=(
                    d['mon_name'] +
                    ' (form: {})'.format(
                        d['form'])),
                url=d['gmapurl'])
        else:
            embed.author = MessageEmbedAuthor(
                name=d['mon_name'], url=d['gmapurl'])
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
        embed.author = MessageEmbedAuthor(
            name=(d['mon_name']),
            url=d['gmapurl'])
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
        embed.author = MessageEmbedAuthor(
            name=('Raid level {}'.format(d['level'])),
            url=d['gmapurl'])
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
