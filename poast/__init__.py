# -*- coding: utf-8 -*-
from __future__ import absolute_import
import codecs
import string
import pymongo
from datetime import datetime
import click

from .mail import Mailer, Messages


def create_mailer(start_date, end_date, conf_obj=None):
    config = conf_obj
    if config is None:
        from .config import Config
        config = Config

    collection = mongo_collection(config.MONGO_DBURI, config.MONGO_DATABASE,
                                  config.MONGO_COLLECTION)
    with codecs.open(config.EMAIL_TEMPLATE) as fp:
        template = string.Template(fp.read())

    messages = Messages(collection, template, start_date=start_date,
                        end_date=end_date)

    return Mailer(queue=[], messages=messages, sender=None)


def mongo_collection(dburi, database, collection):
    client = pymongo.MongoClient(dburi)
    return client[database][collection]


class DateParamType(click.ParamType):
    name = 'date'

    def convert(self, value, param, ctx):
        try:
            return datetime.strptime(value, '%Y-%m-%d')
        except ValueError:
            self.fail('%s is not a valid date string' % value, param, ctx)


DATE_TYPE = DateParamType()
