# -*- coding: utf-8 -*-
"""
OAStats Mailer
"""

import io
import re
from setuptools import find_packages, setup


with io.open('LICENSE') as fp:
    license = fp.read()

with io.open('poast/__init__.py', 'r') as fp:
    version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', fp.read(),
                        re.MULTILINE).group(1)

setup(
    name='poast',
    version=version,
    description='Mail some stats',
    long_description=__doc__,
    url='https://github.com/MITLibraries/poast',
    license=license,
    author='Mike Graves',
    author_email='mgraves@mit.edu',
    packages=find_packages(exclude=['tests']),
    install_requires=[
        'Jinja2',
        'PyYAML',
        'click',
        'pymongo',
    ],
    entry_points={
        'console_scripts': [
            'poast = poast.cli:main',
        ]
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Environment :: Console',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ]
)
