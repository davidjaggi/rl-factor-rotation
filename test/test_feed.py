# %%
import unittest
import numpy as np
import pandas as pd
from src.data.feed import Feed


class TestFeed(unittest.TestCase):
    def setUp(self):
        self.feed = Feed(
            start_date="2019-01-01", end_date="2019-01-02", price_field_name="Close"
        )

    def test_attribute(self):
        assert self.feed.start_date == "2019-01-01"
        assert self.feed.end_date == "2019-01-02"
        assert self.feed.price_field_name == "Close"

        """
        self.feed = Feed(start_date = )
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
        self.assertIn("ticker", self.df.columns, "Ticker column is not in dataframe")
        self.assertIn("close", self.df.columns, "Close column is not in dataframe")

    def test_index(self):
        print(self.df.head())
        # get all entries from multilevel index at 2020-01-01
        print(self.df.loc[("2020-01-02",)])
"""
