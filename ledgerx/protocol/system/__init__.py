# Copyright 2014 NYBX Inc.
# All rights reserved.

"""
:module: ledgerx.protocol.system
:synopsis: A module to provide access to low-level C system functions.
:author: Amr Ali <amr@ledgerx.com>

Code in this module will seem repetitive. It is carefully optimized to minimize
the polymorphic dispatch overhead.
"""

from .time import *
