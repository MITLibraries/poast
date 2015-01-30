# -*- coding: utf-8 -*-
from __future__ import absolute_import
import codecs
import string
import pymongo
from datetime import datetime
import click

from .mail import Mailer, messages, MessageBuilder


def create_mailer(start_date, end_date, conf_obj=None):
    config = conf_obj
    if config is None:
        from .config import Config
        config = Config

    collection = mongo_collection(config.MONGO_DBURI, config.MONGO_DATABASE,
                                  config.MONGO_COLLECTION)
    with codecs.open(config.EMAIL_TEMPLATE) as fp:
        template = string.Template(fp.read())

    builder = MessageBuilder(template, start_date, end_date)
    msgs = messages(collection, builder, address_service(config))
    return Mailer(queue=[], messages=msgs, sender=None)


def mongo_collection(dburi, database, collection):
    client = pymongo.MongoClient(dburi)
    return client[database][collection]


def address_service(cfg):
    from .addresses import AddressService
    user = cfg.get('ORACLE_USER')
    password = cfg.get('ORACLE_PASSWORD')
    sid = cfg.get('ORACLE_SID')
    host = cfg.get('ORACLE_HOST')
    port = cfg.get('ORACLE_PORT')
    return AddressService(user, password, sid, host, port)


class DateParamType(click.ParamType):
    name = 'date'

    def convert(self, value, param, ctx):
        try:
            return datetime.strptime(value, '%Y-%m-%d')
        except ValueError:
            self.fail('%s is not a valid date string' % value, param, ctx)


DATE_TYPE = DateParamType()
