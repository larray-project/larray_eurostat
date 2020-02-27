import gzip

from larray import read_eurostat, Session

from io import StringIO
from urllib.request import urlopen
gzip_open = gzip.open

def remove_chars(s, chars):
    return s.translate({ord(c): None for c in chars})


EUROSTAT_BASEURL = "https://ec.europa.eu/eurostat/estat-navtree-portlet-prod/BulkDownloadListing?sort=1&file="


def _get_one(indicator, drop_markers=True):
    """Get one Eurostat indicator and return it as an array"""

    with urlopen(EUROSTAT_BASEURL + 'data/' + indicator + ".tsv.gz") as f:
        with gzip_open(f, mode='rt') as fgz:
            try:
                s = fgz.read()
                if drop_markers:
                    first_line_end = s.index('\n')
                    # strip markers except on first line
                    s = s[:first_line_end] + remove_chars(s[first_line_end:], ' dbefcuipsrzn:')
                return read_eurostat(StringIO(s))
            except Exception as e:
                e.args = (e.args[0] + "\nCan't open file {}".format(f.geturl()),)
                raise


def eurostat_get(indicators, drop_markers=True):
    """Gets one or several Eurostat indicators and return them as an array or a session.

    Parameters
    ----------
    indicators : str or list/tuple of str
        Name(s) of eurostat indicator(s). When requesting a single indicator, the result is an array, otherwise it is a
        Session.
    drop_markers : bool
        drop markers.

    Returns
    -------
    LArray or Session

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
        return Session([(i, _get_one(i, drop_markers=drop_markers)) for i in indicators])
    else:
        return _get_one(indicators, drop_markers=drop_markers)
