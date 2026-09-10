from datetime import date
import unittest

import pandas as pd

from scoring import nearest_prospective_pivot, monthly_chain_failures


class ProspectiveScoringTests(unittest.TestCase):
    def fixture(self, generated='2026-09-09 06:21 PM ET'):
        return {'generated': generated, 'chart': {'dates': ['2026-09-09']},
                'predictions': [{'isoDate': '2026-09-09', 'type': 'high', 'price': 733.16}],
                'horizons': {'monthly': {'high': {'price': 721.89}, 'low': {'price': 700}}}}

    def test_evening_failure_replay_preserves_expired_targets(self):
        for ticker, side, target, headline in [('QQQ','high',733.16,721.89),
                ('GOOGL','low',326.0,327.9), ('AMZN','low',247.03,247.76)]:
            data = self.fixture()
            data['predictions'][0].update(type=side, price=target)
            data['horizons']['monthly'][side]['price'] = headline
            self.assertEqual(monthly_chain_failures(ticker, data), [])
            self.assertEqual(data['predictions'][0]['price'], target)
            data['predictions'][0]['isoDate'] = '2026-09-10'
            self.assertEqual(len(monthly_chain_failures(ticker, data)), 1)

    def test_intraday_target_still_checked(self):
        self.assertEqual(len(monthly_chain_failures('QQQ', self.fixture('2026-09-09 03:58 PM ET'))), 1)

    def test_explicit_session_and_month_rollover(self):
        data = self.fixture()
        data['horizonSession'] = '2026-10-01'
        data['predictions'][0]['isoDate'] = '2026-10-01'
        self.assertEqual(len(monthly_chain_failures('QQQ', data)), 1)
        data['predictions'][0]['isoDate'] = '2026-09-30'
        self.assertEqual(monthly_chain_failures('QQQ', data), [])

    def test_legacy_friday_after_close_advances_to_monday(self):
        data = self.fixture('2026-09-11 04:00 PM ET')
        data['chart']['dates'] = ['2026-09-11']
        data['predictions'][0]['isoDate'] = '2026-09-11'
        self.assertEqual(monthly_chain_failures('QQQ', data), [])
        data['predictions'][0]['isoDate'] = '2026-09-14'
        self.assertEqual(len(monthly_chain_failures('QQQ', data)), 1)

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
