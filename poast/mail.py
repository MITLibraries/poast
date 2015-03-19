# -*- coding: utf-8 -*-
from __future__ import absolute_import
from email.message import Message
import logging
from functools import partial
try:
    from itertools import ifilter
except ImportError:
    ifilter = filter


logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())


def threshold_filter(item, threshold):
    return item['downloads'] - item['size'] >= threshold


def create_message(sender, subject, context, template):
    msg = Message()
    msg['To'] = context['email']
    msg['From'] = sender
    msg['Subject'] = subject
    msg['Content-Transfer-Encoding'] = 'Quoted-Printable'
    msg.set_payload(template.substitute(context), 'utf-8')
    return msg


def authors(collection, addresser, threshold):
    t_filter = partial(threshold_filter, threshold=threshold)
    with addresser as svc:
        for item in ifilter(t_filter, collection.find({'type': 'author'})):
            try:
                first_name, last_name, email = svc.lookup(item['_id']['mitid'])
            except TypeError:
                logger.info('Author not found: %s (%s)' %
                    (item['_id']['name'], item['_id']['mitid']))
                continue
            countries = [x['downloads'] for x in item['countries']]
            yield {
                'author': u"%s %s" % (first_name, last_name),
                'email': email,
                'downloads': item['downloads'],
                'articles': item['size'],
                'countries': len(list(filter(None, countries)))
            }
