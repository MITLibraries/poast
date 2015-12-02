# -*- coding: utf-8 -*-
from __future__ import absolute_import

import pymongo
from sqlalchemy import Column, MetaData, String, Table, create_engine
from sqlalchemy.sql import bindparam, select

metadata = MetaData()

persons = Table('library_person_lookup', metadata,
                Column('mit_id', String),
                Column('first_name', String),
                Column('last_name', String),
                Column('email', String))


class Engine(object):
    _engine = None

    def __call__(self):
        return self._engine

    def configure(self, conn):
        self._engine = self._engine or create_engine(conn)


class AddressService(object):
    def __init__(self):
        self.conn = engine().connect()
        self.stmt = select([persons.c.first_name, persons.c.last_name,
                            persons.c.email]).\
            where(persons.c.mit_id == bindparam('mit_id'))

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.conn.close()

    def lookup(self, id):
        return self.conn.execute(self.stmt, mit_id=id).fetchone()


def collection(dburi, database, coll):
    client = pymongo.MongoClient(dburi)
    return client[database][coll]


engine = Engine()
