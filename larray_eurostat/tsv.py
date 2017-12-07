import os
import gzip
from io import StringIO
from urllib.request import urlopen
from datetime import date, time, datetime, timedelta, tzinfo

import pandas as pd
from larray import read_eurostat, read_hdf, Session


def remove_chars(s, chars):
    return s.translate({ord(c): None for c in chars})


EUROSTAT_BASEURL = "https://ec.europa.eu/eurostat/estat-navtree-portlet-prod/BulkDownloadListing?sort=1&file="


def _get_one(indicator, drop_markers=True, cache_dir=None, maxage=86400):
    """Get one Eurostat indicator and return it as an array"""

    if cache_dir is not None:
        cached_path = os.path.join(cache_dir, 'eurostat', 'data', f'{indicator}.h5')
        if os.path.exists(cached_path):
            cached_date = datetime.fromtimestamp(os.path.getmtime(cached_path))
            if maxage is None:
                oldest_acceptable = None
            elif isinstance(maxage, int):
                oldest_acceptable = datetime.now() - timedelta(seconds=maxage)
            elif isinstance(maxage, date):
                oldest_acceptable = datetime.combine(maxage, time(hour=0, minute=0))
            else:
                assert isinstance(maxage, datetime)
                oldest_acceptable = maxage
            if oldest_acceptable is None or cached_date >= oldest_acceptable:
                return read_hdf(cached_path, indicator)

    with urlopen(f"{EUROSTAT_BASEURL}data/{indicator}.tsv.gz") as f:
        with gzip.open(f, mode='rt') as fgz:
            try:
                s = fgz.read()
                if drop_markers:
                    first_line_end = s.index('\n')
                    # strip markers except on first line
                    s = s[:first_line_end] + remove_chars(s[first_line_end:], ' dbefcuipsrzn:')
                arr = read_eurostat(StringIO(s))
            except Exception as e:
                e.args = (e.args[0] + f"\nCan't open file {f.geturl()}",)
                raise
            if cache_dir is not None:
                os.makedirs(os.path.join(cache_dir, 'eurostat', 'data'), exist_ok=True)
                arr.to_hdf(cached_path, indicator)
            return arr


# copy-pasted with minor edits from Python documentation
class GMT1(tzinfo):
    def utcoffset(self, dt):
        return timedelta(hours=1) + self.dst(dt)

    def dst(self, dt):
        # DST starts last Sunday in March
        d = datetime(dt.year, 4, 1)
        self.dston = d - timedelta(days=d.weekday() + 1)
        # DST ends last Sunday in October
        d = datetime(dt.year, 11, 1)
        self.dstoff = d - timedelta(days=d.weekday() + 1)
        if self.dston <= dt.replace(tzinfo=None) < self.dstoff:
            return timedelta(hours=1)
        else:
            return timedelta(0)

    def tzname(self, dt):
        return "GMT +1"


gmt1 = GMT1()


