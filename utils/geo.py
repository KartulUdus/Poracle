#!/usr/bin/python
# -*- coding: utf-8 -*-
import ujson as json
import logging
import requests
from xml.etree import ElementTree as ET
from cHaversine import haversine
from geopy.geocoders import Nominatim, GeoNames, GoogleV3
from staticmap import StaticMap, IconMarker
from args import args as get_args
from utils.mysql import get_all_weather_paths


args = get_args()
log = logging.getLogger('mysql')
log.setLevel(logging.DEBUG)


# Distance ([59.426372, 24.7705570], [59.432537, 24.7597870])


def distance(loc1, loc2):
    return haversine((tuple(loc1))[0:2], (tuple(loc2))[0:2])


# Geocodes words into coords


def geoloc(loc):
    log.info("Figuring out where {} is".format(loc))
    if args.gmaps:
        geo = GoogleV3(api_key=args.gmaps[0], timeout=1)
        try:
            pos = geo.geocode(loc, exactly_one=True, timeout=5)
            return pos.latitude, pos.longitude
        except AttributeError:
            return 'ERROR'
    else:
        geo = Nominatim()
        try:
            pos = geo.geocode(loc, exactly_one=True, timeout=5)
            return pos.latitude, pos.longitude
        except AttributeError:
            return 'ERROR'


# Reverse geocodes coords like [59.426372, 24.7705570] into words


def revgeoloc(loc):

    if args.gmaps:
        geo = GoogleV3(api_key=args.gmaps[0], timeout=5)
        pos = geo.reverse(loc, exactly_one=True, timeout=5)
        return json.loads(json.dumps(pos.raw['address_components']))
    else:
        geo = Nominatim()
        pos = geo.reverse((tuple(loc))[0:2], exactly_one=True, timeout=5)
        address = (pos.raw['display_name']).split(",")
        return address


def get_static_map_link(loc):
    width = args.mapwidth
    height = args.mapheight
    zoom = args.zoom

    center = '{},{}'.format(loc[0],loc[1])
    query_center = 'center={}'.format(center)
    query_markers = 'markers=color:red%7C{}'.format(center)
    query_size = 'size={}x{}'.format(width, height)
    query_zoom = 'zoom={}'.format(zoom)
    query_key = 'key={}'.format(args.gmaps[0])
    return ('https://maps.googleapis.com/maps/api/staticmap?' +
            query_center + '&' + query_markers + '&' +
            '&' + query_size + '&' + query_zoom + '&' + query_key)