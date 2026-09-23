import copy
import unittest
from datetime import datetime

from quote_selection import select_quote


class QuoteSelectionTests(unittest.TestCase):
    def setUp(self):
        self.now = datetime.fromisoformat('2026-09-22T18:25:38-04:00')
        self.daily = datetime.fromisoformat('2026-09-22T09:30:00-04:00')
        self.payload = {'asof': self.now.timestamp(),
                        'prices': {'TSLA': 378.9},
                        'quotes': {'TSLA': {'price': 378.5479,
                          'quoteTime': '2026-09-22T18:25:13-04:00'}}}

    def test_small_change_uses_price_and_time_from_same_quote(self):
        result = select_quote(self.payload, 'TSLA', self.daily, self.now)
        self.assertEqual(result['price'], 378.5479)
        self.assertEqual(result['priceAsOf'], '2026-09-22T18:25:13-04:00')
        self.assertIn('5-minute bar', result['priceSource'])

    def test_invalid_price_never_supplies_new_timestamp(self):
        for value in [0, -1, float('nan'), float('inf'), None]:
            with self.subTest(value=value):
                payload = copy.deepcopy(self.payload)
                payload['quotes']['TSLA']['price'] = value
                self.assertIsNone(select_quote(payload, 'TSLA', self.daily, self.now))

    def test_old_missing_future_or_naive_quote_is_not_selected(self):
        for stamp in [None, '', '2026-09-21T19:59:00-04:00',
                      '2026-09-22T18:30:00-04:00', '2026-09-22T18:25:13']:
            with self.subTest(stamp=stamp):
                payload = copy.deepcopy(self.payload)
                payload['quotes']['TSLA']['quoteTime'] = stamp
                self.assertIsNone(select_quote(payload, 'TSLA', self.daily, self.now))

    def test_stale_or_future_fetch_is_not_selected(self):
        for delta in [-21600, 60]:
            payload = copy.deepcopy(self.payload)
            payload['asof'] += delta
            self.assertIsNone(select_quote(payload, 'TSLA', self.daily, self.now))

    def test_missing_quote_leaves_daily_fallback(self):
        self.assertIsNone(select_quote({}, 'TSLA', self.daily, self.now))


if __name__ == '__main__':
    unittest.main()