def get_index(cache_dir=None, maxage='last_index_update'):
    """
    Parameters
    ----------
    cache_dir : str or None, optional
        Path to the cache directory.
    maxage : int or str or None, optional
        Maximum age in seconds for cached files. Defaults to 'last_index_update' (which is everyday at 11:00 and
        23:00 GMT+1). Use None to accept any age.

    Examples
    --------
    >>> df = get_index(cache_dir='__array_cache__', maxage=None)
    >>> df.columns
    Index(['title', 'code', 'type', 'last update of data',
           'last table structure change', 'data start', 'data end'],
          dtype='object')
    """
    if cache_dir is not None:
        cached_path = os.path.join(cache_dir, 'eurostat', 'table_of_contents_en.pkl')
        if os.path.exists(cached_path):
            if maxage is None:
                return pd.read_pickle(cached_path)
            else:
                current_eurostat_time = datetime.now(gmt1)
                if maxage == 'last_index_update':
                    # eurostat index is updated twice a day at 11 and 23 (GMT+1)
                    current_eurostat_day = current_eurostat_time.date()
                    if current_eurostat_time.hour < 11:
                        # yesterday at 23
                        yesterday = current_eurostat_day - timedelta(days=1)
                        last_index_update = datetime.combine(yesterday, time(hour=23, tzinfo=gmt1))
                    else:
                        # today at 11
                        last_index_update = datetime.combine(current_eurostat_day, time(hour=11, tzinfo=gmt1))
                    oldest_acceptable = last_index_update
                else:
                    oldest_acceptable = current_eurostat_time - timedelta(seconds=maxage)
                cached_date = datetime.fromtimestamp(os.path.getmtime(cached_path)).astimezone(gmt1)
                if cached_date >= oldest_acceptable:
                    return pd.read_pickle(cached_path)
    url = EUROSTAT_BASEURL + 'table_of_contents_en.txt'
    with urlopen(url) as f:
        df = pd.read_csv(f, sep='\t', usecols=list(range(7)))
        if cache_dir is not None:
            os.makedirs(os.path.join(cache_dir, 'eurostat'), exist_ok=True)
            df.to_pickle(cached_path)
        return df


def eurostat_get(indicators, drop_markers=True, cache_dir=None, maxage=86400):
    """Gets one or several Eurostat indicators and return them as an array or a session.

    Parameters
    ----------
    indicators : str or list/tuple of str
        Name(s) of eurostat indicator(s). When requesting a single indicator, the result is an Array, otherwise it is a
        Session.
    drop_markers : bool, optional
        Whether or not to drop special markers. Defaults to True.
    cache_dir : str, optional
        Path to the cache directory.  Defaults to None, in which case, no caching will occur and indicators will be
        fetched from Eurostat website each time the function is called.
    maxage : int, datetime.date, datetime.datetime or None, optional
        Maximum age for cached files. Older files in the cache will not be used.
        An int will be interpreted as the number of seconds from now. Defaults to 86400 (a day).
        A date(time) will be interpreted as the oldest date acceptable for cached files (i.e. use a cached indicator
        if it was fetched more recently than the given date).
        Use None to always used cached indicators, if any (this is useful for working without an internet connection).

    Returns
    -------
    Array or Session

    Examples
    --------
    >>> data = eurostat_get('avia_ec_enterp')
    >>> data.info
    2 x 16 x 13
     enterpr [2]: 'AIRP' 'AVIA'
     geo [16]: 'CY' 'CZ' 'EE' ... 'BG' 'FI' 'SE'
     time [13]: 2013 2012 2011 ... 2003 2002 2001
    dtype: float64
    memory used: 3.25 Kb
    >>> indicators = eurostat_get(['avia_ec_enterp', 'apro_mt_lsequi'])
    >>> indicators.names
    ['apro_mt_lsequi', 'avia_ec_enterp']
    >>> indicators.avia_ec_enterp.info
    2 x 16 x 13
     enterpr [2]: 'AIRP' 'AVIA'
     geo [16]: 'CY' 'CZ' 'EE' ... 'BG' 'FI' 'SE'
     time [13]: 2013 2012 2011 ... 2003 2002 2001
    dtype: float64
    memory used: 3.25 Kb
    >>> indicators.apro_mt_lsequi.info
    3 x 1 x 28 x 38
     animals [3]: 'A1000' 'A1100' 'A1200'
     unit [1]: 'THS_HD'
     geo [28]: 'AL' 'BE' 'BG' ... 'SI' 'SK' 'UK'
     time [38]: 1997 1996 1995 ... 1962 1961 1960
    dtype: float64
    memory used: 24.94 Kb
    """
    if isinstance(indicators, (tuple, list)):
        return Session({i: _get_one(i, drop_markers=drop_markers, cache_dir=cache_dir, maxage=maxage)
                        for i in indicators})
    else:
        return _get_one(indicators, drop_markers=drop_markers, cache_dir=cache_dir, maxage=maxage)
