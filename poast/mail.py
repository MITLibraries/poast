# -*- coding: utf-8 -*-
from __future__ import absolute_import
from email.message import Message


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
    """

    def __init__(self, collection, template):
        self.collection = collection
        self.template = template

    def __iter__(self):
        for item in self.collection.find():
            yield self.create_message(item)

    def create_message(self, msg_dict):
        msg = Message()
        msg['Content-Transfer-Encoding'] = 'Quoted-Printable'
        msg.set_payload(self.template.substitute(msg_dict), 'utf-8')
        return msg
