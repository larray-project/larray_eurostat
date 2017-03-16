from __future__ import absolute_import, division, print_function

from unittest import TestCase
import unittest
from larray_eurostat.tsv import *


class TestEurostat(TestCase):
    def test_eurostat_get(self):
        gdp = eurostat_get('nama_aux_cra')
        self.assertEqual(gdp.dtype, float)
        self.assertEqual(gdp.size, 2430)


if __name__ == "__main__":
    unittest.main()
