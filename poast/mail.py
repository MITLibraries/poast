# -*- coding: utf-8 -*-
from __future__ import absolute_import
from email.message import Message
from datetime import datetime
import itertools


class Mailer(object):
    """Creates a mailer that can queue and send messages.

    The message generator should yield ``email.message.Message``s. A queue
    can simply be a list or something more complicated that responds to
    ``append()`` and iterates.

    :param queue: outgoing message queue
    :param messages: message generator
    :param sender: mail sender
    """

    def __init__(self, queue, messages=None, sender=None):
        self.messages = messages
        self.queue = queue
        self.sender = sender

    def queue_messages(self):
        for message in self.messages:
            self.queue.append(message)
        return self

    def send_messages(self):
        for message in self.queue:
            self.sender.mail(message)


class Messages(object):
    """Generates email messages from a MongoDB collection.

    :param collection: mongo collection
    :param template: a Python ``string.Template`` for message body
    :param start_date: ``datetime.datetime`` object for filtering messages
    :param end_date: ``datetime.datetime`` object for filtering messages
    """

    def __init__(self, collection, template, start_date, end_date):
        self.collection = collection
        self.template = template
        self.start_date = start_date
        self.end_date = end_date

    def __iter__(self):
        for item in self.collection.find({'type': 'author'}):
            message_dict = self.process_item(item)
            yield self.create_message(message_dict)

    def process_item(self, item):
        """Creates a dictionary containing total downloads for an author.

        Downloads are only counted if the date falls within the configured
        date range.
        """
        count = 0
        for date in itertools.ifilter(self.date_filter, item['dates']):
            count = count + date['downloads']
        return {'author': item['_id']['name'], 'downloads': count}

    def create_message(self, msg_dict):
        msg = Message()
        msg['Content-Transfer-Encoding'] = 'Quoted-Printable'
        msg.set_payload(self.template.substitute(msg_dict), 'utf-8')
        return msg

    def date_filter(self, date):
        """Filter for individual date/download count dictionary."""
        if date['downloads'] <= 0:
            return False
        dt = datetime.strptime(date['date'], '%Y-%m-%d')
        return dt <= self.end_date and dt >= self.start_date
