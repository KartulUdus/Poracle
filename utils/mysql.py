#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import sys
import math
from args import args as get_args
import logging
import pymysql
from peewee import (InsertQuery, Check, CompositeKey, ForeignKeyField,
                    SmallIntegerField, IntegerField, CharField, DoubleField,
                    BooleanField, DateTimeField, fn, DeleteQuery, FloatField,
                    TextField, JOIN, OperationalError)
from peewee import *


# Globals

#app = Flask(__name__)
sb_schema_version = 1

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
## Tables and MySQL migration
########################################################

class BaseModel(Model):
    class Meta:
        database = db

class humans(BaseModel):
    id = CharField(primary_key=True, index=True, unique=True)
    name = CharField(index=True, max_length=50)
    enabled = BooleanField(default=False)
    latitude = DoubleField(null=True)
    longitude = DoubleField(null=True)

    class Meta:
        indexes = ((('latitude', 'longitude'), False),)
        order_by = ('id',)


class monsters(BaseModel):
    human_id = CharField(index=True,  max_length=30)
    pokemon_id = SmallIntegerField(index=True)
    distance = IntegerField(index=True)
    min_iv = SmallIntegerField(index=True)

    class Meta:
        order_by = ('id',)


class raid(BaseModel):
    human_id = CharField(index=True,  max_length=30)
    pokemon_id = CharField(index=True, max_length=20)
    egg = BooleanField(default=False)
    distance = IntegerField(index=True)

    class Meta:
        order_by = ('id',)


class geocoded(BaseModel):
    id = CharField(primary_key=True, index=True, max_length=50)
    type = CharField(index=True, max_length=20)
    team = SmallIntegerField(null=True)
    address = CharField(index=True)
    gym_name = CharField(index=True, max_length=50,null=True)
    description = TextField(null=True, default="")
    url = CharField(null=True)
    latitude = DoubleField()
    longitude = DoubleField()

    class Meta:
        indexes = ((('latitude', 'longitude'), False),)
        order_by = ('id',)

class schema_version(BaseModel):
    key = CharField()
    val = SmallIntegerField()

    class Meta:
        primary_key = False

## Db Migration

def create_tables():
    db.create_tables([humans, monsters, raid, geocoded, schema_version], safe=True)

def verify_database_schema():

    log.info('Connecting to MySQL database on {}:{}'.format(args.dbhost,
                                                            args.dbport))
    try:

        if not schema_version.table_exists():
            create_tables()
            if humans.table_exists():
                InsertQuery(schema_version,{
                    schema_version.key: 'schema_version',
                    schema_version.val: 1}).execute()

    except OperationalError as e:
        log.critical("MySQL unhappy [ERROR]:% d: % s\n" % (
        e.args[0], e.args[1]))
        exit(1)

########################################################
## Registration commands
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
def register(id,name):
    InsertQuery(humans,{
        humans.id: id,
        humans.name: name}).execute()
    db.close()

def unregister(id):
    humans.delete().where(humans.id == id).execute()
    monsters.delete().where(monsters.human_id == id).execute()
    db.close()

# Activate alarms
def activate(discordid):
    humans.update(enabled=1).where(humans.id == discordid).execute()
    db.close()

def deactivate(discordid):
    humans.update(enabled=0).where(humans.id == discordid).execute()
    db.close()

def set_location(name, lat, lon):
    humans.update(latitude=lat, longitude=lon).where(humans.name == name).execute()
    db.close()

########################################################
## Tracking commands
########################################################
## Monsters:

def check_if_tracked(discordid,monster):
    return monsters.select().where((monsters.human_id == discordid) & (monsters.pokemon_id == monster)).exists()

def check_if_location_set(discordid):
    return humans.select().where((humans.id == discordid) & humans.latitude.is_null()).exists()

def add_tracking(id,monster,distance,iv):
    InsertQuery(monsters,{
        monsters.human_id: id,
        monsters.pokemon_id:monster,
        monsters.distance:distance,
        monsters.min_iv:iv}).execute()
    db.close()

def update_tracking(id,monster,distance,iv):
    monsters.update(distance=distance, min_iv=iv).where((monsters.human_id == id) & (monsters.pokemon_id == monster)).execute()
    db.close()

def remove_tracking(id,monster):
    monsters.delete().where((monsters.human_id == id)& (monsters.pokemon_id == monster)).execute()
    db.close()

def monster_any(id):
    return monsters.select().where(monsters.pokemon_id == id).exists()

## Raids

def check_if_raid_tracked(discordid,monster):
    return raid.select().where((raid.human_id == discordid)&(raid.pokemon_id == monster)).exists()

def add_raid_tracking(id,monster,distance):
    InsertQuery(raid,{
        raid.human_id: id,
        raid.pokemon_id:monster,
        raid.distance:distance}).execute()
    db.close()

def update_raid_tracking(id,monster,distance):
    raid.update(distance=distance).where((raid.pokemon_id == monster) & (raid.human_id == id)).execute()
    db.close()

def remove_raid_tracking(id,monster):
    monsters.delete().where((raid.human_id == id) & (raid.pokemon_id == monster)).execute()
    db.close()

########################################################
## geocoding
########################################################

def check_if_geocoded(id):
    return geocoded.select().where(geocoded.id == id).exists()

def save_geocoding(id,team,address,gym_name,description,url,lat,lon):
    InsertQuery(geocoded,{
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

def spawn_geocoding(id,addr,lat,lon):
    InsertQuery(geocoded,{
        geocoded.id: id,
        geocoded.type: 'spawn',
        geocoded.address: addr,
        geocoded.latitude: lat,
        geocoded.longitude: lon
        }).execute()
    db.close()

def update_team(id,team):
    geocoded.update(team=team).where(id == id).execute()
    db.close()

########################################################
## Alarm filter
########################################################


def who_cares(type, data, iv):

    if type == 'monster':
        monster_id = data['pokemon_id']
        return humans.select(humans.id, humans.name, monsters.distance, monsters.min_iv,
                             humans.latitude,humans.longitude)\
            .join(monsters, on=(humans.id == monsters.human_id))\
            .where(
                humans.id == monsters.human_id,
                humans.enabled == 1,
                monsters.pokemon_id == monster_id,
                monsters.min_iv <= iv).dicts()

    elif type == 'raid':
        if 'start' in data:
            level = data['level']
            return humans.select(humans.id, humans.name, raid.distance, raid.pokemon_id,
                                humans.latitude, humans.longitude) \
                .join(raid, on=(humans.id == raid.human_id)) \
                .where(
                humans.id == raid.human_id,
                humans.enabled == 1,
                raid.pokemon_id == level,
                raid.egg == 1).dicts()

        else:
            monster_id = data['pokemon_id']
            return humans.select(humans.id, humans.name, raid.distance, raid.pokemon_id,
                                humans.latitude, humans.longitude) \
                .join(raid, on=(humans.id == raid.human_id)) \
                .where(
                humans.id == raid.human_id,
                humans.enabled == 1,
                raid.pokemon_id == monster_id,
                raid.egg == 0).dicts()
