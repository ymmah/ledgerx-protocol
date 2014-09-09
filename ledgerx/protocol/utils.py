# Copyright 2014 NYBX Inc.
# All rights reserved.

"""
:module: ledgerx.protocol.utils
:synopsis: A module for misc utilities.
:author: Amr Ali <amr@ledgerx.com>
"""

import os
import importlib

from semantic_version import Version
from collections import deque as consume

def import_versions(basefile, package):
    """\
    Iterate over protocol files and import all version modules.

    :param basefile:
        The file from which adjacent version files will be imported.
    :param package:
        The package name that contains the version files.
    :returns:
        A dictionary of versions `x.x.x` and imported version modules.
    """
    vers = filter(lambda x: Version.version_re.match(x.lstrip('v').replace('_', '.')),
            map(lambda x: x.rstrip('.py'),
                os.listdir(os.path.dirname(basefile))
                )
            )
    res = {}
    consume(map(lambda x: res.update(
        {x.lstrip('v').replace('_', '.'): importlib.import_module(".{0}".format(x),
            package=package)}
        ), vers), maxlen=0)
    return res

