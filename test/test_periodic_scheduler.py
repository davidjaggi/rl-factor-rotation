import unittest

from src.data.rebalancing_schedule import PeriodicSchedule


class TestPeriodicSchedule(unittest.TestCase):
    def setUp(self) -> None:
        self.schedule = PeriodicSchedule("WOM-3FRI")

    def test_return_list(self):
        print(self.schedule.rebalancing_dates)
        # currently returns empty list
