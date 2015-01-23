#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import

try:
    import unittest2 as unittest
except ImportError:
    import unittest


def main():
    suite = unittest.defaultTestLoader.discover('tests')
    unittest.TextTestRunner().run(suite)

if __name__ == '__main__':
    main()
