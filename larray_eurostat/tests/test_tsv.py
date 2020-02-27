import pytest
import re
from larray_eurostat.tsv import *


def test_eurostat_get():
    dataset = 'nama_aux_cra'

    msg = "Not a gzipped file (b'<!')\nCan't open file {}data/{}.tsv.gz".format(EUROSTAT_BASEURL, dataset)
    with pytest.raises(OSError, match=re.escape(msg)):
        eurostat_get(dataset)
