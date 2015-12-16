# Copyright 2014 NYBX Inc.
# All rights reserved.

"""
:module: ledgerx.protocol.test.test_system
:synopsis: Unit tests for the system module.
:author: Amr Ali <amr@ledgerx.com>
"""

import os
import sys
import unittest
import time as pytime

from functools import partial
from ledgerx.protocol.system import time

class TestTime(unittest.TestCase):

    def test_interface(self):
        self.assertTrue(hasattr(time, 'realtime'))
        self.assertTrue(hasattr(time, 'monotonic'))

        if sys.platform != 'linux':
            self.assertEqual(time.realtime, pytime.time)
            self.assertEqual(time.monotonic, pytime.monotonic)
        else:
            self.assertIsInstance(time.realtime, partial)
            self.assertIsInstance(time.monotonic, partial)

    def test_timers(self):
        self.assertIsInstance(time.realtime(), float)
        self.assertIsInstance(time.monotonic(), float)

