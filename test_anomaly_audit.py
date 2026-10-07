import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parent


class ForecastVelocityAuditTests(unittest.TestCase):
    def run_audit(self, predictions):
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
                "const TRADES = {};\nconst UNUSED = {};\n",
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
            {"isoDate": "2026-10-13", "type": "high", "price": 106.0},
            {"isoDate": "2026-10-15", "type": "low", "price": 100.0},
        ])
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_same_session_turns_are_blocked(self):
        result = self.run_audit([
            {"isoDate": "2026-10-13", "type": "high", "price": 101.0},
            {"isoDate": "2026-10-13", "type": "low", "price": 100.0},
        ])
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("same trading session", result.stdout)

    def test_one_session_nineteen_percent_move_stays_blocked(self):
        result = self.run_audit([
            {"isoDate": "2026-10-13", "type": "high", "price": 119.0},
            {"isoDate": "2026-10-14", "type": "low", "price": 100.0},
        ])
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("implausible", result.stdout)


if __name__ == "__main__":
    unittest.main()
