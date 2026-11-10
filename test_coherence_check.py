"""Year-aware trade ordering must not block a valid December/January plan."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parent


class TradeOrderingTests(unittest.TestCase):
    def check(self, entry, exit_label, asof="2026-11-09 23:14", sortd="2026-12-07"):
        trades = {"QQQ": {"asof": asof, "trades": [{
            "label": "fixture", "execute": entry, "exitWin": exit_label,
            "sortd": sortd,
        }]}}
        with tempfile.TemporaryDirectory() as td:
            Path(td, "data.js").write_text(
                'const DATA_ALL = {};\nconst TRADES = ' + json.dumps(trades)
                + ';\nconst UNUSED = {};\n', encoding="utf-8")
            return subprocess.run([sys.executable, str(ROOT / "coherence_check.py")],
                                  cwd=td, capture_output=True, text=True)

    def test_december_to_january_is_valid(self):
        result = self.check("Mon 12/07", "Mon 01/04")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_named_month_rollover_is_valid(self):
        result = self.check("Dec 07", "Jan 04")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_real_reversed_dates_still_fail(self):
        result = self.check("Mon 12/07", "Tue 12/01")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("BEFORE it enters", result.stdout)

    def test_january_entry_before_december_exit_is_valid(self):
        result = self.check("Mon 01/04", "Mon 12/07", sortd="2026-01-04",
                            asof="2026-01-01 12:00")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_relative_exit_remains_unscored(self):
        result = self.check("Mon 12/07", "50% profit or ~1 week")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
