#!/usr/bin/python
# -*- coding: utf-8 -*-

from disco.bot import Plugin
from disco.types import channel


from disco.util.sanitize import S




class Register(Plugin):
    @Plugin.command('ping')
    def command_ping(self, event):
        if not(event.msg.channel.is_dm):
            event.msg.reply('Pong!')

    @Plugin.command('register')
    def command_register(self, event):
        if not (event.msg.channel.is_dm):
            if (event.msg.channel.name == 'general'):
                dmid = event.msg.author.open_dm().id
                print dmid
                print event.msg.author
                print event.msg.author.id

                event.msg.reply('Hello {}'.format(event.msg.author))

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