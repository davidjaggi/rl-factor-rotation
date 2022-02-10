# %%
import unittest
from src.data.data_feed import BaseDataFeed


class TestBaseDataFeed(unittest.TestCase):
    def setUp(self):
        self.tickers = ["AAPL", "MSFT"]
        self.start_date = "2020-01-01"
        self.end_date = "2020-12-31"
        self.data_feed = BaseDataFeed(self.tickers, self.start_date, self.end_date)
        self.df = self.data_feed.df

    def test_num_tickers(self):
        self.assertEqual(
            self.data_feed.num_tickers, len(self.tickers), "Number of tickers is not 2"
        )

    def test_column_name(self):
        self.assertIn("date", self.df.columns, "Date column is not in dataframe")

    def test_date_index(self):
        df_index = self.df.index
        df_date = self.df.date
