#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import sys
from args import args as get_args
import logging
import pymysql
from . import config
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

args = get_args(os.path.abspath(os.path.dirname(__file__)))
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

class Utf8mb4CharField(CharField):
    def __init__(self, max_length=191, *args, **kwargs):
        self.max_length = max_length
        super(CharField, self).__init__(*args, **kwargs)

class humans(BaseModel):
    id = Utf8mb4CharField(index=True, unique=True, max_length=20)
    name = Utf8mb4CharField(index=True, max_length=50)
    enabled = BooleanField(default=False)
    latitude = DoubleField(null=True)
    longitude = DoubleField(null=True)

    class Meta:
        indexes = ((('latitude', 'longitude'), False),)


class monsters(BaseModel):
    id = Utf8mb4CharField(index=True, max_length=20)
    pokemon_id = SmallIntegerField(index=True)
    distance = SmallIntegerField(index=True)
    min_iv = SmallIntegerField(index=True)

class raid(BaseModel):
    id = Utf8mb4CharField(index=True, max_length=20)
    pokemon_id = SmallIntegerField(index=True)
    distance = SmallIntegerField(index=True)

class geocoded(BaseModel):
    id = Utf8mb4CharField(index=True, max_length=50,  unique=True)
    type = Utf8mb4CharField(index=True, max_length=20)
    team = SmallIntegerField()
    address = Utf8mb4CharField(index=True)
    gym_name = Utf8mb4CharField(index=True, max_length=50)
    description = TextField(null=True, default="")
    url = Utf8mb4CharField(null=True)
    latitude = DoubleField(null=True)
    longitude = DoubleField(null=True)

    class Meta:
        indexes = ((('latitude', 'longitude'), False),)

class schema_version(BaseModel):
    key = Utf8mb4CharField()
    val = SmallIntegerField()

    class Meta:
        primary_key = False

## Db Migration

def create_tables():
    db.create_tables([humans, monsters, raid, geocoded, schema_version])

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
    monsters.delete().where(monsters.id == id).execute()
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
    return monsters.select().where(monsters.id == discordid).where(monsters.pokemon_id == monster).exists()

def add_tracking(id,monster,distance,iv):
    InsertQuery(monsters,{
        monsters.id: id,
        monsters.pokemon_id:monster,
        monsters.distance:distance,
        monsters.min_iv:iv}).execute()
    db.close()

def update_tracking(id,monster,distance,iv):
    monsters.update(distance=distance, min_iv=iv).where(monsters.id == id).where(monsters.pokemon_id == monster).execute()
    db.close()

def remove_tracking(id,monster):
    monsters.delete().where(monsters.id == id).where(monsters.pokemon_id == monster).execute()
    db.close()

## Raids
def check_if_raid_tracked(discordid,monster):
    return raid.select().where(raid.id == discordid).where(raid.pokemon_id == monster).exists()

def add_raid_tracking(id,monster,distance):
    InsertQuery(raid,{
        raid.id: id,
        raid.pokemon_id:monster,
        raid.distance:distance}).execute()
    db.close()

def update_raid_tracking(id,monster,distance):
    raid.update(distance=distance).where(raid.pokemon_id == monster).where(raid.id == id).execute()
    db.close()

def remove_raid_tracking(id,monster):
    monsters.delete().where(raid.id == id).where(raid.pokemon_id == monster).execute()
    db.close()

########################################################
## geocoding commands
########################################################

def check_if_geocoded(id):
    return geocoded.select().where(geocoded.id == id).exists()

def save_geocoding(id,type,team,address,gym_name,description,url,lat,lon):
    InsertQuery(geocoded,{
        geocoded.id: id,
        geocoded.type: type,
        geocoded.team: team,
        geocoded.address: address,
        geocoded.gym_name: gym_name,
        geocoded.description: description,
        geocoded.url: url,
        geocoded.latitude: lat,
        geocoded.longitude: lon
        }).execute()
    db.close()

def update_team(id,team):
    geocoded.update(team=team).where(id == id).execute()
    db.close()
