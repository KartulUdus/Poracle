#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import ujson as json
from disco.bot import Plugin, Bot
from disco.api.client import APIClient
from disco.types.message import MessageEmbed, MessageEmbedField, MessageEmbedThumbnail, MessageEmbedAuthor
from disco.api.http import HTTPClient
from utils.args import args as get_args
from utils.geo import geoloc
from utils.mysql import (registered, register, unregister, activate, deactivate,
                        registered_by_name, set_location, check_if_tracked,
                        add_tracking, update_tracking, remove_tracking,
                        check_if_location_set, check_if_raid_tracked, remove_raid_tracking, add_raid_tracking)

args = get_args()

class Commands(Plugin):

## Register DM id as human
    @Plugin.command('register')
    def command_register(self, event):
        dmid = event.msg.author.open_dm().id
        name = event.msg.author
        ping = event.msg.author.mention
        if not (event.msg.channel.is_dm):
            if (event.msg.channel.name == args.channel):
                if not(registered(dmid)):
                    register(dmid,name)
                    event.msg.reply('Hello {}, thank you for registering!'.format(ping))
                else:
                    event.msg.reply('Hello {}, you are already registered'.format(ping))
            else:
                event.msg.reply(
                    'Hello {}, !register is only available in #{}'.format(ping, args.channel))


## Unregister humans DM id
    @Plugin.command('unregister')
    def command_unregister(self, event):
        if not (event.msg.channel.is_dm):
            if (event.msg.channel.name == args.channel):
                dmid = event.msg.author.open_dm().id
                ping = event.msg.author.mention
                if not (registered(dmid)):
                    event.msg.reply(
                        'Hello {}, You are not currenlty registered!'.format(ping))
                else:
                    unregister(dmid)
                    event.msg.reply(
                        'Hello {}, You are no longer registered!'.format(ping))

## Enable alarms for human
    @Plugin.command('start')
    def command_start(self, event):
        dmid = event.msg.channel.id
        ping = event.msg.author.mention
        name = event.msg.author
        if (event.msg.channel.is_dm):
            if not (check_if_location_set(dmid)):
                if (registered_by_name(name)):
                    activate(dmid)
                    print event
                    event.msg.reply('Your alarms have been activated!')
                else:
                    event.msg.reply(
                        'This command is only available for registered humans! :eyes:')
            else:
                event.msg.reply(
                    'Please use `!location <location>` to set your location first :slight_smile:')
        else:
            event.msg.reply('Hello {}, This command is only available in DM '.format(ping))


## Disable alarms for human
    @Plugin.command('stop')
    def command_stop(self, event):
        dmid = event.msg.author.open_dm().id
        ping = event.msg.author.mention
        name = event.msg.author
        if (event.msg.channel.is_dm):
            if (registered_by_name(name)):
                deactivate(dmid)
                event.msg.reply('Your alarms have been stopped!')
            else:
                event.msg.reply(
                    'This command is only available for registered humans! :eyes:')
        else:
            event.msg.reply('Hello {}, This command is only available in DM '.format(ping))

