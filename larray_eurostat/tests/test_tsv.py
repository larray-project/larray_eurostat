import re
from urllib.error import HTTPError

import pytest

from larray_eurostat.tsv import eurostat_get


def test_eurostat_get_bad_dataset():
    dataset = 'does-not-exist'

    msg = "HTTP Error 404: Not Found"
    with pytest.raises(HTTPError, match=f'^{re.escape(msg)}$'):
        eurostat_get(dataset)
