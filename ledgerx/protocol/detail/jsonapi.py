# Copyright 2014 NYBX Inc.
# All rights reserved.

"""
:module: ledgerx.protocol.detail.jsonapi
:synopsis: JSON API abstraction over all 3 major implementations.
:author: Amr Ali <amr@ledgerx.com>
"""

import importlib

_jsonmod = None
__priority = ['simplejson', 'jsonlib2', 'json']

for mod in __priority:
    try:
        _jsonmod = importlib.import_module(mod)
    except ImportError:
        pass
    else:
        break

def dumps(obj, **kwargs):
    """\
    Serialize object to JSON bytes (utf-8).
    See :func:`jsonapi.jsonmod.dumps` for details on kwargs.

    :param obj: A JSON serialize-able object.
    :returns: A JSON string of bytes.
    """
    if 'separators' not in kwargs:
        kwargs['separators'] = (',', ':')
    s = _jsonmod.dumps(obj, **kwargs)

    if not isinstance(s, bytes):
        s = s.encode('utf8')
    return s

def loads(s, **kwargs):
    """\
    Load object from JSON bytes (utf-8).
    See :func:`jsonapi.jsonmod.loads` for details on kwargs.

    :param s: A JSON string of bytes.
    :returns: A Python object.
    """
    if isinstance(s, bytes):
        s = s.decode('utf8')
    return _jsonmod.loads(s, **kwargs)

