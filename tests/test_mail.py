# -*- coding: utf-8 -*-
from __future__ import absolute_import
import unittest

from jinja2 import Template

from poast.mail import (threshold_filter, country_filter, create_message,
                        authors, format_num, pluralize, global_context)
from poast.db import AddressService


class ThresholdFilterTestCase(unittest.TestCase):
    def testFilterReturnsFalseWhenBelowThreshold(self):
        self.assertFalse(threshold_filter({'downloads': 10, 'size': 6}, 5))

    def testFilterReturnsTrueWhenEqualToThreshold(self):
        self.assertTrue(threshold_filter({'downloads': 10, 'size': 5}, 5))

    def testFilterReturnTrueWhenAboveThreshold(self):
        self.assertTrue(threshold_filter({'downloads': 10, 'size': 4}, 5))


class CountryFilterTestCase(unittest.TestCase):
    def testFilterReturnsFalseWhenCountryHasNoDownloads(self):
        self.assertFalse(country_filter({'country': 'FIN', 'downloads': 0}))

    def testFilterReturnsTrueWhenCountryHasDownloads(self):
        self.assertTrue(country_filter({'country': 'FIN', 'downloads': 1}))


class CreateMessageTestCase(unittest.TestCase):
    def setUp(self):
        self.tmpl = Template(u'{{author}}: {{downloads}}')
        self.ctx = {'author': u'Guðrún', 'downloads': 1,
                    'email': 'foo@example.com'}

    def testSetsToAddress(self):
        msg = create_message(u'bar@example.com', u'Test', self.ctx, self.tmpl)
        self.assertEqual(msg['To'], 'foo@example.com')

    def testAttachesPayload(self):
        msg = create_message(u'bar@example.com', u'Test', self.ctx, self.tmpl)
        self.assertEqual(msg.get_payload(decode=True),
                         u'Guðrún: 1'.encode('utf-8'))


def test_authors_removes_duplicates_by_email(mongo):
    with AddressService() as svc:
        a = list(authors(mongo.oastats.summary, svc, 8))
    assert len(a) == 2


def test_authors_removes_items_below_threshold(mongo):
    with AddressService() as svc:
        a = list(authors(mongo.oastats.summary, svc, 9))
    assert len(a) == 1


def test_authors_returns_constructed_author(mongo):
    with AddressService() as svc:
        a = list(authors(mongo.oastats.summary, svc, 8))
    assert a[0] == {
        'author': 'Foo Bar', 'email': 'foobar@example.com',
        'downloads': 10, 'articles': 2, 'countries': 2, 'total_size': 13,
        'total_countries': 4
    }


class TemplateFiltersTestCase(unittest.TestCase):
    def testPluralizeReturnsPluralForMoreThanOne(self):
        self.assertEqual(pluralize(2, 'foobar', 'foobars'), 'foobars')

    def testPluralizeReturnsSingleForOne(self):
        self.assertEqual(pluralize(1, 'foobar', 'foobars'), 'foobar')

    def testFormatNumAddsCommas(self):
        self.assertEqual(format_num(123), '123')
        self.assertEqual(format_num(1234), '1,234')
        self.assertEqual(format_num(12345), '12,345')
        self.assertEqual(format_num(1234567), '1,234,567')


def test_global_context_returns_summary(mongo):
    assert global_context(mongo.oastats.summary) == \
        {"size": 13, "countries": 4}


def test_address_service_returns_record():
    with AddressService() as svc:
        p = svc.lookup('0987')
    assert p == (u'Þorgerðr', u'Hǫlgabrúðr', 'thor@example.com')
