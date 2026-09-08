from datetime import date
import unittest

import pandas as pd

from scoring import nearest_prospective_pivot


class ProspectiveScoringTests(unittest.TestCase):
    def test_pre_log_pivot_cannot_score(self):
        pivots = [
            {"type": "high", "date": pd.Timestamp("2026-08-13")},
            {"type": "high", "date": pd.Timestamp("2026-08-20")},
        ]
        trading_days = [date(2026, 8, d) for d in range(10, 25)]
        td_pos = lambda value: trading_days.index(value)
        result = nearest_prospective_pivot(
            pivots, "high", date(2026, 8, 18), date(2026, 8, 17), td_pos
        )
        self.assertEqual(result["date"].date(), date(2026, 8, 20))

    def test_same_day_pivot_cannot_score_after_daily_analysis(self):
        pivots = [{"type": "low", "date": pd.Timestamp("2026-08-17")}]
        result = nearest_prospective_pivot(
            pivots, "low", date(2026, 8, 18), date(2026, 8, 17), lambda value: 0
        )
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