## Set Humans Location
    @Plugin.command('location', '<content:str...>')
    def command_location(self, event, content):
        name = event.msg.author
        ping = event.msg.author.mention
        content = content.encode('utf-8')
        if (event.msg.channel.is_dm):
            if not (registered_by_name(name)):
                event.msg.reply(
                    'This command is only available for registered humans! :eyes:')
            else:
                loc = geoloc(content)
                if (loc == 'ERROR'):
                    event.msg.reply(
                        'I was unable to locate {}'.format(content))
                else:
                    set_location(name,loc[0],loc[1])
                    maplink = 'https://www.google.com/maps/search/?api=1&query=' + str(loc[0]) + ',' + str(loc[1])
                    event.msg.reply(
                        'I have set your location to {}. \n You can double check: {}'.format(content,maplink))
        else:
            event.msg.reply(
                'Hello {}, This command is only available in DM'.format(ping))


 ## Set or update tracking for monster

    @Plugin.command('track', '<id:int> <dis:int> <iv:int>')
    def command_track(self, event, id, dis, iv):
        discordid = event.msg.channel.id
        name = event.msg.author
        if (event.msg.channel.is_dm):
            if(registered_by_name(name)):
                if not(check_if_tracked(discordid, id)):
                    add_tracking(discordid,id,dis,iv)
                    event.msg.reply('I have added tracking for: {} within {}m at least {}% percect'.format(id,dis,iv))
                else:
                    update_tracking(discordid,id,dis,iv)
                    event.msg.reply(
                        'I have updated tracking for: {} within {}m at least {}% percect'.format(
                            id, dis, iv))
            else:
                event.msg.reply(
                    'This command is only available for registered humans! :eyes:')

        else:
            event.msg.reply(
                'Tracking is only available in DM for registered humans')

 ## Untrack monster:


    @Plugin.command('untrack', '<id:int>')
    def command_untrack(self, event, id):
        discordid = event.msg.channel.id
        name = event.msg.author
        if (event.msg.channel.is_dm):
            if(registered_by_name(name)):
                if not(check_if_tracked(discordid, id)):
                    event.msg.reply('You are not currently tracking {} :eyes:'.format(id))
                else:
                    remove_tracking(discordid,id)
                    event.msg.reply('I have removed tracking for: {} '.format(id))
            else:
                event.msg.reply(
                    'This command is only available for registered humans! :eyes:')

        else:
            event.msg.reply(
                'Tracking is only available in DM for registered humans')



#######################################raid

    ## Set or update tracking for raid

    @Plugin.command('raid', '<id:int> <dis:int>')
    def command_track_raid(self, event, id, dis):
        discordid = event.msg.channel.id
        name = event.msg.author
        if (event.msg.channel.is_dm):
            if (registered_by_name(name)):
                if not (check_if_raid_tracked(discordid, id)):
                    add_raid_tracking(discordid, id, dis)
                    event.msg.reply(
                        'I have added tracking for: {} raids within {}m '.format(
                            id, dis))
                else:
                    update_raid_tracking(discordid, id, dis)
                    event.msg.reply(
                        'I have updated tracking for: {} raids distance to {}m'.format(
                            id, dis, iv))
            else:
                event.msg.reply(
                    'This command is only available for registered humans! :eyes:')

        else:
            event.msg.reply(
                'Tracking is only available in DM for registered humans')

            ## Untrack monster:

    @Plugin.command('raid remove', '<id:int>')
    def command_raid_remove(self, event, id):
        discordid = event.msg.channel.id
        name = event.msg.author
        if (event.msg.channel.is_dm):
            if (registered_by_name(name)):
                if not (check_if_raid_tracked(discordid, id)):
                    event.msg.reply(
                        'You are not currently tracking {} :eyes:'.format(
                            id))
                else:
                    remove_raid_tracking(discordid, id)
                    event.msg.reply(
                        'I have removed tracking for: {} '.format(id))
            else:
                event.msg.reply(
                    'This command is only available for registered humans! :eyes:')

        else:
            event.msg.reply(
                'Tracking is only available in DM for registered humans')

class Alert(APIClient):
    def alert(self, d):
        print d

        embed = MessageEmbed(color=d['color'])
        embed.author = MessageEmbedAuthor(name=d['mon_name'],url=d['gmapurl'])

        print d['form']
        self.channels_messages_create(d['channel'], embed=embed)




        # #image1 = [MessageEmbedField(name='potato', value='https://b1naryth1ef.github.io/disco/api/disco_types_message.html')]
        # embed = MessageEmbed(color=7915600)
        # embed.fields.append(
        #     MessageEmbedField(name='potato',
        #                       value='')
        # )
        # embed.fields.append(
        #     MessageEmbedField(name='potato',
        #                       value='')
        # )
        # embed.thumbnail = MessageEmbedThumbnail(url=icon)
        #
        # pic = (['testmap2.png', open('utils/images/geocoded/testmap2.png', 'r')])
        # self.channels_messages_create(channel,content='PLEASE WORK!',attachment=pic, embed=embed,)
