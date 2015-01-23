# -*- coding: utf-8 -*-
from __future__ import absolute_import
import unittest
from mock import Mock, call
from email.message import Message
from string import Template

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
        messages = Messages(collection=None, template=Template(''))
        msg = messages.create_message({})
        self.assertIsInstance(msg, Message)

    def testCreateMessageUsesTemplate(self):
        messages = Messages(collection=None,
                            template=Template(u'${author}: ${downloads}'))
        msg = messages.create_message(
            {'author': u'Guðrún Ósvífursdóttir', 'downloads': 1})
        self.assertEqual(msg.get_payload(),
                         u'Guðrún Ósvífursdóttir: 1'.encode('utf-8'))

    def testMessagesIteratesOverMessages(self):
        mock_coll = Mock()
        mock_coll.find.return_value = [1]
        messages = Messages(collection=mock_coll, template=Template(''))
        messages.create_message = Mock(return_value=23)
        msg = next(iter(messages))
        self.assertEqual(msg, 23)
