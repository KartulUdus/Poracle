#!/usr/bin/python
# -*- coding: utf-8 -*-
import configargparse
import os
import sys


def args():

    configfile = []
    if '-cf' not in sys.argv and '--config' not in sys.argv:
        configfile = [os.getenv('CONFIG', os.path.join(
            os.path.dirname(__file__), '../config/config.ini'))]
    parser = configargparse.ArgParser(
        default_config_files=configfile)

    # Webserver args
    parser.add_argument(
        '-cf',
        '--config',
        is_config_file=True,
        help='Configuration file')
    parser.add_argument(
        '-d',
        '--debug',
        help='Debug Mode',
        action='store_true',
        default=False)
    parser.add_argument(
        '-H',
        '--host',
        help='Set web server listening host',
        default='127.0.0.1')
    parser.add_argument(
        '-P',
        '--port',
        type=int,
        help='Web server port',
        default=3030)
    # Database args
    parser.add_argument('-DH', '--dbhost', help='mysql host')
    parser.add_argument('-u', '--user', help='mysql user')
    parser.add_argument('-pw', '--password', help='database password')
    parser.add_argument('-db', '--database', help='database name')
    parser.add_argument('-dbP', '--dbport', help='mysql port', default='3306')
    # Discord args
    parser.add_argument('-t', '--token',
                        required = True,
                        type=str,
                        help='Discord bot token')
    parser.add_argument(
        '-ch',
        '--channel',
        help='channel where registration is enabled',
        default='general')
    parser.add_argument(
        '-us',
        '--usaddress',
        help='address order reversed from eu format',
        action='store_true',
        default=False)
    parser.add_argument(
        '-pxf',
        '--prefix',
        help='what to start discord commands with',
        default='!')
    parser.add_argument(
        '-F',
        '--forms',
        help='enable forms for mons that have it',
        action='store_true',
        default=False)

    parser.add_argument(
        '-img',
        '--imgurl',
        help='source of alarm thumbnails',
        default='https://raw.githubusercontent.com/KartulUdus/Poracle/'
                'master/utils/images/icons/')
    parser.add_argument(
        '-murl',
        '--mapurl',
        help='link to personal map in alarms',
        default=False)
    parser.add_argument(
        '-bmap',
        '--bottommap',
        help='Enable, to move the map below the embedded details',
        action='store_true',
        default=False)
    parser.add_argument(
        '--owner',
        help='Username of owner',
        type=str,
        default='poracle$1234')

    parser.add_argument(
        '-Imp',
        '--imperial',
        help='Time in 12h format',
        action='store_true',
        default=False)

    # Static Map size

    parser.add_argument(
        '-gm',
        '--gmaps',
        help='google maps api key', default=None, action='append',
        required=True)

    parser.add_argument(
        '-mw',
        '--mapwidth',
        type=int,
        help='static map width',
        default=250)
    parser.add_argument(
        '-mh',
        '--mapheight',
        type=int,
        help='static map height',
        default=175)

    parser.add_argument(
        '-z',
        '--zoom',
        type=int,
        help='static map zoom',
        default=15)

    parser.add_argument(
        '-mt',
        '--map-type',
        type=str,
        help='static map style',
        default='roadmap')
    parser.add_argument(
        '-C', '--concurrency', type=int,
        help = 'Maximum concurrent connections for the webserver',
        default = 200)

    # DTS args

# Bot respond dts
    parser.add_argument(
        '--registering',
        default='Hello {}, thank you for registering!')
    parser.add_argument(
        '--alreadyreg',
        default='Hello {}, you are already registered')
    parser.add_argument(
        '--onlyinchannel',
        default='Hello {}, !poracle is only available in #{}')
    parser.add_argument(
        '--notregistered',
        default='Hello {}, You are not currenlty registered!')
    parser.add_argument(
        '--unregistered',
        default='Hello {}, You are no longer registered!')
    parser.add_argument(
        '--start',
        default='Your alarms have been activated!')
    parser.add_argument(
        '--onlyregistered',
        default='This command is only available for registered users :eyes:')
    parser.add_argument(
        '--channelnotfound',
        default='This channel isn\'t registered :eyes:')

    parser.add_argument(
        '--locationfirst',
        default='Please use `!location <location>` to set your location first'
                ' :slight_smile:')
    parser.add_argument(
        '--stop',
        default='Your alarms have been stopped!')
    parser.add_argument(
        '--onlydm',
        default='Hello {}, This command is only available in DM ')
    parser.add_argument(
        '--notfind',
        default='I was unable to locate {}')
    parser.add_argument(
        '--locationset',
        default='I have set your location to {}. \n You can double check: {}')
    parser.add_argument(
        '--badswitch',
        default=':no_good: Invalid command.\nOptions: [map, address, iv,'
                ' moveset, weather]')
    parser.add_argument(
        '--switchyes',
        default='I have turned {} on in your alarms')
    parser.add_argument(
        '--switchno',
        default='I have turned {} off in your alarms')
    parser.add_argument(
        '--trackingadd',
        default='I have added tracking for: {} within {}m at least {}%'
                ' perfect')
    parser.add_argument(
        '--trackingupd',
        default='I have updated tracking for: {} within {}m at least {}%'
                ' perfect')
    parser.add_argument(
        '--monnotfound',
        default='I could not find {}')
    parser.add_argument(
        '--nottracking',
        default='You are not currently tracking {} :eyes:')
    parser.add_argument(
        '--removedtracking',
        default='I have removed tracking for: {}')
    parser.add_argument(
        '--raidadded',
        default='I have added tracking for: {} raids within {}m')
    parser.add_argument(
        '--raidupd',
        default='I have updated tracking for: {} raids distance to {}m')
    parser.add_argument(
        '--invalidraidlvl',
        default='Invalid raid level :no_good:')
    parser.add_argument(
        '--eggadded',
        default='I have added tracking for level {} raids within {}m ')
    parser.add_argument(
        '--eggupdated',
        default='I have updated level{} raid tracking distance to {}m')
    parser.add_argument(
        '--eggnottracked',
        default='You are not currently tracking lvl{} raid eggs :eyes:')
    parser.add_argument(
        '--eggremoved',
        default='I have removed tracking for level{} raids ')
    parser.add_argument(
        '--perfect-added',
        default='I have added :100: alarms within {}m')
    parser.add_argument(
        '--perfect-updated',
        default='I have updated :100: alarms within {}m')
    parser.add_argument(
        '--special-removed',
        default='I have removed tracking for {} pokemon')
    return parser.parse_args()
