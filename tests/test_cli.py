# -*- coding: utf-8 -*-
from __future__ import absolute_import

import io
import os
from email import message_from_file, message_from_string

from click.testing import CliRunner
import pytest

from poast.cli import main


pytestmark = pytest.mark.usefixtures("mongo")


@pytest.fixture
def runner():
    return CliRunner()


def test_queue_writes_messages_to_directory(runner, tmp_dir, mongo_db):
    runner.invoke(main, ['queue', tmp_dir, '--mongo',
                  'mongodb://localhost:%d' % mongo_db.port])
    msgs = os.listdir(tmp_dir)
    assert len(msgs) == 1
    with io.open(os.path.join(tmp_dir, msgs[0])) as fp:
        msg = message_from_file(fp)
    assert msg['To'] == 'thor@example.com'
