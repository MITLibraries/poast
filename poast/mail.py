# -*- coding: utf-8 -*-
from __future__ import absolute_import

import io
import logging
import os
from email import message_from_file
from email.mime.text import MIMEText
from functools import partial

from jinja2 import Environment

from poast.db import AddressService

try:
    import itertools.ifilter as filter
except ImportError:
    pass


def messages(summary, sender, reply_to, subject, threshold):
    template = make_template(pluralize=pluralize, format_num=format_num)
    with AddressService() as addresser:
        for author in authors(summary, addresser, threshold):
            yield create_message(sender, subject, author, template)


def threshold_filter(item, threshold):
    return item['downloads'] - item['size'] >= threshold


def country_filter(item):
    return item['downloads'] > 0


def create_message(sender, subject, context, template):
    try:
        msg = MIMEText(template.render(context), 'plain', 'us-ascii')
    except UnicodeEncodeError:
        msg = MIMEText(template.render(context), 'plain', 'utf-8')
    msg['To'] = context['email']
    msg['From'] = sender
    msg['Subject'] = subject
    return msg


def authors(collection, addresser, threshold):
    logger = logging.getLogger(__name__)
    t_filter = partial(threshold_filter, threshold=threshold)
    totals = global_context(collection)
    emails = []
    for item in filter(t_filter, collection.find({'type': 'author'})):
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
    countries = filter(country_filter, summary['countries'])
    return {'size': summary['size'], 'countries': len(list(countries))}


def make_template(**kwargs):
    environment = Environment()
    environment.filters.update(kwargs)
    tmpl = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                        'message.tmpl')
    with io.open(tmpl) as fp:
        template = environment.from_string(fp.read())
    return template


def delivery_queue(path):
    for relpath, dirs, files in os.walk(path):
        for f in files:
            f_msg = os.path.join(relpath, f)
            with io.open(f_msg, encoding='us-ascii') as fp:
                yield message_from_file(fp)
