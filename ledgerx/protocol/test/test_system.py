# Copyright 2014 NYBX Inc.
# All rights reserved.

"""
:module: ledgerx.protocol.test.test_system
:synopsis: Unit tests for the system module.
:author: Amr Ali <amr@ledgerx.com>
"""

import os
import unittest

from types import MethodType
from ledgerx.protocol.system import time

class TestTime(unittest.TestCase):

    def test_interface(self):
        self.assertTrue(hasattr(time, 'realtime'))
        self.assertTrue(hasattr(time, 'monotonic'))
        self.assertIsInstance(time.realtime, MethodType)
        self.assertIsInstance(time.monotonic, MethodType)

    def test_timers(self):
        self.assertIsInstance(time.realtime(), float)
        self.assertIsInstance(time.monotonic(), float)

