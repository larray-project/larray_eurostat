from __future__ import absolute_import, division, print_function

import pytest
import re
from larray_eurostat.tsv import *


def test_eurostat_get():
    dataset = 'nama_aux_cra'

    msg = "Not a gzipped file"
    if sys.version_info[0] >= 3:
        msg += " (b'<!')\nCan't open file {}data/{}.tsv.gz".format(EUROSTAT_BASEURL, dataset)
    type_err = IOError if sys.version_info[0] < 3 else OSError

    with pytest.raises(type_err, match=re.escape(msg)):
        eurostat_get(dataset)
