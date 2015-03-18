#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import
import sys
try:
    import unittest2 as unittest
except ImportError:
    import unittest


def main():
    suite = unittest.defaultTestLoader.discover('tests')
    result = unittest.TextTestRunner().run(suite)
    if not result.wasSuccessful():
        sys.exit(1)

if __name__ == '__main__':
    main()
