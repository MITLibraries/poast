# -*- coding: utf-8 -*-
from __future__ import absolute_import

import asyncore
import io
import json
import os
import shutil
import smtpd
import tempfile
import threading

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
    client.oastats.optout.drop()


@pytest.yield_fixture
def tmp_dir():
    path = tempfile.mkdtemp()
    yield path
    shutil.rmtree(path)


@pytest.yield_fixture
def smtp_server():
    server = TestSMTPServer(('localhost', 0))
    server.start()
    yield server
    server.close()


class TestSMTPServer(smtpd.SMTPServer):
    def __init__(self, localaddr):
        self.received = {}
        smtpd.SMTPServer.__init__(self, localaddr, None)
        self._port = self.socket.getsockname()[1]

    def process_message(self, peer, mailfrom, rcpttos, data):
        self.received[rcpttos[0]] = data

    def start(self):
        self.thread = threading.Thread(target=asyncore.loop,
                                       kwargs={'timeout': 0.1})
        self.thread.start()

    def close(self):
        smtpd.SMTPServer.close(self)
        self.thread.join()
