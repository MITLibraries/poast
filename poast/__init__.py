# -*- coding: utf-8 -*-
from __future__ import absolute_import
import io
import string
import pymongo
from datetime import datetime
import click

from .mail import messages, MessageBuilder
from .config import Config


def message_queue(start_date, end_date, cfg=Config()):
    collection = mongo_collection(cfg['MONGO_DBURI'], cfg['MONGO_DATABASE'],
                                  cfg['MONGO_COLLECTION'])
    with io.open(cfg['EMAIL_TEMPLATE']) as fp:
        template = string.Template(fp.read())

    builder = MessageBuilder(template, start_date, end_date)
    msgs = messages(collection, builder, address_service(cfg),
                    cfg['DOWNLOAD_THRESHOLD'], cfg['EMAIL_SENDER'])
    return msgs


def mongo_collection(dburi, database, collection):
    client = pymongo.MongoClient(dburi)
    return client[database][collection]


def address_service(cfg):
    from .addresses import AddressService
    user = cfg['ORACLE_USER']
    password = cfg['ORACLE_PASSWORD']
    sid = cfg['ORACLE_SID']
    host = cfg['ORACLE_HOST']
    port = cfg['ORACLE_PORT']
    return AddressService(user, password, sid, host, port)


class DateParamType(click.ParamType):
    name = 'date'

    def convert(self, value, param, ctx):
        try:
            return datetime.strptime(value, '%Y-%m-%d')
        except ValueError:
            self.fail('%s is not a valid date string' % value, param, ctx)


DATE_TYPE = DateParamType()
