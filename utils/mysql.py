#!/usr/bin/python
# -*- coding: utf-8 -*-
import time
from args import args as get_args
import logging
from peewee import (InsertQuery, MySQLDatabase, Model,
                    SmallIntegerField, IntegerField, CharField, DoubleField,
                    BooleanField, TextField, OperationalError, IntegrityError)
#from peewee import *
# Globals

sb_schema_version = 2
now = int(time.time())

# Logging

log = logging.getLogger('mysql')
log.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s [%(threadName)18s][%(module)14s]' +
                              '[%(levelname)8s] %(message)s')
ch.setFormatter(formatter)
log.addHandler(ch)

args = get_args()
# Test Db Connection


db = MySQLDatabase(host="{}".format(
    args.dbhost), port=int("{}".format(
    args.dbport)), user="{}".format(
    args.user), passwd="{}".format(
    args.password), database='{}'.format(args.database),
    connect_timeout=10)


########################################################
# Tables and MySQL migration
########################################################

class BaseModel(Model):
    class Meta:
        database = db


class humans(BaseModel):
    id = CharField(primary_key=True, index=True, unique=True)
    name = CharField(index=True, max_length=50)
    alerts_sent = IntegerField(index=True, default=0)
    enabled = BooleanField(default=True)
    address_enabled = BooleanField(default=True)
    map_enabled = BooleanField(default=True)
    iv_enabled = BooleanField(default=True)
    moves_enabled = BooleanField(default=True)
    weather_enabled = BooleanField(default=False)
    latitude = DoubleField(null=True)
    longitude = DoubleField(null=True)

    class Meta:
        indexes = ((('latitude', 'longitude'), False),)
        order_by = ('id',)


class monsters(BaseModel):
    human_id = CharField(index=True, max_length=30)
    pokemon_id = SmallIntegerField(index=True)
    distance = IntegerField(index=True)
    min_iv = SmallIntegerField(index=True)

    class Meta:
        order_by = ('id',)


class raid(BaseModel):
    human_id = CharField(index=True, max_length=30)
    pokemon_id = CharField(index=True, max_length=20)
    egg = BooleanField(default=False)
    distance = IntegerField(index=True)

    class Meta:
        order_by = ('id',)


class geocoded(BaseModel):
    id = CharField(index=True, max_length=50)
    type = CharField(index=True, max_length=20)
    weather_path = CharField(index=True, null=True, max_length=100)
    team = SmallIntegerField(null=True)
    address = CharField(index=True)
    gym_name = CharField(index=True, max_length=50, null=True)
    description = TextField(null=True, default="")
    url = CharField(null=True)
    latitude = DoubleField()
    longitude = DoubleField()

    class Meta:
        indexes = ((('latitude', 'longitude'), False),)
        primary_key = False


class weather(BaseModel):
    area = CharField(primary_key=True, index=True, max_length=100)
    updated = IntegerField(index=True, null=True)
    description = CharField(null=True, index=True, max_length=50)
    windspeed = CharField(null=True, index=True, max_length=50)
    temperature = IntegerField(null=True, index=True)


class schema_version(BaseModel):
    key = CharField()
    val = SmallIntegerField()


class cache(BaseModel):
    id = CharField(primary_key=True, index=True, max_length=50)
    despawn = IntegerField(index=True, null=True)
    hatch = IntegerField(index=True, null=True)
    raid_end = IntegerField(index=True, null=True)



    class Meta:
        primary_key = False


# Db Migration


def create_tables():
    db.create_tables([humans, monsters, raid, geocoded,
                      weather, schema_version], safe=True)


def verify_database_schema():
    log.info('Connecting to MySQL database on {}:{}'.format(args.dbhost,
                                                            args.dbport))
    try:

        if not schema_version.table_exists():
            create_tables()
            if humans.table_exists():
                InsertQuery(schema_version, {
                    schema_version.key: 'schema_version',
                    schema_version.val: 1}).execute()

        if not cache.table_exists():
            schema_version.update(val=2).where(
                schema_version.key == 'schema_version').execute()
            db.create_table(cache, safe=True)
            db.close()

    except OperationalError as e:
        log.critical("MySQL unhappy [ERROR]:% d: % s\n" % (
            e.args[0], e.args[1]))
        exit(1)


########################################################
# Caching
########################################################

def cache_exist(id, col):
    if not cache.select().where(cache.id == id).exists():
        return False
    else:
        f = cache.select().where(cache.id == id).dicts()
        if f[0][col] > now:
            return True
        else:
            return False


def cache_insert(id, time, col):
    try:
        if args.debug:
            log.debug('updating {} cache'.format(col))
        InsertQuery(cache, {
            cache.id: id,
            col: time
        }).execute()
    except IntegrityError:
        cache.update(**{col: time}).where(cache.id == id).execute()
        db.close()


