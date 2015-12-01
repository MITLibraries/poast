# -*- coding: utf-8 -*-
from __future__ import absolute_import
import unittest
from mock import Mock, MagicMock
from jinja2 import Template

import pytest

from poast.mail import (threshold_filter, country_filter, create_message,
                        authors, format_num, pluralize, global_context)
from poast.addresses import AddressService


@pytest.fixture
def collection():
    item = {
        "_id": {
            "name": u"Foobar",
            "mitid": '1234'
        },
        "size": 2,
        "downloads": 10,
        "countries": [
            {"downloads": 3, "country": "USA"},
            {"downloads": 7, "country": "FRA"},
            {"downloads": 0, "country": "ISL"}
        ]
    }
    coll = Mock()
    coll.find_one.return_value = \
        {'size': 1, 'countries': [{'downloads': 1, 'country': 'USA'}]}
    coll.find.return_value = [item]
    return coll


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


class AuthorsTestCase(unittest.TestCase):
    def setUp(self):
        self.item = {
            "_id": {
                "name": u"Foobar",
                "mitid": 123
            },
            "size": 2,
            "downloads": 10,
            "countries": [
                {"downloads": 3, "country": "USA"},
                {"downloads": 7, "country": "FRA"},
                {"downloads": 0, "country": "ISL"}
            ]
        }
        self.collection = Mock()
        self.collection.find_one.return_value = \
            {'size': 1, 'countries': [{'downloads': 1, 'country': 'USA'}]}
        self.collection.find.return_value = [self.item]
        self.addresser = MagicMock()
        self.addresser.lookup.return_value = ('Foo', 'Bar',
                                              'foobar@example.com')

    def testFiltersOutDuplicatesByEmail(self):
        rows = [('Foo', 'Bar', 'foobar@example.com'),
                ('Foo', 'Baz', 'foobaz@example.com'),
                ('Foo', 'Bar', 'foobar@example.com')]
        self.collection.find.return_value = [self.item] * 3
        self.addresser.lookup.side_effect = rows
        a = authors(self.collection, self.addresser, 1)
        self.assertEqual(len(list(a)), 2)


def test_authors_removes_items_below_threshold(collection):
    with AddressService() as svc:
        a = list(authors(collection, svc, 9))
    assert len(a) == 0


def test_authors_returns_constructed_author(collection):
    with AddressService() as svc:
        a = list(authors(collection, svc, 8))
    assert a[0] == {
        'author': 'Foo Bar', 'email': 'foobar@example.com',
        'downloads': 10, 'articles': 2, 'countries': 2, 'total_size': 1,
        'total_countries': 1
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


class GlobalContextTestCase(unittest.TestCase):
    def testReturnsSummaryDictionary(self):
        item = {'size': 123456, 'countries': [
            {"downloads": 3, "country": "USA"},
            {"downloads": 7, "country": "FRA"},
            {"downloads": 0, "country": "ISL"}
        ]}
        coll = Mock(**{'find_one.return_value': item})
        self.assertEqual(global_context(coll),
                         {'size': 123456, 'countries': 2})


def test_address_service_returns_record():
    with AddressService() as svc:
        p = svc.lookup('0987')
    assert p == (u'Þorgerðr', u'Hǫlgabrúðr', 'thor@example.com')
