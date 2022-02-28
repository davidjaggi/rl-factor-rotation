# %%
import unittest

from src.data.feed import StooqDataFeed
from src.utils.load_path import load_data_path


class TestStooqDataFeed(unittest.TestCase):
    def setUp(self):
        self.data_path = load_data_path()
        self.feed = StooqDataFeed(tickers=["AAPL", "MSFT"], start_date="2010-01-01", end_date="2020-01-01")

    def test_class(self):
        assert self.feed.__class__.__name__ == "StooqDataFeed"

    def test_data(self):
        df = self.feed.data
        assert df.__class__.__name__ == "dict"

    def test_num_assets(self):
        assert self.feed.num_assets == 2

    def test_column_names(self):
        # assert lists are equal
        print(self.feed.data["AAPL"].columns)
        names = ['Open', 'High', 'Low', 'Close', 'Volume']
        assert len(self.feed.data["AAPL"].columns) == len(names)
        assert all([a == b for a, b in zip(self.feed.data["AAPL"].columns, names)])
