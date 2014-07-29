# Copyright 2014 NYBX Inc.
# All rights reserved.

"""
:module: ledgerx.protocol.test.test_detail
:synopsis: Unit tests for the detail module.
:author: Amr Ali <amr@ledgerx.com>
"""

import unittest

from ledgerx.utils import jsonapi

class TestUtils(unittest.TestCase):

    def test_jsonapi(self):
        test = {'a': 1, 'b': 'c', 'c': 3.14159265359}
        json = jsonapi.dumps(test)
        obj = jsonapi.loads(json)
        self.assertEqual(obj, test)

