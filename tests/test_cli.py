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


def test_mail_sends_messages(runner, smtp_server):
    emails = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                          'fixtures/emails/')
    runner.invoke(main, ['mail', emails, '--yes', '--username', 'foo',
                         '--password', 'bar', '--smtp-port', smtp_server._port,
                         '--no-ssl'])
    with io.open(os.path.join(emails, 'foo')) as fp:
        foobar = message_from_file(fp)
    rcvd = message_from_string(smtp_server.received['foobar@example.com'])
    assert rcvd.get_payload() == foobar.get_payload()

    with io.open(os.path.join(emails, 'thor')) as fp:
        thor = message_from_file(fp)
    rcvd = message_from_string(smtp_server.received['thor@example.com'])
    assert rcvd.get_payload() == thor.get_payload().strip()
