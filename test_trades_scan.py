from datetime import date, datetime, timezone
import io
import json
import inspect
import unittest
from unittest.mock import patch

from trades_scan import _bizdays, build_trades


class TradeHorizonTests(unittest.TestCase):
    def test_october_fourteenth_is_six_sessions_from_october_sixth(self):
        self.assertEqual(_bizdays(date(2026, 10, 6), date(2026, 10, 14)), 6)

    def test_generator_uses_eastern_date_not_runner_date(self):
        source = inspect.getsource(build_trades)
        self.assertIn("eastern_now().date()", source)
        self.assertNotIn("date.today()", source)

    def model_cards(self, target):
        expiry = int(datetime(2027, 1, 15, tzinfo=timezone.utc).timestamp())
        options = [{"strike": k, "bid": 1, "ask": 2} for k in [75, 85, 95, 105]]
        payload = {"optionChain": {"result": [{"expirationDates": [expiry],
                   "options": [{"puts": options, "calls": options}]}]}}
        class Opener:
            def open(self, *args, **kwargs):
                return io.StringIO(json.dumps(payload))
        data = {"TEST": {"price": 90, "levels": {"support": [], "resistance": []},
                "predictions": [
                    {"type": "low", "price": target, "isoDate": "2026-12-07", "date": "Mon 12/07"},
                    {"type": "high", "price": 100, "isoDate": "2026-12-14", "date": "Mon 12/14"}]}}
        with patch("trades_scan._session", return_value=(Opener(), "test")), \
             patch("trades_scan.eastern_now", return_value=datetime(2026, 11, 11, tzinfo=timezone.utc)):
            result = build_trades(data)
        self.assertIn("TEST", result)
        return [t for t in result["TEST"]["trades"] if t["kind"] == "MODEL"]

    def test_sparse_grid_omits_model_that_would_fail_audit(self):
        self.assertEqual(self.model_cards(82.51), [])

    def test_nearby_model_remains_available(self):
        cards = self.model_cards(83)
        self.assertEqual(len(cards), 1)
        self.assertEqual(cards[0]["strikes"], [85])


if __name__ == "__main__":
    unittest.main()
