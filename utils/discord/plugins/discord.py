#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import print_function
from disco.bot import Plugin
from disco.util.sanitize import S


class BasicPlugin(Plugin):
    @Plugin.command('!ping')
    def on_ping_command(self, event):
        # Generally all the functionality you need to interact with is contained
        #  within the event object passed to command and event handlers.
        event.msg.reply('Hello {}=={}'.format(event.msg.author, event.msg.author.id))
        print (event.msg.author)