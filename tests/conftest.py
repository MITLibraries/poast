# -*- coding: utf-8 -*-
from __future__ import absolute_import

import asyncore
import io
import json
import os
import socket
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


@pytest.yield_fixture
def tmp_dir():
    path = tempfile.mkdtemp()
    yield path
    shutil.rmtree(path)


@pytest.yield_fixture
def smtp_server():
    port = _get_open_port()
    server = TestSMTPServer(('localhost', port))
    server.start()
    yield server
    server.close()


def _get_open_port(host="localhost"):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((host, 0))
    port = s.getsockname()[1]
    s.close()
    return port


class TestSMTPServer(smtpd.SMTPServer):
    def __init__(self, localaddr):
        self.received = []
        self._port = localaddr[1]
        smtpd.SMTPServer.__init__(self, localaddr, None)

    def process_message(self, peer, mailfrom, rcpttos, data):
        self.received.append(data)

    def start(self):
        self.thread = threading.Thread(target=asyncore.loop,
                                       kwargs={'timeout': 0.1})
        self.thread.start()

    def close(self):
        smtpd.SMTPServer.close(self)
        self.thread.join()
