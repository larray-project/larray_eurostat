from __future__ import absolute_import, division, print_function

import sys
import urllib.request
import gzip

from larray import read_eurostat

if sys.version_info[0] < 3:
    from StringIO import StringIO
else:
    from io import StringIO

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
    """
    with urllib.request.urlopen(EUROSTAT_BASEURL + indicator + ".tsv.gz") as f:
        with gzip.open(f, mode='rt') as fgz:
            s = fgz.read()
            if drop_markers:
                first_line_end = s.index('\n')
                # strip markers except on first line
                s = s[:first_line_end] + s[first_line_end:].translate({ord(i): None for i in ' dbefcuipsrzn:'})
            return read_eurostat(StringIO(s))