def clear_cache():
    cache.delete().where((cache.despawn <= now )|(cache.raid_end <= now))\
        .execute()


########################################################
# Registration commands
########################################################

# See if user is registered (true|false)


def registered(self):
    return (humans
            .select()
            .where(humans.id == self).exists())


# See if user is registered by name


def registered_by_name(self):
    return (humans
            .select()
            .where(humans.name == self).exists())


# Register human


def register(id, name):
    InsertQuery(humans, {
        humans.id: id,
        humans.name: name}).execute()
    db.close()


def unregister(id):
    humans.delete().where(humans.id == id).execute()
    monsters.delete().where(monsters.human_id == id).execute()
    raid.delete().where(raid.human_id == id).execute()
    db.close()


# Activate alarms


def activate(discordid):
    humans.update(enabled=1).where(humans.id == discordid).execute()
    db.close()


def deactivate(discordid):
    humans.update(enabled=0).where(humans.id == discordid).execute()
    db.close()


def set_location(name, lat, lon):
    humans.update(
        latitude=lat,
        longitude=lon).where(
        humans.name == name).execute()
    db.close()


########################################################
# Tracking commands
########################################################
# Monsters:


def get_mon_tracked(discordid):
    return monsters.select().where(monsters.human_id == discordid).order_by(
        monsters.pokemon_id.asc()).dicts()

def get_raid_tracked(discordid):
    return raid.select().where((raid.human_id == discordid) &
                    (raid.egg == 0)).order_by(raid.pokemon_id.asc()).dicts()

def get_egg_tracked(discordid):
    return raid.select().where((raid.human_id == discordid) &
                               (raid.egg == 1)).dicts()

def get_human_location(discordid):
    return humans.select().where(humans.id == discordid).dicts()

def check_if_tracked(discordid, monster):
    return monsters.select().where(
        (monsters.human_id == discordid) & (
            monsters.pokemon_id == monster)).exists()


def check_if_location_set(discordid):
    return humans.select().where((humans.id == discordid) &
                                 humans.latitude.is_null()).exists()


def add_tracking(id, monster, distance, iv):
    InsertQuery(monsters, {
        monsters.human_id: id,
        monsters.pokemon_id: monster,
        monsters.distance: distance,
        monsters.min_iv: iv
        }).execute()
    db.close()


def update_tracking(id, monster, distance, iv):
    monsters.update(
        distance=distance, min_iv=iv).where(
        (monsters.human_id == id) & (
            monsters.pokemon_id == monster)).execute()
    db.close()


def remove_tracking(id, monster):
    monsters.delete().where(
        (monsters.human_id == id) & (
            monsters.pokemon_id == monster)).execute()
    db.close()


def monster_any(id):
    return monsters.select().where(monsters.pokemon_id == id).exists()


# Raids


def raid_any(id, egg):
    return raid.select().where((raid.pokemon_id == id) & (raid.egg == egg)) \
        .exists()


def add_raid_tracking(id, monster, distance):
    InsertQuery(raid, {
        raid.human_id: id,
        raid.pokemon_id: monster,
        raid.egg: 0,
        raid.distance: distance}).execute()
    db.close()


def update_raid_tracking(id, monster, distance):
    raid.update(
        distance=distance).where(
        (raid.pokemon_id == monster) & (
            raid.human_id == id)).where(
        raid.egg == 0).execute()
    db.close()


def remove_raid_tracking(id, monster):
    raid.delete().where(
        (raid.human_id == id) & (
            raid.pokemon_id == monster)).where(
        raid.egg == 0).execute()
    db.close()


def check_if_raid_tracked(discordid, monster):
    return raid.select().where(
        (raid.human_id == discordid) & (raid.pokemon_id == monster)).where(
        raid.egg == 0).exists()
    # Eggs


def check_if_egg_tracked(discordid, monster):
    return raid.select().where(
        (raid.human_id == discordid) & (
            raid.pokemon_id == monster)).where(
        raid.egg == 1).exists()


def add_egg_tracking(id, monster, distance):
    InsertQuery(raid, {
        raid.human_id: id,
        raid.pokemon_id: monster,
        raid.egg: 1,
        raid.distance: distance}).execute()
    db.close()


def update_egg_tracking(id, monster, distance):
    raid.update(
        distance=distance).where(
        (raid.pokemon_id == monster) & (
            raid.human_id == id)).where(
        raid.egg == 1).execute()
    db.close()


def remove_egg_tracking(id, monster):
    raid.delete().where(
        (raid.human_id == id) & (
            raid.pokemon_id == monster)).where(
        raid.egg == 1).execute()
    db.close()

    # add tracking counter to human


