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
    >>> data = eurostat_get('nama_10r_2gvagr')
    >>> data.info
    1 x 310 x 16
     unit [1]: 'PCH_PRE'
     geo [310]: 'AT' 'BE' 'BE1' ... 'UKN0' 'UKZ' 'UKZZ'
     time [16]: 2015 2014 2013 ... 2002 2001 2000
    dtype: float64
    memory used: 38.75 Kb
    """
    with urlopen(EUROSTAT_BASEURL + indicator + ".tsv.gz") as f:
        with gzip_open(f, mode='rt') as fgz:
            try:
                s = fgz.read()
                if drop_markers:
                    first_line_end = s.index('\n')
                    # strip markers except on first line
                    s = s[:first_line_end] + remove_chars(s[first_line_end:], ' dbefcuipsrzn:')
                return read_eurostat(StringIO(s))
            except Exception as e:
                if sys.version_info[0] >= 3:
                    e.args = (e.args[0] + " \nCan't open file {}".format(f.geturl()),)
                raise
