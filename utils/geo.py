#!/usr/bin/python
# -*- coding: utf-8 -*-
import ujson as json
import logging
from cHaversine import haversine
from geopy.geocoders import Nominatim, GeoNames
from staticmap import StaticMap, IconMarker
from args import args as get_args

args = get_args()
log = logging.getLogger('mysql')
log.setLevel(logging.DEBUG)


# Distance ([59.426372, 24.7705570], [59.432537, 24.7597870])


def distance(loc1, loc2):
    return haversine((tuple(loc1))[0:2], (tuple(loc2))[0:2])


# Get's place name to later use for weather


def get_weather_area_name(loc):
    loc = GeoNames(username=args.weatheruser).reverse(loc, exactly_one=True)
    server = json.loads(json.dumps(loc.raw))
    return (
        server['countryName'] +
        '/' +
        server['adminName1'] +
        '/' +
        server['name']).replace(
        " ",
        "_")


# Geocodes words into coords


def geoloc(loc):
    log.info("Figuring out where {} is".format(loc))
    geo = Nominatim()
    try:
        pos = geo.geocode(loc, exactly_one=True)
        return pos.latitude, pos.longitude
    except AttributeError:
        return 'ERROR'


# Reverse geocodes coords like [59.426372, 24.7705570] into words


def revgeoloc(loc):
    geo = Nominatim()
    pos = geo.reverse((tuple(loc))[0:2], exactly_one=True)
    address = (pos.raw['display_name']).split(",")
    return address


# Stores static map image in images/geocoded/<spawn_gym_id>.png

def makemap(lat, lon, id):
    map = StaticMap(args.mapwidth, args.mapheight, 80,
                    url_template='http://a.tile.osm.org/{z}/{x}/{y}.png')
    marker = IconMarker((lon, lat), 'utils/images/icon-flag.png', 12, 32)
    map.add_marker(marker)
    image = map.render(zoom=15)
    image.save('utils/images/geocoded/{}.png'.format(id))
    log.info("Generated and saved {}.png".format(id))
    return
