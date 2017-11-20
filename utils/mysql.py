#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
from args import args as get_args
import logging
import pymysql
from . import config
from peewee import (InsertQuery, Check, CompositeKey, ForeignKeyField,
                    SmallIntegerField, IntegerField, CharField, DoubleField,
                    BooleanField, DateTimeField, fn, DeleteQuery, FloatField,
                    TextField, JOIN, OperationalError)
from flask import Flask
from playhouse.flask_utils import FlaskDB
from playhouse.pool import PooledMySQLDatabase
from playhouse.shortcuts import RetryOperationalError, case
from playhouse.migrate import migrate, MySQLMigrator
from playhouse.flask_utils import FlaskDB


# Globals
app = Flask(__name__)
flaskDb = FlaskDB()
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

def connect_db():

    try:
        return pymysql.connect(host="{}".format(
            args.dbhost), port=int("{}".format(
            args.dbport)), user="{}".format(
            args.user), passwd="{}".format(
            args.password), database='{}'.format(args.database),
            connect_timeout=10)
    except pymysql.Error as e:
        log.critical("MySQL unhappy [ERROR]:% d: % s\n" % (e.args[0], e.args[1]))
        exit(1)
        return False

def check_db_version():

    log.info('Connecting to MySQL database on {}:{}'.format(args.dbhost,
                                                            args.dbport))
    humans(BaseModel)

## Db table Models


class Utf8mb4CharField(CharField):
    def __init__(self, max_length=191, *args, **kwargs):
        self.max_length = max_length
        super(CharField, self).__init__(*args, **kwargs)

class BaseModel(flaskDb.Model):

    @classmethod
    def database(cls):
        return cls._meta.database

    @classmethod
    def get_all(cls):
        return [m for m in cls.select().dicts()]

class LatLongModel(BaseModel):

    @classmethod
    def get_all(cls):
        results = [m for m in cls.select().dicts()]
        return results

class humans(LatLongModel):
    id = Utf8mb4CharField(primary_key=True, max_length=20)
    name = Utf8mb4CharField(index=True, max_length=50)
    enabled = BooleanField()
    latitude = DoubleField()
    longitude = DoubleField()
    class Meta:
        indexes = ((('latitude', 'longitude'), False),)

class pokemon(BaseModel):
    discord_id = Utf8mb4CharField(index=True, max_length=20)
    pokemon_id = SmallIntegerField(index=True)
    distance = SmallIntegerField(index=True)
    min_iv = SmallIntegerField(index=True)
    latitude = DoubleField()
    longitude = DoubleField()


    class Meta:
        indexes = ((('latitude', 'longitude'), False),)


class raid(BaseModel):
    discord_id = Utf8mb4CharField(index=True, max_length=20)
    pokemon_id = SmallIntegerField(index=True)
    distance = SmallIntegerField(index=True)
    min_iv = SmallIntegerField(index=True)
    latitude = DoubleField()
    longitude = DoubleField()

    class Meta:
        indexes = ((('latitude', 'longitude'), False),)


class geocoded(BaseModel):
    latitude = DoubleField()
    longitude = DoubleField()
    address = Utf8mb4CharField(index=True, max_length=50)
    raid = BooleanField()
    gym_id = Utf8mb4CharField(index=True, max_length=50)
    gym_name = Utf8mb4CharField(index=True, max_length=50)
    gym_description = Utf8mb4CharField()
    class Meta:
        indexes = ((('latitude', 'longitude'), False),)

class schema_version(BaseModel):
    key = Utf8mb4CharField()
    val = SmallIntegerField()

    class Meta:
        primary_key = False




