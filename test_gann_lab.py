from datetime import date
import unittest

import numpy as np
import pandas as pd

import gann_lab as g


def frame(close, start="2008-01-02"):
    idx = pd.bdate_range(start, periods=len(close), tz="America/New_York")
    return pd.DataFrame({"Close": close}, index=idx)


def planted(n=4500, seed=1):
    rng = np.random.default_rng(seed)
    idx = pd.bdate_range("2008-01-02", periods=n)
    days = np.array([(d - idx[0]).days for d in idx])
    return 100 * np.exp(0.15 * np.sin(2 * np.pi * days / 180.0) + np.cumsum(rng.normal(0, 0.004, n)))


class VibrationLabTests(unittest.TestCase):
    def test_zigzag_confirms_after_the_turn_and_finds_smooth_cycles(self):
        piv = g.zigzag(planted(1200), 6.0)
        self.assertGreater(len(piv), 15)
        for i, kind, confirmed in piv:
            self.assertGreater(confirmed, i)
        kinds = [k for _, k, _ in piv]
        self.assertTrue(all(a != b for a, b in zip(kinds, kinds[1:])))

    def test_planted_cycle_is_found_and_random_walk_is_not(self):
        found = g.analyze_ticker(frame(planted()), 6.0, date(2025, 4, 1))
        names = {r["tool"] for r in found["tools"] if r["verdict"] == "IN PLAY"}
        self.assertIn("90 calendar days from a major turn", names)
        rw = 100 * np.exp(np.cumsum(np.random.default_rng(1).normal(0, 0.018, 4500)))
        self.assertEqual(g.analyze_ticker(frame(rw), 6.0, date(2025, 4, 1))["inPlay"], 0)

    def test_calls_do_not_change_when_the_future_is_removed(self):
        close = planted(3000)
        cut = 2000
        full = frame(close)
        part = frame(close[:cut])

        def calls(df):
            c = df["Close"].to_numpy(float)
            cal = g.Calendar([d.date() for d in df.index])
            mj, mn = g.zigzag(c, 15.0), g.zigzag(c, 6.0)
            out = g.time_tools(cal, c, mj, mn, None, None)
            return {k: sorted((i, d) for i, d in v[1] if i < cut - 1 and d is not None)
                    for k, v in out.items()}
        a, b = calls(full), calls(part)
        for tool in b:
            if "swing duration" in tool or "major cycle" in tool:
                continue   # these map to sessions; beyond the cut they are unknown
            self.assertEqual(a.get(tool, []), b[tool], tool)

    def test_analog_calls_are_issued_before_their_targets(self):
        c = planted(2500)
        for name, (fam, calls) in g.analog_tools(c, g.zigzag(c, 6.0)).items():
            self.assertTrue(calls)
            self.assertTrue(all(target > issue for issue, target in calls), name)

    def test_levels_use_only_major_turns_confirmed_before_each_turn(self):
        c = planted(2500)
        mj, mn = g.zigzag(c, 15.0), g.zigzag(c, 6.0)
        cal = g.Calendar([d.date() for d in frame(c).index])
        lv = g.level_tools(c, mj, mn, None, None, cal)
        eligible = [m for m in mn if len([x for x in mj if x[2] <= m[0]]) >= 2]
        for name, (fam, prices, levels) in lv.items():
            self.assertEqual(len(prices), len(eligible), name)

    def test_shuffled_history_keeps_dates_and_start_price(self):
        df = frame(planted(800))
        s = g.shuffled(df, 3)
        self.assertTrue(s.index.equals(df.index))
        self.assertAlmostEqual(s["Close"].iloc[0], df["Close"].iloc[0])
        self.assertAlmostEqual(np.std(np.diff(np.log(s["Close"]))),
                               np.std(np.diff(np.log(df["Close"]))), places=6)


if __name__ == "__main__":
    unittest.main()
