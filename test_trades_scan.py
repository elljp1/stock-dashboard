from datetime import date
import inspect
import unittest

from trades_scan import _bizdays, build_trades


class TradeHorizonTests(unittest.TestCase):
    def test_october_fourteenth_is_six_sessions_from_october_sixth(self):
        self.assertEqual(_bizdays(date(2026, 10, 6), date(2026, 10, 14)), 6)

    def test_generator_uses_eastern_date_not_runner_date(self):
        source = inspect.getsource(build_trades)
        self.assertIn("eastern_now().date()", source)
        self.assertNotIn("date.today()", source)


if __name__ == "__main__":
    unittest.main()
