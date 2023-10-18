import gzip
from io import StringIO
from urllib.request import urlopen

from larray import Session, read_eurostat


def _remove_chars(s, chars):
    return s.translate({ord(c): None for c in chars})

def transform_time_labels(label):
    # Account for ambiguous label type (in multifreq larrays, year is str; in only-year larrays, year is given as int)
    # Need string format to search for patterns (e.g. Q1,M12), but return int format when only years are given.
    str_label = str(label)

    if '-Q' in str_label:
        year, quarter = str_label.split('-')
        return f"{year}Q{quarter[1:]}"
    elif '-' in str_label:
        year, month = str_label.split('-')
        return f"{year}M{month.zfill(2)}"
    elif isinstance(label, int):
        return label
    else:
        return str_label

EUROSTAT_BASEURL = "https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/"

def _get_one(indicator, *, drop_markers=True):
    """Get one Eurostat indicator and return it as an array."""
    url = f"{EUROSTAT_BASEURL}{indicator}?format=TSV&compressed=true"
    with urlopen(url) as f, gzip.open(f, mode='rt') as fgz:    # noqa: S310
        try:
            s = fgz.read()
            if drop_markers:
                first_line_end = s.index('\n')
                # strip markers except on first line
                s = s[:first_line_end] + _remove_chars(s[first_line_end:], ' dbefcuipsrzn:')

            la_data = read_eurostat(StringIO(s))
            
            # Rename time axis. Rename time labels and reverse them (compatibility old API)
            la_data = la_data.rename(TIME_PERIOD='time')
            la_data = la_data.set_labels('time', transform_time_labels)
            la_data = la_data.reverse('time')
            
            # If only one frequency: subset and return without redundant freq Axis (compatibility old API)
            if len(la_data.freq) == 1:
                return la_data[la_data.freq.labels[0]]
            else:
                return la_data

        except Exception as e:
            e.args = (e.args[0] + f"\nCan't open file {f.geturl()}",)
            raise


def eurostat_get(indicators, *, drop_markers=True):
    """Get one or several Eurostat indicators and return them as an array or a session.

    Parameters
    ----------
    indicators : str or list/tuple of str
        Name(s) of eurostat indicator(s). When requesting a single indicator, the result is an Array, otherwise it is a
        Session.
    drop_markers : bool, optional
        Whether or not to drop special markers. Defaults to True.

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
        return Session({i: _get_one(i, drop_markers=drop_markers) for i in indicators})
    return _get_one(indicators, drop_markers=drop_markers)
