# Copyright 2014 NYBX Inc.
# All rights reserved.

"""
:module: ledgerx.protocol.sockets
:synopsis: A module for socket patterns.
:author: Amr Ali <amr@ledgerx.com>
"""

import zmq

def create_socket(ctx, stype, rtimeo=1000, reconn_ivl=1,
        linger=1000):
    """\
    Create a 0MQ socket.

    :param ctx: The 0MQ context which this socket will belong to.
    :param stype: The 0MQ socket type.
    :param rtimeo: the 0MQ socket receive timeout in milliseconds.
    :param reconn_ivl: The 0MQ socket reconnection interval in milliseconds.
    :param linger: The 0MQ socket linger period in milliseconds.
    :returns: A 0MQ socket.
    """
    s = ctx.socket(stype)
    s.rcvtimeo = rtimeo
    s.reconnect_ivl = reconn_ivl
    s.linger = linger
    return s

def dealer_socket(ctx, *args, **kwargs):
    """\
    Create a 0MQ DEALER socket.

    :param ctx: The 0MQ context which this socket will belong to.
    :returns: A 0MQ socket.
    """
    return create_socket(ctx, zmq.DEALER, *args, **kwargs)

def router_socket(ctx, *args, **kwargs):
    """\
    Create a 0MQ ROUTER socket.

    :param ctx: The 0MQ context which this socket will belong to.
    :returns: A 0MQ socket.
    """
    return create_socket(ctx, zmq.ROUTER, *args, **kwargs)

def req_socket(ctx, *args, **kwargs):
    """\
    Create a 0MQ REQ socket.

    :param ctx: The 0MQ context which this socket will belong to.
    :returns: A 0MQ socket.
    """
    return create_socket(ctx, zmq.REQ, *args, **kwargs)

def rep_socket(ctx, *args, **kwargs):
    """\
    Create a 0MQ REP socket.

    :param ctx: The 0MQ context which this socket will belong to.
    :returns: A 0MQ socket.
    """
    return create_socket(ctx, zmq.REP, *args, **kwargs)

def sub_socket(ctx, *args, **kwargs):
    """\
    Create a 0MQ SUB socket.

    :param ctx: The 0MQ context which this socket will belong to.
    :returns: A 0MQ socket.
    """
    return create_socket(ctx, zmq.SUB, *args, **kwargs)

def pub_socket(ctx, *args, **kwargs):
    """\
    Create a 0MQ PUB socket.

    :param ctx: The 0MQ context which this socket will belong to.
    :returns: A 0MQ socket.
    """
    return create_socket(ctx, zmq.PUB, *args, **kwargs)

def push_socket(ctx, *args, **kwargs):
    """\
    Create a 0MQ PUSH socket.

    :param ctx: The 0MQ context which this socket will belong to.
    :returns: A 0MQ socket.
    """
    return create_socket(ctx, zmq.PUSH, *args, **kwargs)

def pull_socket(ctx, *args, **kwargs):
    """\
    Create a 0MQ PULL socket.

    :param ctx: The 0MQ context which this socket will belong to.
    :returns: A 0MQ socket.
    """
    return create_socket(ctx, zmq.PULL, *args, **kwargs)

def pair_socket(ctx, *args, **kwargs):
    """\
    Create a 0MQ PAIR socket.

    :param ctx: The 0MQ context which this socket will belong to.
    :returns: A 0MQ socket.
    """
    return create_socket(ctx, zmq.PAIR, *args, **kwargs)

def secure_socket(sfn, secretkey, publickey, serverkey=None, *args, **kwargs):
    """\
    Establish a CURVE secure 0MQ socket.

    :param sfn: Socket creation function.
    :param secretkey: The secret key.
    :param publickey: The public key.
    :param serverkey: The server key. Only supplied for client sockets.
    """
    s = sfn(*args, **kwargs)
    s.curve_secretkey = secretkey
    s.curve_publickey = publickey
    if serverkey:
        s.curve_serverkey = serverkey
    else:
        s.curve_server = True
    return s


