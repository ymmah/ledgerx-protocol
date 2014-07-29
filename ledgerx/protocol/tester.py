# Copyright 2014 NYBX Inc.
# All rights reserved.

"""
:module: ledgerx.protocol.tester
:synopsis: Utilities for tests.
:author: Amr Ali <amr@ledgerx.com>
"""

import os

def load_test_suite():
    from unittest import TestLoader
    root_dir = os.path.dirname(os.path.abspath(__file__))
    suite = TestLoader().discover(root_dir)
    return suite

