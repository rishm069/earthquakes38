import unittest
import pandas
from conversion import klass_conversion
from data_retrival import fetch_data
from data_retrival import get_data
from data_retrival import conversion

class TestData(unittest.TestCase):
    def test_basic_data(self):
        self.assertIsInstance(get_data(), list)
    def test_conversion(self):
        new_ls = []
        conversion(get_data())
        self.assertIsInstance(fetch_data(), pandas.core.frame.DataFrame)
    def test_rows(self):
        self.assertIsNot(len(fetch_data()), 0)

unittest.main() 