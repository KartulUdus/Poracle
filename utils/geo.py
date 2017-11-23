#!/usr/bin/python
# -*- coding: utf-8 -*-

from cHaversine import haversine
from args import args
from geopy.geocoders import Nominatim
from staticmap import StaticMap, IconMarker


log = logging.getLogger('mysql')
log.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s [%(threadName)18s][%(module)14s]' +
                              '[%(levelname)8s] %(message)s')
ch.setFormatter(formatter)
log.addHandler(ch)
args = get_args(os.path.abspath(os.path.dirname(__file__)))


##distance ([59.426372, 24.7705570], [59.432537, 24.7597870])

def distance(loc1, loc2):
    return haversine((tuple(loc1))[0:2], (tuple(loc2))[0:2])

## Geocodes words into coords

def geoloc(loc):
    log.info("Figuring out where {} is".format(loc))
    geo = Nominatim()
    pos = geo.geocode(loc, exactly_one=True)
    return ((pos.latitude, pos.longitude))

## Reverse geocodes coords like [59.426372, 24.7705570] into words

def revgeoloc(loc):
    geo = Nominatim()
    pos = geo.reverse((tuple(loc))[0:2], exactly_one=True)
    return (pos.raw['address'])


## Stores static map image in images/geocoded/<spawn_gym_id>.png

def makemap(lat,lon,id):
    map = StaticMap(330,250,80,
                    url_template='http://a.tile.osm.org/{z}/{x}/{y}.png')
    marker = IconMarker((lon, lat), 'utils/images/icon-flag.png', 12, 32)
    map.add_marker(marker)
    image = map.render(zoom=15)
    image.save('utils/images/geocoded/{}.png'.format(id))
    log.info("Generated and saved {}.png".format(id))
    return