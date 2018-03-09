from __future__ import absolute_import, division, print_function

import pytest
from larray_eurostat.tsv import *


def test_eurostat_get():
    dataset = 'nama_aux_cra'

    msg = "Not a gzipped file (b'<!')"
    if sys.version_info[0] >= 3:
        msg += "\nCan't open file {}{}.tsv.gz".format(EUROSTAT_BASEURL, dataset)
    type_err = IOError if sys.version_info[0] < 3 else OSError

    with pytest.raises(type_err, message=msg):
        eurostat_get(dataset)
