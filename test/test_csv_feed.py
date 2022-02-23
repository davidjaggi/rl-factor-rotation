# %%
import unittest

from src.data.feed import CSVDataFeed
from src.utils.load_path import load_data_path


class TestCSVDataFeed(unittest.TestCase):
    def setUp(self):
        self.data_path = load_data_path()
        self.feed = CSVDataFeed(
            file_name=self.data_path + "/example_data.csv"
        )

    def test_class(self):
        assert self.feed.__class__.__name__ == "CSVDataFeed"

    def test_data(self):
        df = self.feed.data
        assert df.__class__.__name__ == "dict"

    def test_num_assets(self):
        assert self.feed.num_assets == 2

    def test_column_names(self):
        # assert lists are equal
        names = [
            "Price Open",
            "Price High",
            "Price Low",
            "Price Close",
            "Volume",
        ]
        assert len(self.feed.data["AAPL.O"].columns) == len(names)
        assert all([a == b for a, b in zip(self.feed.data["AAPL.O"].columns, names)])
