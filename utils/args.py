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
    parser.add_argument('-cf', '--config', is_config_file=True, help='Configuration file')
    parser.add_argument('-d', '--debug', help='Debug Mode', action='store_true', default=False)
    parser.add_argument('-H', '--host', help='Set web server listening host', default='127.0.0.1')
    parser.add_argument('-P', '--port', type=int, help='Web server port', default=3030)
    # Database args
    parser.add_argument('-DH', '--dbhost', help='mysql host')
    parser.add_argument('-u', '--user', help='mysql user')
    parser.add_argument('-pw', '--password', help='database password')
    parser.add_argument('-db', '--database', help='database name')
    parser.add_argument('-dbP', '--dbport', help='mysql port', default='3306')
    # Discord args
    parser.add_argument('-t', '--token', help='Discord bot token')
    parser.add_argument('-ch', '--channel', help='channel where registration is enabled', default='general')
    parser.add_argument('-us', '--usaddress', help='address order reversed from eu format',action='store_true', default=False)
    parser.add_argument('-pxf', '--prefix', help='what to start discord commands with', default='!')
    parser.add_argument('-F', '--forms', help='enable forms for mons that have it', action='store_true', default=False)

    parser.add_argument('-img', '--imgurl', help='source of alarm thumbnails', default='https://raw.githubusercontent.com/KartulUdus/Poracle/master/utils/images/icons/')
    parser.add_argument('-murl', '--mapurl', help='link to personal map in alarms', default=False)
    parser.add_argument('-bmap', '--bottommap', help='Enable, if you would like the map to be below the embedded details', action='store_true', default=False)
    parser.add_argument('--weatheruser', help='Username to GeoNames', default=False)
    # Static Map size

    parser.add_argument('-mw', '--mapwidth', type=int, help='static map width', default=250)
    parser.add_argument('-mh', '--mapheight', type=int, help='static map height ', default=175)

    # DTS args

# Bot respond dts
    parser.add_argument('--registering', help='', default='Hello {}, thank you for registering!')
    parser.add_argument('--alreadyreg', help='', default='Hello {}, you are already registered')
    parser.add_argument('--onlyinchannel', help='', default='Hello {}, !register is only available in #{}')
    parser.add_argument('--notregistered', help='', default='Hello {}, You are not currenlty registered!')
    parser.add_argument('--unregistered', help='', default='Hello {}, You are no longer registered!')
    parser.add_argument('--start', help='', default='Your alarms have been activated!')
    parser.add_argument('--onlyregistered', help='', default='This command is only available for registered humans! :eyes:')
    parser.add_argument('--locationfirst', help='', default='Please use `!location <location>` to set your location first :slight_smile:')
    parser.add_argument('--stop', help='', default='Your alarms have been stopped!')
    parser.add_argument('--onlydm', help='', default='Hello {}, This command is only available in DM ')
    parser.add_argument('--notfind', help='', default='I was unable to locate {}')
    parser.add_argument('--locationset', help='', default='I have set your location to {}. \n You can double check: {}')
    parser.add_argument('--badswitch', help='', default=':no_good: Invalid command.\nOptions: [map, address, iv, moveset, weather]')
    parser.add_argument('--switchyes', help='', default='I have turned {} on in your alarms')
    parser.add_argument('--switchno', help='', default='I have turned {} off in your alarms')
    parser.add_argument('--trackingadd', help='', default='I have updated tracking for: {} within {}m at least {}% perfect')
    parser.add_argument('--trackingupd', help='', default='I have updated tracking for: {} within {}m at least {}% perfect')
    parser.add_argument('--monnotfound', help='', default='I could not find {}')
    parser.add_argument('--nottracking', help='', default='You are not currently tracking {} :eyes:')
    parser.add_argument('--removedtracking', help='', default='I have removed tracking for: {}')
    parser.add_argument('--raidadded', help='', default='I have added tracking for: {} raids within {}m')
    parser.add_argument('--raidupd', help='', default='I have updated tracking for: {} raids distance to {}m')
    parser.add_argument('--invalidraidlvl', help='', default='Invalid raid level :no_good:')
    parser.add_argument('--eggadded', help='', default='I have added tracking for level {} raids within {}m ')
    parser.add_argument('--eggupdated', help='', default='I have updated changed level{} raid tracking distance to {}m')
    parser.add_argument('--eggnottracked', help='', default='You are not currently tracking lvl{} raid eggs :eyes:')
    parser.add_argument('--eggremoved', help='', default='I have removed tracking for level{} raids ')

# Monster alarm dts

    parser.add_argument('--pmtitle', help='', default='a wild {} has appeared!')
    parser.add_argument('--pmintro', help='', default='It will despawn at {}, you have {} left')
    parser.add_argument('--pltitle', help='', default=':map:')
    parser.add_argument('--plfield', help='field in location box *', default='Location: {}')
    parser.add_argument('--pivtitle', help='', default=':medal:')
    parser.add_argument('--pivfield', help='field in iv box ******', default='Perfection: **{}%** , ({}/{}/{}), Level:**{}** (cp:**{}**)')
    parser.add_argument('--pmvtitle', help='', default=':dancer:')
    parser.add_argument('--pmvfield', help='field in moveset box **', default='Quick move: {}, Charge Move: {}')

# Raid alarm dts
    parser.add_argument('--rmtitle', help='', default='Raid against {} has started!')
    parser.add_argument('--rmintro', help='', default='It will end at {}, in {}')
    parser.add_argument('--rltitle', help='', default=':map:')
    parser.add_argument('--rlfield', help='', default='{}')
    parser.add_argument('--rmvtitle', help='', default=':dancer:')
    parser.add_argument('--rmvfield', help='', default='Quick move: {}, Charge Move: {}')
    parser.add_argument('--rivtitle', help='', default='{}')
    parser.add_argument('--rivfield', help='', default='{}')
# Eggs
    parser.add_argument('--emtitle', help='', default='Level {} egg appeared!')
    parser.add_argument('--emintro', help='', default='It will begin at {}, (in {})')

# Weather and map link used globally
    parser.add_argument('--weathertitle', help='', default=':white_sun_cloud: {}')
    parser.add_argument('--weatherbody', help='', default='Temperature {}°C, {}')
    parser.add_argument('--RMtitle', help='', default=':eyes:')
    parser.add_argument('--RMlink', help='', default='{}')


    return parser.parse_args()


