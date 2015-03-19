# -*- coding: utf-8 -*-
from __future__ import absolute_import
import unittest
from mock import Mock, MagicMock
from string import Template

from poast.mail import threshold_filter, create_message, authors


class ThresholdFilterTestCase(unittest.TestCase):
    def testFilterReturnsFalseWhenBelowThreshold(self):
        self.assertFalse(threshold_filter({'downloads': 10, 'size': 6}, 5))

    def testFilterReturnsTrueWhenEqualToThreshold(self):
        self.assertTrue(threshold_filter({'downloads': 10, 'size': 5}, 5))

    def testFilterReturnTrueWhenAboveThreshold(self):
        self.assertTrue(threshold_filter({'downloads': 10, 'size': 4}, 5))


class CreateMessageTestCase(unittest.TestCase):
    def setUp(self):
        self.tmpl = Template(u'${author}: ${downloads}')
        self.ctx = {'author': u'Guðrún', 'downloads': 1, 'email': 'foo@example.com'}

    def testSetsToAddress(self):
        msg = create_message(u'bar@example.com', u'Test', self.ctx, self.tmpl)
        self.assertEqual(msg['To'], u'Guðrún <foo@example.com>')

    def testAttachesPayload(self):
        msg = create_message(u'bar@example.com', u'Test', self.ctx, self.tmpl)
        self.assertEqual(msg.get_payload(decode=True),
                         u'Guðrún: 1'.encode('utf-8'))

class AuthorsTestCase(unittest.TestCase):
    def setUp(self):
        item = {
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
        self.collection = Mock(**{'find.return_value': [item]})
        self.addresser = MagicMock()
        self.addresser.__enter__.return_value = Mock(
            **{'lookup.return_value': ('Foo', 'Bar', 'foobar@example.com')})

    def testFiltersOutItemsBelowThreshold(self):
        a = authors(self.collection, self.addresser, 9)
        self.assertEqual(len(list(a)), 0)

    def testReturnsConstructedAuthor(self):
        a = authors(self.collection, self.addresser, 8)
        self.assertEqual(next(a), {
            'author': 'Foo Bar', 'email': 'foobar@example.com', 'downloads': 10,
            'articles': 2, 'countries': 2,
        })
