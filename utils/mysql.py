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
from flask import Flask
from playhouse.flask_utils import FlaskDB
from playhouse.pool import PooledMySQLDatabase
from playhouse.shortcuts import RetryOperationalError, case
from playhouse.migrate import migrate, MySQLMigrator
from playhouse.flask_utils import FlaskDB

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
args = get_args(os.path.abspath(os.path.dirname(__file__)))
# Test Db Connection


db = MySQLDatabase(host="{}".format(
            args.dbhost), port=int("{}".format(
            args.dbport)), user="{}".format(
            args.user), passwd="{}".format(
            args.password), database='{}'.format(args.database),
            connect_timeout=10)


########################################################
## Table modesl begin
########################################################

class BaseModel(Model):
    class Meta:
        database = db

class Utf8mb4CharField(CharField):
    def __init__(self, max_length=191, *args, **kwargs):
        self.max_length = max_length
        super(CharField, self).__init__(*args, **kwargs)

class humans(BaseModel):
    id = SmallIntegerField(index=True, unique=True)
    name = Utf8mb4CharField(index=True, max_length=50)
    enabled = BooleanField()
    latitude = DoubleField()
    longitude = DoubleField()

    class Meta:
        indexes = ((('latitude', 'longitude'), False),)


class monsters(BaseModel):
    id = SmallIntegerField(index=True)
    pokemon_id = SmallIntegerField(index=True)
    distance = SmallIntegerField(index=True)
    min_iv = SmallIntegerField(index=True)
    latitude = DoubleField()
    longitude = DoubleField()

    class Meta:
        indexes = ((('latitude', 'longitude'), False),)



class raid(BaseModel):
    discord_id = SmallIntegerField(index=True)
    pokemon_id = SmallIntegerField(index=True)
    distance = SmallIntegerField(index=True)
    min_iv = SmallIntegerField(index=True)
    latitude = DoubleField()
    longitude = DoubleField()



class geocoded(BaseModel):
    id = Utf8mb4CharField(index=True, max_length=20,  unique=True)
    type = Utf8mb4CharField(index=True, max_length=20)
    adress = Utf8mb4CharField(index=True)
    distance = SmallIntegerField(index=True)
    description = TextField(null=True, default="")
    url = Utf8mb4CharField()
    latitude = DoubleField()
    longitude = DoubleField()

    class Meta:
        indexes = ((('latitude', 'longitude'), False),)

class schema_version(BaseModel):
    key = Utf8mb4CharField()
    val = SmallIntegerField()

    class Meta:
        primary_key = False

########################################################
## END OF TABLES
########################################################


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


## Functions

def registered(id):
    return (humans.select()
            .where(humans.id == id))






