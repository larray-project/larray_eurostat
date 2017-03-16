from __future__ import absolute_import, division, print_function

import os
import urllib.request
import gzip
import larray as la

__all__ = ["eurostat_get"]

_eurostat_path = "http://ec.europa.eu/eurostat/estat-navtree-portlet-prod/BulkDownloadListing?sort=1&file=data%2F"


def _cleantsv(tsv):
    fline = tsv.index('\n')
    header = tsv[:fline]
    contents = tsv[fline:].translate({ord(i): None for i in ' dbefcuipsrzn:'})
    return (header + contents)


def eurostat_get(indicator, path='', drop_tsv=True):
    '''Gets Eurostat indicator and returns it as an array.

    Paramaters
    ----------
    indicator : str
        eurostat indicator
    path : str
        path to store temporary files (default: current directory)
    drop_tsv : bool
        delete tsv-file afterwards

    Returns
    -------
    LArray
        Array containing indicator.
    '''
    tsv = indicator + ".tsv"
    gz = tsv + ".gz"
    url = _eurostat_path + gz
    file_name, headers = urllib.request.urlretrieve(url, path + gz)

    fgz = gzip.open(path + gz, 'rt')
    ftsv = open(path + tsv, 'w+')
    tsvbuffer = fgz.read()
    ftsv.write(_cleantsv(tsvbuffer))
    fgz.close()
    ftsv.close()
    os.remove(path + gz)
    la_data = la.read_eurostat(path + tsv)
    if drop_tsv:
        os.remove(path + tsv)
    return la_data
