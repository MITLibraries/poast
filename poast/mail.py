# -*- coding: utf-8 -*-
from __future__ import absolute_import
from email.message import Message
import logging
from functools import partial
try:
    from itertools import ifilter
except ImportError:
    ifilter = filter


def threshold_filter(item, threshold):
    return item['downloads'] - item['size'] >= threshold


def country_filter(item):
    return item['downloads'] > 0


def create_message(sender, subject, context, template):
    msg = Message()
    msg['To'] = context['email']
    msg['From'] = sender
    msg['Subject'] = subject
    msg['Content-Transfer-Encoding'] = 'Quoted-Printable'
    msg.set_payload(template.render(context), 'utf-8')
    return msg


def authors(collection, addresser, threshold):
    logger = logging.getLogger(__name__)
    t_filter = partial(threshold_filter, threshold=threshold)
    totals = global_context(collection)
    emails = []
    for item in ifilter(t_filter, collection.find({'type': 'author'})):
        try:
            first_name, last_name, email = \
                addresser.lookup(item['_id']['mitid'])
        except TypeError:
            logger.warning('Author not found: %s (%s)' %
                           (item['_id']['name'], item['_id']['mitid']))
            continue
        if not email:
            logger.warning('Author missing email: %s (%s)' %
                           (item['_id']['name'], item['_id']['mitid']))
            continue
        if email in emails:
            logger.warning('Duplicate email: %s' % (email,))
            continue
        emails.append(email)
        countries = [x['downloads'] for x in item['countries']]
        yield {
            'author': u"%s %s" % (first_name, last_name),
            'email': email,
            'downloads': item['downloads'],
            'articles': item['size'],
            'countries': len(list(filter(None, countries))),
            'total_size': totals['size'],
            'total_countries': totals['countries'],
        }


def pluralize(count, single, plural):
    if count > 1:
        return plural
    else:
        return single


def format_num(number):
    chars = []
    for i, n in enumerate(str(number)[::-1]):
        if i and not (i % 3):
            chars.insert(0, ',')
        chars.insert(0, n)
    return ''.join(chars)


def global_context(collection):
    summary = collection.find_one({'type': 'overall'},
                                  {'size': 1, 'countries': 1})
    countries = ifilter(country_filter, summary['countries'])
    return {'size': summary['size'], 'countries': len(list(countries))}
