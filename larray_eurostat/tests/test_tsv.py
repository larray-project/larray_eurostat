import re

import pytest

from larray_eurostat.tsv import eurostat_get, EUROSTAT_BASEURL


def test_eurostat_get_bad_dataset():
    dataset = 'nama_aux_cra'

    msg = f"Not a gzipped file (b'<!')\nCan't open file {EUROSTAT_BASEURL}data/{dataset}.tsv.gz"
    with pytest.raises(OSError, match=f'^{re.escape(msg)}$'):
        eurostat_get(dataset)
