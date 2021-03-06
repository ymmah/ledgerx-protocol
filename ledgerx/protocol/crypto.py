# Copyright 2014 NYBX Inc.
# All rights reserved.

"""
:module: ledgerx.protocol.crypto
:synopsis: Cryptographic operations module.
:author: Amr Ali <amr@ledgerx.com>
"""

import io
import zmq

from contextlib import contextmanager
from collections import Container

@contextmanager
def closing(obj_support_close, call_close=True):
    """\
    A context manager to control whether we want to call ``close`` on the object.

    :param obj_support_close: The object that supports the ``close`` method.
    :param call_close: Whether to call ``close`` on the object. (default: True)
    """
    try:
        yield obj_support_close
    finally:
        if call_close:
            obj_support_close.close()

class KeyPair(Container):
    """\
    A 0MQ CURVE key pair container.
    """
    header = "----- BEGIN {name} -----"
    footer = "----- END {name} -----"

    def __init__(self, public=None, private=None):
        self.private = private
        self.public = public

    def __contains__(self, keydata):
        hasit = False
        if self.public:
            hasit |= keydata == self.public
        if self.private:
            hasit |= keydata == self.private
        return hasit

    def __eq__(self, other):
        if isinstance(other, bytes):
            return other == self.private or other == self.public
        if isinstance(other, self.__class__):
            return other.public == self.public and other.private == self.private
        return False

    def save_certificate(self, file_or_obj):
        """\
        Generate a new CURVE key pair and store it in a certificate file or write
        it to a bytes buffer.

        :param file_or_obj: The path to the certificate file or bytes buffer.
        :returns: :class:`KeyPair`
        """
        header = self.header + '\n'
        footer = self.footer + '\n'

        call_close = True
        if hasattr(file_or_obj, 'writelines'):
            fobj = file_or_obj
            call_close = False
        else:
            fobj = open(file_or_obj, 'wb')

        with closing(fobj, call_close) as fd:
            if self.private:
                val = [header.format(name='PRIVATE KEY').encode('utf8'),
                        self.private + b'\n',
                        footer.format(name='PRIVATE KEY').encode('utf8')]
                fd.writelines(val)

            if self.public:
                val = [header.format(name='PUBLIC KEY').encode('utf8'),
                        self.public + b'\n',
                        footer.format(name='PUBLIC KEY').encode('utf8')]
                fd.writelines(val)
        return self

    @classmethod
    def generate(cls):
        """\
        Generate a new CURVE key pair.

        :returns: :class:`KeyPair`
        """
        pub, priv = zmq.curve_keypair()
        return cls(pub, priv)

    @classmethod
    def load_certificate(cls, file_or_bytes):
        """\
        Read both the public and private keys from a certificate file or bytes.

        :param file_or_bytes: The path to the certificate file or bytes.
        :returns: :class:`KeyPair` if successful, None otherwise
        """
        privstring = 'PRIVATE KEY'
        pubstring = 'PUBLIC KEY'
        should_continue = True
        privkey = pubkey = None

        if isinstance(file_or_bytes, bytes):
            fobj = io.BytesIO(file_or_bytes)
        else:
            fobj = open(file_or_bytes, 'rb')

        with fobj as fd:
            while should_continue:
                line = fd.readline()
                if cls.header.format(name=privstring).encode('utf8') in line:
                    privkey = fd.readline()[:-1]
                elif cls.header.format(name=pubstring).encode('utf8') in line:
                    pubkey = fd.readline()[:-1]

                if not line:
                    should_continue = False

        if not(privkey or pubkey):
            return None

        return cls(pubkey, privkey)

