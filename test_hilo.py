import json
import tempfile
import unittest
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import hilo
import market_calendar as cal
from market_time import EASTERN


def et(y, m, d, hh, mm):
    return datetime(y, m, d, hh, mm, tzinfo=EASTERN)


def sessions_before(day, n):
    out, d = [], day
    while len(out) < n:
        d = cal.previous_session(d)
        out.append(d)
    return sorted(out)


def synthetic_bars(day, base, hi_bar=2, lo_bar=20):
    """Regular-session 15-minute bars with the high at hi_bar and the low at lo_bar."""
    n = cal.expected_bars(day)
    bars = []
    for i in range(n):
        t = hilo.hhmm(9 * 60 + 30 + 15 * i)
        h, l = base + 1, base - 1
        if i == hi_bar:
            h = base + 3 + (day.day % 3) * 0.1
        if i == lo_bar % n:
            l = base - 3 - (day.day % 4) * 0.1
        bars.append((t, h, l, base + 0.5))
    return bars


def build_store(days, base=100.0):
    store = {'TST': {}}
    now = datetime(2027, 1, 1, tzinfo=timezone.utc)
    hilo.update_store(store, 'TST', {d: synthetic_bars(d, base + i * 0.1) for i, d in enumerate(days)}, now)
    return store


def write_csv(path, days_bars):
    with open(path, 'w') as f:
        f.write('Datetime,Open,High,Low,Close,Volume\n')
        for day, bars in days_bars.items():
            for t, h, l, c in bars:
                ts = datetime.combine(day, datetime.strptime(t, '%H:%M').time(), EASTERN)
                f.write(f'{ts.isoformat(sep=" ")},{c},{h},{l},{c},0\n')


class CalendarTests(unittest.TestCase):
    def test_holiday_and_half_day(self):
        self.assertFalse(cal.is_session(date(2026, 9, 7)))           # Labor Day
        self.assertEqual(cal.expected_bars(date(2026, 11, 27)), 14)  # 1:00 PM close
        self.assertEqual(cal.expected_bars(date(2026, 10, 9)), 26)
        with self.assertRaises(ValueError):
            cal.is_session(date(2030, 1, 2))                          # unverified year fails closed

    def test_target_session(self):
        self.assertEqual(cal.target_session(et(2026, 10, 9, 8, 0)), (date(2026, 10, 9), 'premarket'))
        self.assertEqual(cal.target_session(et(2026, 10, 9, 11, 0)), (date(2026, 10, 9), 'intraday'))
        self.assertEqual(cal.target_session(et(2026, 10, 9, 16, 30)), (date(2026, 10, 12), 'premarket'))
        self.assertEqual(cal.target_session(et(2026, 9, 5, 12, 0)), (date(2026, 9, 8), 'premarket'))


class StoreTests(unittest.TestCase):
    def test_incomplete_and_open_sessions_are_not_stored(self):
        day = date(2026, 10, 8)
        bars = synthetic_bars(day, 100)
        store = {}
        hilo.update_store(store, 'TST', {day: bars[:-1]}, et(2026, 10, 9, 9, 0))
        self.assertNotIn('2026-10-08', store['TST'])                  # one bar missing
        hilo.update_store(store, 'TST', {day: bars}, et(2026, 10, 8, 15, 0))
        self.assertNotIn('2026-10-08', store['TST'])                  # session not closed yet
        hilo.update_store(store, 'TST', {day: bars}, et(2026, 10, 8, 16, 1))
        self.assertIn('2026-10-08', store['TST'])

    def test_half_day_needs_only_its_own_bars(self):
        day = date(2026, 11, 27)
        store = {}
        hilo.update_store(store, 'TST', {day: synthetic_bars(day, 100)}, et(2026, 11, 27, 13, 5))
        self.assertEqual(len(store['TST']['2026-11-27']['bars']), 14)

    def test_stored_session_is_never_rewritten(self):
        day = date(2026, 10, 8)
        store = {}
        hilo.update_store(store, 'TST', {day: synthetic_bars(day, 100)}, et(2026, 10, 9, 9, 0))
        hilo.update_store(store, 'TST', {day: synthetic_bars(day, 110)}, et(2026, 10, 9, 9, 0))
        self.assertEqual(store['TST']['2026-10-08']['bars'][0][3], 100.5)
        self.assertEqual(store['TST']['2026-10-08']['providerRevisions'], 1)


