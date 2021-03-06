#!/usr/bin/env python
# Copyright 2014 NYBX Inc.
# All rights reserved.

import os

from setuptools import setup, find_packages

BASE_DIR = os.path.dirname(__file__)
README_PATH = os.path.join(BASE_DIR, 'README.md')
REQS_PATH = os.path.join(BASE_DIR, 'requirements.txt')

with open('ledgerx/protocol/version.py', 'rb') as fd:
    exec(fd.read())

def __filter_requires(filename):
    # Unnecessary packages for exchange's normal operations
    unreqs = ['sphinx', 'theme', '-e']
    with open(filename, 'rb') as fd:
        reqs = map(lambda req: req.strip(b'\n').decode(), fd.readlines())
    for unreq in unreqs:
        reqs = filter(lambda x: unreq not in x.lower(), reqs)
    return list(reqs)

classifiers = [
    'License :: Other/Proprietary License',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Natural Language :: English',
    'Intended Audience :: Financial and Insurance Industry',
    'Topic :: Scientific/Engineering :: Mathematics',
    'Programming Language :: Python :: 3',
    ]

setup(
        name = 'ledgerx-protocol',
        version = __version__,
        description = 'LedgerX Base Protocol Library',
        long_description = open(README_PATH).read(),
        maintainer = 'Amr Ali',
        maintainer_email = 'amr@ledgerx.com',
        url = 'https://ledgerx.com',
        zip_safe = True,
        install_requires = __filter_requires(REQS_PATH),
        namespace_packages = ['ledgerx', 'ledgerx.protocol'],
        packages = find_packages(exclude=['*test*']),
        test_suite = 'ledgerx.protocol.tester.load_test_suite',
        platforms = 'POSIX',
        classifiers = classifiers,
    )

