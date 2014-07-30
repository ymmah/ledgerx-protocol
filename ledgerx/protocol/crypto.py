# Copyright 2014 NYBX Inc.
# All rights reserved.

"""
:module: ledgerx.protocol.crypto
:synopsis: Cryptographic operations module.
:author: Amr Ali <amr@ledgerx.com>
"""

import zmq

from collections import Container

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

    def save_certificate(self, filepath):
        """\
        Generate a new CURVE key pair and store it in a certificate file.

        :param filepath: The path to the certificate file.
        :returns: :class:`KeyPair`
        """
        header = self.header + '\n'
        footer = self.footer + '\n'

        with open(filepath, 'wb') as fd:
            val = [header.format(name='PRIVATE KEY').encode('utf8'),
                    self.private + b'\n',
                    footer.format(name='PRIVATE KEY').encode('utf8')]
            fd.writelines(val)

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
    def load_certificate(cls, filepath):
        """\
        Read both the public and private keys from a certificate file.

        :param filepath: The path to the certificate file.
        :returns: :class:`KeyPair` if successful, None otherwise
        """
        privstring = 'PRIVATE KEY'
        pubstring = 'PUBLIC KEY'
        should_continue = True
        privkey = pubkey = None

        with open(filepath, 'rb') as fd:
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

