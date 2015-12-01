# -*- coding: utf-8 -*-
from __future__ import absolute_import
import io
import json
import os

import pytest

from poast.addresses import engine, persons, metadata


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
