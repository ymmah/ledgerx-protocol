# Copyright 2014 NYBX Inc.
# All rights reserved.

"""
:module: ledgerx.protocol.test.test_crypto
:synopsis: Unit tests for the crypto module.
:author: Amr Ali <amr@ledgerx.com>
"""

import io
import unittest

from ledgerx.protocol.crypto import KeyPair

class TestKeyPair(unittest.TestCase):

    def test_keypair(self):
        kp = KeyPair(private=b'a', public=b'b')

        self.assertIn(kp, kp)
        self.assertIn(kp.public, kp)
        self.assertIn(kp.private, kp)

        self.assertEqual(kp, kp)
        self.assertEqual(kp.public, kp)
        self.assertEqual(kp.private, kp)

        kpt = KeyPair(private=b'a', public=b'a')
        self.assertNotEqual(kpt, kp)
        self.assertIn(kpt, kp)
        self.assertIn(kp, kpt)
        self.assertNotIn(kp.public, kpt)
        self.assertNotEqual(kp.public, kpt)
        self.assertEqual(kp.private, kpt)

    def test_keypair_generate(self):
        keypair = KeyPair.generate()
        self.assertIn(keypair.public, keypair)
        self.assertIn(keypair.private, keypair)

    def test_keypair_generate_load_certificate(self):
        filepath = '/tmp/test_ledgerx.cert'
        keypair0 = KeyPair.generate().save_certificate(filepath)
        keypair1 = KeyPair.load_certificate(filepath)
        self.assertEqual(keypair0, keypair1)

        with open(filepath, 'rb') as fd:
            keypair1 = KeyPair.load_certificate(fd.read())
        self.assertEqual(keypair0, keypair1)

    def test_keypair_io_interface(self):
        buff = io.BytesIO()
        keypair0 = KeyPair.generate().save_certificate(buff)
        keypair1 = KeyPair.load_certificate(buff.getvalue())
        self.assertEqual(keypair0, keypair1)

