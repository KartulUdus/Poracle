#!/usr/bin/python
# -*- coding: utf-8 -*-

from disco.bot import Plugin
from disco.types import channel

from disco.util.sanitize import S


from utils.mysql import registered, register, unregister


class Commands(Plugin):
    @Plugin.command('ping')
    def command_ping(self, event):
        if not(event.msg.channel.is_dm):
            event.msg.reply('Pong!')

    @Plugin.command('register')

    def command_register(self, event):
        if not (event.msg.channel.is_dm):
            if (event.msg.channel.name == 'general'):
                dmid = event.msg.author.open_dm().id
                name = event.msg.author
                ping = event.msg.author.mention
                if not(registered(dmid)):
                    register(dmid,name)
                    event.msg.reply('Hello {}, thank you for registering!'.format(ping))
                else:
                    event.msg.reply('Hello {}, you are already registered'.format(ping))

    @Plugin.command('unregister')
    def command_unregister(self, event):
        if not (event.msg.channel.is_dm):
            if (event.msg.channel.name == 'general'):
                dmid = event.msg.author.open_dm().id
                name = event.msg.author
                ping = event.msg.author.mention
                if not (registered(dmid)):
                    event.msg.reply(
                        'Hello {}, You are not currenlty registered!'.format(ping))
                else:
                    unregister(dmid)
                    event.msg.reply(
                        'Hello {}, You are no longer registered!'.format(ping))

    @Plugin.command('potato')

    def command_potato(self, event):
        if not (event.msg.channel.is_dm):
            if (event.msg.channel.name == 'general'):
                dm = event.msg.author.open_dm()
                dm.send_message('Hello @{}'.format(event.msg.author))
                print event.msg.author.id

                if (event.msg.author.id == 22274285905956048):
                    print(dm.id)





                    # potato = event.msg.channel
        # print bool(potato.is_dm)
        # event.msg.reply('Pong!')
        # print potato.name, potato.id
        # print event.msg.author.id

# class SendDm(Plugin):
#
#                     dm_channel = self.bot.client.state.dms.get( < dm_id >)
#                     dm_channel.send_message('<content>')
#      @Plugin.command('!pong')
#      def on_ping_command(self, event):
#          if (event.msg.channel.name!='generael'):
#             event.msg.reply(
#
     #       if (channel.ChannelType == 2):
            #           'Hello {}=={}'.format(event.msg.author, event.msg.author.id))

         ##event.msg.channel.name