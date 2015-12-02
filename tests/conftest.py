# -*- coding: utf-8 -*-
from __future__ import absolute_import

import io
import json
import os
import shutil
import tempfile

from mongobox import MongoBox
from pymongo import MongoClient
import pytest

from poast.db import engine, metadata, persons


@pytest.fixture(scope="session", autouse=True)
def db():
    data = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                        'fixtures/people.json')
    with io.open(data, encoding="utf-8") as fp:
        people = json.load(fp)
    engine.configure('sqlite://')
    metadata.bind = engine()
    metadata.create_all()
    conn = engine().connect()
    conn.execute(persons.insert(), people)
    conn.close()


@pytest.yield_fixture(scope="session", autouse=True)
def mongo_db():
    with MongoBox() as mdb:
        yield mdb


@pytest.yield_fixture
def mongo(mongo_db):
    data = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                        'fixtures/mongo.json')
    with io.open(data, encoding="utf-8") as fp:
        people = json.load(fp)

    client = MongoClient('localhost', mongo_db.port)
    client.oastats.summary.insert_many(people)
    yield client
    client.oastats.summary.drop()


@pytest.yield_fixture
def tmp_dir():
    path = tempfile.mkdtemp()
    yield path
    shutil.rmtree(path)
