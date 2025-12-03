import re
from urllib.error import HTTPError

import pytest

from larray_eurostat.tsv import eurostat_get


def test_eurostat_get_bad_dataset():
    dataset = 'does-not-exist'

    msg = "HTTP Error 404: Not Found"
    with pytest.raises(HTTPError, match=f'^{re.escape(msg)}$') as ex_info:
        eurostat_get(dataset)
    # HTTPError Exceptions hold a reference to some resources which must
    # be explicitly closed, otherwise pytest complains on Python 3.14
    exception = ex_info.value
    exception.close()


# https://github.com/larray-project/larray_eurostat/issues/33
def test_year_only_axes_as_int_and_not_object():
    data = eurostat_get('avia_ec_enterp')
    assert data.time.dtype.kind == 'i'


# Check that annual frequency does not break when there is another axis with an 'A' label
# https://github.com/larray-project/larray_eurostat/issues/34
# An example of indicator with this problem is 'hsw_ph3_01'.
# Keeping this test commented because the data is ~34Mb, so using it as a unit test
# is probably not a good idea.
# def test_annual_freq_with_other_a_label():
#     data = eurostat_get('hsw_ph3_01')
#     assert 'freq' not in data.axes

