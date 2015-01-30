# -*- coding: utf-8 -*-
from __future__ import absolute_import
import unittest
from mock import Mock, call
from string import Template
from datetime import datetime

from poast.mail import Mailer, MessageBuilder


class MailerTestCase(unittest.TestCase):
    def testQueueMessagesAddsMessageToQueue(self):
        mailer = Mailer(queue=[], messages=[1,2], sender=None)
        mailer.queue_messages()
        self.assertEqual(mailer.queue, [1, 2])

    def testSendMessagesMailsEachMessage(self):
        mock_mailer = Mock()
        mailer = Mailer(queue=[1,2], messages=None, sender=mock_mailer)
        mailer.send_messages()
        mock_mailer.mail.assert_has_calls([call(1), call(2)])


class MessageBuilderTestCase(unittest.TestCase):
    def setUp(self):
        self.builder = MessageBuilder(Template(u'${author}: ${downloads}'),
                                      datetime(2014, 1, 1),
                                      datetime(2014, 1, 2))

    def testCreateMessageReturnsMessage(self):
        msg = self.builder.create_message({
            'author': u'Guðrún Ósvífursdóttir', 'downloads': 1
        })
        self.assertEqual(msg.get_payload(),
                         u'Guðrún Ósvífursdóttir: 1'.encode('utf-8'))

    def testDateFilterFiltersByDate(self):
        self.assertTrue(self.builder.date_filter(
            {'date': '2014-01-01', 'downloads': 1}))
        self.assertFalse(self.builder.date_filter(
            {'date': '2014-01-03', 'downloads': 1}))

    def testDateFilterFiltersByDownloads(self):
        self.assertTrue(self.builder.date_filter(
            {'date': '2014-01-01', 'downloads': 1}))
        self.assertFalse(self.builder.date_filter(
            {'date': '2014-01-01', 'downloads': 0}))

    def testProcessItemReturnsProcessedDictionary(self):
        item = {
            "_id": {
                "name": u"Foobar"
            },
            "dates": [
                {"downloads": 1, "date": "2014-01-01"},
                {"downloads": 2, "date": "2014-01-02"}
            ]
        }
        self.assertEqual(self.builder.process_item(item),
                         {'author': u'Foobar', 'downloads': 3})
