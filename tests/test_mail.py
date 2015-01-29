# -*- coding: utf-8 -*-
from __future__ import absolute_import
import unittest
from mock import Mock, call
from email.message import Message
from string import Template
from datetime import datetime

from poast.mail import Mailer, Messages


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


class MessagesTestCase(unittest.TestCase):
    def testCreateMessageReturnsMessage(self):
        messages = Messages(collection=None, template=Template(''),
                            start_date=None, end_date=None)
        msg = messages.create_message({})
        self.assertIsInstance(msg, Message)

    def testCreateMessageUsesTemplate(self):
        messages = Messages(collection=None,
                            template=Template(u'${author}: ${downloads}'),
                            start_date=None, end_date=None)
        msg = messages.create_message(
            {'author': u'Guðrún Ósvífursdóttir', 'downloads': 1})
        self.assertEqual(msg.get_payload(),
                         u'Guðrún Ósvífursdóttir: 1'.encode('utf-8'))

    def testMessagesIteratesOverMessages(self):
        mock_coll = Mock()
        mock_coll.find.return_value = [1]
        messages = Messages(collection=mock_coll, template=Template(''),
                            start_date=None, end_date=None)
        messages.process_item = Mock()
        messages.create_message = Mock(return_value=23)
        msg = next(iter(messages))
        self.assertEqual(msg, 23)

    def testDateFilterFiltersByDate(self):
        messages = Messages(None, None, datetime(2014, 1, 1),
                            datetime(2014, 1, 2))
        self.assertTrue(messages.date_filter(
            {'date': '2014-01-01', 'downloads': 1}))
        self.assertFalse(messages.date_filter(
            {'date': '2014-01-03', 'downloads': 1}))

    def testDateFilterFiltersByDownloads(self):
        messages = Messages(None, None, datetime(2014, 1, 1),
                            datetime(2014, 1, 2))
        self.assertTrue(messages.date_filter(
            {'date': '2014-01-01', 'downloads': 1}))
        self.assertFalse(messages.date_filter(
            {'date': '2014-01-01', 'downloads': 0}))

    def testProcessItemReturnsProcessedDictionary(self):
        messages = Messages(collection=None, template=None,
                            start_date=datetime(2014, 1, 1),
                            end_date=datetime(2014, 1, 2))
        item = {
            "_id": {
                "name": u"Foobar"
            },
            "dates": [
                {"downloads": 1, "date": "2014-01-01"},
                {"downloads": 2, "date": "2014-01-02"}
            ]
        }
        self.assertEqual(messages.process_item(item),
                         {'author': u'Foobar', 'downloads': 3})