def add_alarm_counter(id):
    for human in humans.select().where(humans.id == id):
        human.alerts_sent += 1
        human.save()


def switch(id, col):
    q = humans.get(humans.id == id)
    if getattr(q, col):
        humans.update(**{col: 0}).where(id == id).execute()
        return False
    else:
        humans.update(**{col: 1}).where(id == id).execute()
        return True


########################################################
# geocoding
########################################################


def check_if_geocoded(id):
    return geocoded.select().where(geocoded.id == id).exists()


def check_if_weather(id):
    return geocoded.select(geocoded.weather_path).where(
        (geocoded.id == id) & geocoded.weather_path.is_null(False)).exists()


def update_weather_path(id, path):
    geocoded.update(weather_path=path).where(geocoded.id == id).execute()
    try:
        InsertQuery(weather, {
            weather.area: path,
            weather.updated: 0
        }).execute()
    except IntegrityError:
        if args.debug:
            log.debug('tried to update weather where it already exists')
    db.close()


def get_weather_path(id):
    return geocoded.select(
        geocoded.weather_path).where(
        geocoded.id == id).dicts()

def get_all_weather_paths():
    paths = geocoded.select(geocoded.weather_path,
                           geocoded.latitude,
                           geocoded.longitude).where(geocoded.weather_path.is_null(False)).distinct(geocoded.weather_path)
    return paths.dicts()

def get_weather(area):
    return weather.select().where(weather.area == area).dicts()[0]


def get_weather_updated(area):
    return weather.select(weather.updated).where(
        weather.area == area).dicts()[0]['updated']


def get_address(id):
    return geocoded.select(geocoded.address).where(geocoded.id == id).dicts()


def get_geocoded(id):
    return geocoded.select().where(geocoded.id == id).dicts()[0]


def save_geocoding(id, team, address, gym_name, description, url, lat, lon):
    InsertQuery(geocoded, {
        geocoded.id: id,
        geocoded.type: 'raid',
        geocoded.team: team,
        geocoded.address: address,
        geocoded.gym_name: gym_name,
        geocoded.description: description,
        geocoded.url: url,
        geocoded.latitude: lat,
        geocoded.longitude: lon
    }).execute()
    db.close()


def spawn_geocoding(id, addr, lat, lon):
    InsertQuery(geocoded, {
        geocoded.id: id,
        geocoded.type: 'spawn',
        geocoded.address: addr,
        geocoded.latitude: lat,
        geocoded.longitude: lon
    }).execute()
    db.close()


def update_team(id, team):
    geocoded.update(team=team).where(geocoded.id == id).execute()
    db.close()


def update_weather(area, desc, wind, temp):
    weather.update(
        description=desc,
        windspeed=wind,
        temperature=temp,
        updated=now).where(
        weather.area == area).execute()
    db.close()


########################################################
# Alarm filter
########################################################


def who_cares(type, data, iv):
    if type == 'monster':
        monster_id = data['pokemon_id']
        return humans.select(
            humans.id,
            humans.name,
            humans.map_enabled,
            humans.address_enabled,
            humans.iv_enabled,
            humans.moves_enabled,
            humans.weather_enabled,
            monsters.distance,
            monsters.min_iv,
            humans.latitude,
            humans.longitude).join(
            monsters,
            on=(
                humans.id == monsters.human_id)).where(
            humans.id == monsters.human_id,
            humans.enabled == 1,
            monsters.pokemon_id == monster_id,
            monsters.min_iv <= iv).dicts()

    elif type == 'raid':
        if data['pokemon_id'] is not None:
            return humans.select(
                humans.id,
                humans.name,
                raid.distance,
                raid.pokemon_id,
                humans.map_enabled,
                humans.address_enabled,
                humans.iv_enabled,
                humans.moves_enabled,
                humans.weather_enabled,
                humans.latitude,
                humans.longitude).join(
                raid,
                on=(
                    humans.id == raid.human_id)).where(
                humans.id == raid.human_id,
                humans.enabled == 1,
                raid.pokemon_id == data['pokemon_id'],
                raid.egg == 0).dicts()

        else:
            return humans.select(
                humans.id,
                humans.name,
                raid.distance,
                raid.pokemon_id,
                humans.map_enabled,
                humans.address_enabled,
                humans.iv_enabled,
                humans.moves_enabled,
                humans.weather_enabled,
                humans.latitude,
                humans.longitude).join(
                raid,
                on=(
                    humans.id == raid.human_id)).where(
                humans.id == raid.human_id,
                humans.enabled == 1,
                raid.pokemon_id == data['level'],
                raid.egg == 1).dicts()
