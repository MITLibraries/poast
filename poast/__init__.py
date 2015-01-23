# -*- coding: utf-8 -*-
from __future__ import absolute_import
import codecs
import string
import pymongo

from .mail import Mailer, Messages


def create_mailer(conf_obj=None):
    config = conf_obj
    if config is None:
        from .config import Config
        config = Config

    collection = mongo_collection(config.MONGO_DBURI, config.MONGO_DATABASE,
                                  config.MONGO_COLLECTION)
    with codecs.open(config.EMAIL_TEMPLATE) as fp:
        template = string.Template(fp.read())
    messages = Messages(collection, template)

    return Mailer(queue=[], messages=messages, sender=None)


def mongo_collection(dburi, database, collection):
    client = pymongo.MongoClient(dburi)
    return client[database][collection]
