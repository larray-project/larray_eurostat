import pytest
import re
from larray_eurostat.tsv import *


def test_eurostat_get():
    dataset = 'nama_aux_cra'

    msg = f"Not a gzipped file (b'<!')\nCan't open file {EUROSTAT_BASEURL}data/{dataset}.tsv.gz"
    with pytest.raises(OSError, match=re.escape(msg)):
        eurostat_get(dataset)
