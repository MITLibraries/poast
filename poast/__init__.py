# -*- coding: utf-8 -*-
from __future__ import absolute_import
import io
import pymongo
import os
from email import message_from_string
from jinja2 import Environment

from .addresses import AddressService, engine
from .mail import create_message, authors, pluralize, format_num
from .config import Config

__version__ = '0.1.0'


def message_queue(cfg=Config()):
    collection = mongo_collection(cfg['MONGO_DBURI'], cfg['MONGO_DATABASE'],
                                  cfg['MONGO_COLLECTION'])
    engine.configure(cfg['SQLALCHEMY_DB_URI'])
    threshold = cfg['DOWNLOAD_THRESHOLD']
    environment = Environment()
    environment.filters['pluralize'] = pluralize
    environment.filters['format_num'] = format_num
    with io.open(cfg['EMAIL_TEMPLATE']) as fp:
        template = environment.from_string(fp.read())
    with AddressService() as addresser:
        for author in authors(collection, addresser, threshold):
            yield create_message(cfg['EMAIL_SENDER'], cfg['EMAIL_SUBJECT'],
                                 author, template)


def delivery_queue(path):
    for relpath, dirs, files in os.walk(path):
        for f in files:
            f_msg = os.path.join(relpath, f)
            with io.open(f_msg, encoding='utf-8') as fp:
                yield message_from_string(fp.read().encode('utf-8'))


def mongo_collection(dburi, database, collection):
    client = pymongo.MongoClient(dburi)
    return client[database][collection]
