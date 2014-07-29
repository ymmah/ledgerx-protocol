# Copyright 2014 NYBX Inc.
# All rights reserved.

"""
:module: ledgerx.protocol.detail.msgpack
:synopsis: Expose the same msgpack interface with secure default settings.
:author: Amr Ali <amr@ledgerx.com>
"""

from msgpack import *

def loads(data, max_buffer_size=4096, **kwargs):
    """\
    A secure version of :funcs:`msgpack.loads`.
    """
    up = Unpacker(max_buffer_size=max_buffer_size, **kwargs)
    up.feed(data)
    return up.unpack()

