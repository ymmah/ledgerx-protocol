# Copyright 2014 NYBX Inc.
# All rights reserved.

"""
:module: ledgerx.protocol.system.time
:synopsis: A module to allow access to high-precision system timers.
:author: Amr Ali <amr@ledgerx.com>

Code in this module will seem repetitive. It is carefully optimized to minimize
the polymorphic dispatch overhead.
"""

import os

from cffi import FFI

class time(object):
    """\
    A wrapper class to prevent CFFI context leaking outside of the module.
    """
    timespec = None # holds a `struct timespec` pointer

    # See <linux/time.h>
    CLOCK_REALTIME = 0
    CLOCK_MONOTONIC_RAW = 4
    CLOCK_REALTIME_COARSE = 5
    CLOCK_MONOTONIC_COARSE = 6

    @classmethod
    def init(cls):
        ffi = FFI()
        ffi.cdef(
                """
                /* See clock_gettime(2) */
                struct timespec {
                    long tv_sec; /* seconds */
                    long tv_nsec; /* nanoseconds */
                };

                int clock_gettime(int clk_id, struct timespec *tp);
                """
                )
        cls.C = ffi.verify("#include <time.h>")
        cls.timespec = ffi.new("struct timespec *")
        cls.ffi = ffi

    @classmethod
    def monotonic(cls):
        """\
        Return the tick of system wide monotonic timer since an unspecified
        starting event.

        :returns: float seconds since an unspecified starting event.
        """
        t = cls.timespec
        if cls.C.clock_gettime(cls.CLOCK_MONOTONIC_RAW, t) != 0:
            _errno = cls.ffi.errno
            raise OSError(_errno, os.strerror(_errno))
        return t.tv_sec + t.tv_nsec * 1e-9

    @classmethod
    def realtime(cls):
        """\
        Return the real time (i.e., wall-time) from a system wide timer.
        Note that this is a non-monotonic timer and will get affected
        by discontinuous jumps in the system time and by incremental
        adjustments performed by adjtime(3) and NTP.

        :returns: float seconds since the EPOCH.
        """
        t = cls.timespec
        if cls.C.clock_gettime(cls.CLOCK_REALTIME, t) != 0:
            _errno = cls.ffi.errno
            raise OSError(_errno, os.strerror(_errno))
        return t.tv_sec + t.tv_nsec * 1e-9

time.init()
realtime = time.realtime
monotonic = time.monotonic

__all__ = ['realtime', 'monotonic']

