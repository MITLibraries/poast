# -*- coding: utf-8 -*-

class Config(object):
    MONGO_DBURI = 'mongodb://localhost:27017'
    MONGO_DATABASE = 'oastats'
    MONGO_COLLECTION = 'summary'

    EMAIL_TEMPLATE = 'poast/message.tmpl'
