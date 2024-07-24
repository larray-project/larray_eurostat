import re
from urllib.error import HTTPError

import pytest

from larray_eurostat.tsv import eurostat_get


def test_eurostat_get_bad_dataset():
    dataset = 'does-not-exist'

    msg = "HTTP Error 404: Not Found"
    with pytest.raises(HTTPError, match=f'^{re.escape(msg)}$'):
        eurostat_get(dataset)


# https://github.com/larray-project/larray_eurostat/issues/33
def test_year_only_axes_as_int_and_not_object():
    data = eurostat_get('avia_ec_enterp')
    assert data.time.dtype.kind == 'i'