class ModelTests(unittest.TestCase):
    def setUp(self):
        self.day = date(2026, 10, 9)
        self.store = build_store(sessions_before(self.day, 30))

    def test_premarket_four_outputs_with_uncertainty(self):
        f, why = hilo.premarket_forecast(self.store['TST'], self.day)
        self.assertIsNone(why)
        for side in ('high', 'low'):
            b = f[side]
            self.assertLessEqual(b['lo'], b['price'])
            self.assertLessEqual(b['price'], b['hi'])
            self.assertIn('time', b)
            self.assertGreaterEqual(b['p60'], 0)
        self.assertEqual(f['high']['time'], '10:00')                 # synthetic highs sit at bar 2
        self.assertEqual(f['dataCutoff'], et(2026, 10, 8, 16, 0).isoformat())

    def test_premarket_ignores_target_and_later_sessions(self):
        before, _ = hilo.premarket_forecast(self.store['TST'], self.day)
        leaky = json.loads(json.dumps(self.store))
        for d in (self.day, date(2026, 10, 12)):
            leaky['TST'][d.isoformat()] = {'bars': [list(b) for b in synthetic_bars(d, 500, hi_bar=25)]}
        after, _ = hilo.premarket_forecast(leaky['TST'], self.day)
        self.assertEqual(before['high'], after['high'])
        self.assertEqual(before['low'], after['low'])

    def test_needs_prior_session(self):
        st = dict(self.store['TST'])
        st.pop(cal.previous_session(self.day).isoformat())
        f, why = hilo.premarket_forecast(st, self.day)
        self.assertIsNone(f)
        self.assertIn('prior session', why)

    def test_intraday_uses_only_bars_so_far(self):
        today = synthetic_bars(self.day, 103, hi_bar=1, lo_bar=3)[:4]
        f, why = hilo.intraday_forecast(self.store['TST'], self.day, today)
        self.assertIsNone(why)
        self.assertEqual(f['dataCutoff'], et(2026, 10, 9, 10, 30).isoformat())
        self.assertEqual(f['observed']['bars'], 4)
        self.assertGreaterEqual(f['high']['price'], f['observed']['high'])
        self.assertLessEqual(f['low']['price'], f['observed']['low'])
        self.assertTrue(0 <= f['high']['pAlreadySet'] <= 1)

    def test_intraday_rejects_gaps(self):
        today = synthetic_bars(self.day, 103)[:5]
        del today[2]
        f, why = hilo.intraday_forecast(self.store['TST'], self.day, today)
        self.assertIsNone(f)


class LedgerTests(unittest.TestCase):
    def test_chain_detects_edits(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'ledger.jsonl'
            hilo.append_record({'ticker': 'A', 'n': 1}, path)
            hilo.append_record({'ticker': 'B', 'n': 2}, path)
            self.assertEqual(hilo.verify_ledger(path), {'ok': True, 'records': 2})
            lines = path.read_text().splitlines()
            path.write_text(lines[0].replace('"n": 1', '"n": 9') + '\n' + lines[1] + '\n')
            self.assertFalse(hilo.verify_ledger(path)['ok'])


class RunTests(unittest.TestCase):
    def make_root(self, tmp, today_bars=None):
        root = Path(tmp)
        (root / 'tickers.txt').write_text('TST\nGC=F\n')
        days = sessions_before(date(2026, 10, 9), 30)
        bars = {d: synthetic_bars(d, 100 + i * 0.1) for i, d in enumerate(days)}
        if today_bars:
            bars[date(2026, 10, 9)] = today_bars
        write_csv(root / 'TST_15m.csv', bars)
        return root

    def test_premarket_once_then_intraday_revisions(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self.make_root(tmp, synthetic_bars(date(2026, 10, 9), 103))
            r1 = hilo.run(now=et(2026, 10, 9, 8, 0), root=root)
            hilo.run(now=et(2026, 10, 9, 8, 30), root=root)
            ledger = hilo.read_ledger(root / hilo.LEDGER)
            self.assertEqual([x['kind'] for x in ledger], ['premarket'])
            self.assertIn('GC=F', r1['excluded'])
            hilo.run(now=et(2026, 10, 9, 10, 40), root=root)
            ledger = hilo.read_ledger(root / hilo.LEDGER)
            intraday = [x for x in ledger if x['kind'] == 'intraday']
            self.assertEqual(len(intraday), 1)
            # 10:40: bars starting 9:30-10:15 have finished; the 10:30 bar has not
            self.assertEqual(intraday[0]['lastBar'], '2026-10-09 10:15')
            self.assertEqual(intraday[0]['checkpoint'], 4)
            hilo.run(now=et(2026, 10, 9, 10, 55), root=root)              # same checkpoint: no new record
            self.assertEqual(len([x for x in hilo.read_ledger(root / hilo.LEDGER) if x['kind'] == 'intraday']), 1)
            self.assertLessEqual(datetime.fromisoformat(intraday[0]['dataCutoff']),
                                 datetime.fromisoformat(intraday[0]['issuedAt']))
            self.assertTrue(hilo.verify_ledger(root / hilo.LEDGER)['ok'])

    def test_scoring_waits_for_complete_session_and_gates_issue_time(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self.make_root(tmp, synthetic_bars(date(2026, 10, 9), 103))
            hilo.run(now=et(2026, 10, 9, 8, 0), root=root)
            r = hilo.run(now=et(2026, 10, 9, 12, 0), root=root)
            self.assertEqual(r['forward']['premarket']['high']['n'], 0)   # session still open
            r = hilo.run(now=et(2026, 10, 9, 17, 0), root=root)
            self.assertEqual(r['forward']['premarket']['high']['n'], 1)
            late = dict(hilo.read_ledger(root / hilo.LEDGER)[0], issuedAt=et(2026, 10, 9, 9, 45).isoformat())
            store = json.loads((root / hilo.SESSIONS).read_text())
            self.assertEqual(hilo.score_rows([late], store), [])          # issued after the open


if __name__ == '__main__':
    unittest.main()
