# Copyright 2014 NYBX Inc.
# All rights reserved.

"""
:module: ledgerx.protocol.test.test_sockets
:synopsis: Unit tests for the sockets module.
:author: Amr Ali <amr@ledgerx.com>
"""

import zmq
import unittest

from ledgerx.protocol import sockets

class TestSockets(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.ctx = zmq.Context()

    @classmethod
    def tearDownClass(cls):
        cls.ctx.destroy()

    def test_create_socket(self):
        s = sockets.create_socket(self.ctx, zmq.REQ)
        self.assertIsInstance(s, zmq.Socket)
        self.assertEqual(s.rcvtimeo, 1000)
        self.assertEqual(s.reconnect_ivl, 1)
        self.assertEqual(s.linger, 1000)
        self.assertEqual(s.sndhwm, 0)
        self.assertEqual(s.rcvhwm, 0)

    def test_sockets(self):
        self.__assert_sock_type('dealer', zmq.DEALER)
        self.__assert_sock_type('router', zmq.ROUTER)
        self.__assert_sock_type('req', zmq.REQ)
        self.__assert_sock_type('rep', zmq.REP)
        self.__assert_sock_type('sub', zmq.SUB)
        self.__assert_sock_type('xsub', zmq.XSUB)
        self.__assert_sock_type('pub', zmq.PUB)
        self.__assert_sock_type('xpub', zmq.XPUB)
        self.__assert_sock_type('push', zmq.PUSH)
        self.__assert_sock_type('pull', zmq.PULL)
        self.__assert_sock_type('pair', zmq.PAIR)

    def test_secure_socket(self):
        pub, priv = zmq.curve_keypair()

        s = sockets.secure_socket(sockets.req_socket, priv, pub, ctx=self.ctx)
        self.assertTrue(s.curve_server)

        s = sockets.secure_socket(sockets.req_socket, priv, pub,
                serverkey=pub, ctx=self.ctx)
        self.assertFalse(s.curve_server)

    def __assert_sock_type(self, socket, stype):
        s = getattr(sockets, '{0}_socket'.format(socket))(self.ctx)
        self.assertEqual(s.type, stype)

