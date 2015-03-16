# -*- coding: utf-8 -*-
from __future__ import absolute_import
from email.message import Message
from email.utils import formataddr
from datetime import datetime
import itertools
import logging


logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())


def messages(collection, builder, addresser, threshold, sender):
    with addresser as svc:
        for item in collection.find({'type': 'author'}):
            try:
                first_name, last_name, email = svc.lookup(item['_id']['mitid'])
            except TypeError:
                logger.info('Author not found: %s (%s)' %
                    (item['_id']['name'], item['_id']['mitid']))
                continue
            name = "%s %s" % (first_name, last_name)
            item['_id']['name'] = name
            msg = builder.build(item, threshold)
            if msg is not False:
                msg['To'] = formataddr((name, email))
                msg['From'] = sender
                msg['Subject'] = u'Open Access Statistics'
                yield msg


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


class MessageBuilder(object):
    """Builds email messages.

    :param template: a Python ``string.Template`` for message body
    :param start_date: ``datetime.datetime`` object for filtering download count
    :param end_date: ``datetime.datetime`` object for filtering download count
    """

    def __init__(self, template, start_date, end_date):
        self.template = template
        self.start_date = start_date
        self.end_date = end_date

    def build(self, item, threshold):
        msg_dict = self.process_item(item)
        if msg_dict['downloads'] < threshold:
            return False
        return self.create_message(self.process_item(item))

    def process_item(self, item):
        """Creates a dictionary containing total downloads for an author.

        Downloads are only counted if the date falls within the configured
        date range.
        """
        count = 0
        for date in itertools.ifilter(self.date_filter, item['dates']):
            count = count + date['downloads']
        countries = 0
        for country in item['countries']:
            if country['downloads'] > 0:
                countries = countries + 1
        msg_dict = {
            'author': item['_id']['name'],
            'downloads': count,
            'articles': item['size'],
            'countries': countries
        }
        return msg_dict

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
