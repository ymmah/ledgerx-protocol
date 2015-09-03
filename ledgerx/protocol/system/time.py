# Copyright 2014 NYBX Inc.
# All rights reserved.

"""
:module: ledgerx.protocol.system.time
:synopsis: A module to allow access to high-precision system timers.
:author: Amr Ali <amr@ledgerx.com>
"""

import time

from functools import partial

# NOTE: Using partial is in fact faster than passing time.CLOCK_XXX to
# time.clock_gettime on every call.
if getattr(time, 'clock_gettime', None):
    realtime = partial(time.clock_gettime, time.CLOCK_REALTIME)
    monotonic = partial(time.clock_gettime, time.CLOCK_MONOTONIC_RAW)
else:
    realtime = time.time
    monotonic = time.monotonic

__all__ = ['realtime', 'monotonic']

