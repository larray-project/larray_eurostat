from __future__ import absolute_import, division, print_function

import sys
import gzip

from larray import read_eurostat

if sys.version_info[0] < 3:
    from StringIO import StringIO
    from urllib2 import urlopen as _urlopen
    from contextlib import closing

    # this version of urlopen can probably be used *only* as a context manager
    def urlopen(*args, **kwargs):
        with closing(_urlopen(*args, **kwargs)) as f:
            # fetching the whole file instead of streaming it, because Python2's gzip does not support that
            compressed_data = StringIO(f.read())
        return closing(compressed_data)

    def gzip_open(file_obj, mode):
        return gzip.GzipFile(fileobj=file_obj, mode='rb')

    def remove_chars(s, chars):
        return s.translate(None, chars)
else:
    from io import StringIO
    from urllib.request import urlopen
    gzip_open = gzip.open

    def remove_chars(s, chars):
        return s.translate({ord(c): None for c in chars})


EUROSTAT_BASEURL = "http://ec.europa.eu/eurostat/estat-navtree-portlet-prod/BulkDownloadListing?sort=1&file=data%2F"


def eurostat_get(indicator, drop_markers=True):
    """Gets Eurostat indicator and returns it as an array.

    Parameters
    ----------
    indicator : str
        name of eurostat indicator
    drop_markers : bool
        drop markers.

    Returns
    -------
    LArray

    Examples
    --------
    >>> gdp = eurostat_get('nama_aux_cra')
    >>> gdp.info
    1 x 45 x 54
     indic_na [1]: 'PPS_NAC'
     geo [45]: 'AT' 'BA' 'BE' ... 'TR' 'UK' 'US'
     time [54]: 2013 2012 2011 ... 1962 1961 1960
    dtype: float64
    """
    with urlopen(EUROSTAT_BASEURL + indicator + ".tsv.gz") as f:
        with gzip_open(f, mode='rt') as fgz:
            s = fgz.read()
            if drop_markers:
                first_line_end = s.index('\n')
                # strip markers except on first line
                s = s[:first_line_end] + remove_chars(s[first_line_end:], ' dbefcuipsrzn:')
            return read_eurostat(StringIO(s))
