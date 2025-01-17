"""
    babel.localtime
    ~~~~~~~~~~~~~~~

    Babel specific fork of tzlocal to determine the local timezone
    of the system.

    :copyright: (c) 2013-2022 by the Babel Team.
    :license: BSD, see LICENSE for more details.
"""

import sys
import time
from datetime import datetime, timedelta, tzinfo
from threading import RLock

if sys.platform == 'win32':
    from babel.localtime._win32 import _get_localzone
else:
    from babel.localtime._unix import _get_localzone


_cached_tz = None
_cache_lock = RLock()

STDOFFSET = timedelta(seconds=-time.timezone)
if time.daylight:
    DSTOFFSET = timedelta(seconds=-time.altzone)
else:
    DSTOFFSET = STDOFFSET

DSTDIFF = DSTOFFSET - STDOFFSET
ZERO = timedelta(0)


class _FallbackLocalTimezone(tzinfo):

    def utcoffset(self, dt: datetime) -> timedelta:
        if self._isdst(dt):
            return DSTOFFSET
        else:
            return STDOFFSET

    def dst(self, dt: datetime) -> timedelta:
        if self._isdst(dt):
            return DSTDIFF
        else:
            return ZERO

    def tzname(self, dt: datetime) -> str:
        return time.tzname[self._isdst(dt)]

    def _isdst(self, dt: datetime) -> bool:
        tt = (dt.year, dt.month, dt.day,
              dt.hour, dt.minute, dt.second,
              dt.weekday(), 0, -1)
        stamp = time.mktime(tt)
        tt = time.localtime(stamp)
        return tt.tm_isdst > 0


def get_localzone() -> tzinfo:
    """Returns the current underlying local timezone object.
    Generally this function does not need to be used, it's a
    better idea to use the :data:`LOCALTZ` singleton instead.
    """
    return _get_localzone()


try:
    LOCALTZ = get_localzone()
except LookupError:
    LOCALTZ = _FallbackLocalTimezone()
