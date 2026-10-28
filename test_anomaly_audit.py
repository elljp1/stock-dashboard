from datetime import date, timedelta
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parent

# The audit flags any forecast event dated before today, so fixture dates must
# stay in the future.  Anchor on a Monday at least a week out so session counts
# (weekdays only) are stable and no time-zone edge can make a date look past.
_today = date.today()
MON = _today + timedelta(days=7 + (7 - _today.weekday()) % 7)
TUE = MON + timedelta(days=1)
WED = MON + timedelta(days=2)


class ForecastVelocityAuditTests(unittest.TestCase):
    def run_audit(self, predictions, trades=None):
        data = {
            "TEST": {
                "price": 100.0,
                "predictions": predictions,
                "levels": {"support": [], "resistance": []},
                "horizons": {},
                "dayForecasts": [],
            }
        }
        with tempfile.TemporaryDirectory() as td:
            Path(td, "data.js").write_text(
                "const DATA_ALL = " + json.dumps(data) + ";\n"
                "const TRADES = " + json.dumps(trades or {}) + ";\nconst UNUSED = {};\n",
                encoding="utf-8",
            )
            return subprocess.run(
                [sys.executable, str(ROOT / "anomaly_audit.py")],
                cwd=td,
                capture_output=True,
                text=True,
            )

    def test_two_session_moderate_swing_is_allowed(self):
        result = self.run_audit([
            {"isoDate": MON.isoformat(), "type": "high", "price": 106.0},
            {"isoDate": WED.isoformat(), "type": "low", "price": 100.0},
        ])
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_same_session_turns_are_blocked(self):
        result = self.run_audit([
            {"isoDate": MON.isoformat(), "type": "high", "price": 101.0},
            {"isoDate": MON.isoformat(), "type": "low", "price": 100.0},
        ])
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("same trading session", result.stdout)

    def test_one_session_nineteen_percent_move_stays_blocked(self):
        result = self.run_audit([
            {"isoDate": MON.isoformat(), "type": "high", "price": 119.0},
            {"isoDate": TUE.isoformat(), "type": "low", "price": 100.0},
        ])
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("implausible", result.stdout)

    def test_expiration_year_is_checked_without_month_day_rollover_false_alarm(self):
        entry_year = _today.year if _today < date(_today.year, 12, 1) else _today.year + 1
        entry = date(entry_year, 12, 1)
        exit_date = date(entry_year, 12, 8)
        good_expiry = date(entry_year + 1, 1, 15)
        trade = {
            "kind": "INCOME", "label": "year rollover", "hz": "",
            "sortd": entry.isoformat(), "execute": "Tue 12/01",
            "exitWin": "Tue 12/08", "exp": "Jan 15",
            "expIso": good_expiry.isoformat(), "strikes": [], "premium": 1,
        }
        good = self.run_audit([], {"TEST": {"trades": [trade]}})
        self.assertEqual(good.returncode, 0, good.stdout + good.stderr)

        trade["expIso"] = date(entry_year, 12, 1).isoformat()
        bad = self.run_audit([], {"TEST": {"trades": [trade]}})
        self.assertNotEqual(bad.returncode, 0)
        self.assertIn("expires Jan 15 before its exit", bad.stdout)


if __name__ == "__main__":
    unittest.main()

