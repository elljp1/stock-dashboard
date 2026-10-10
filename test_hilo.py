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
            self.assertGreaterEqual(b['pBar'], 0)
            self.assertGreaterEqual(b['window']['p60'], b['pBar'])
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


def ledger_rec(n):
    side = {'price': 100.0 + n, 'lo': 99.0 + n, 'hi': 101.0 + n, 'time': '09:30', 'window': {'centre': '10:30'}}
    return {'model': 'test', 'kind': 'premarket', 'ticker': 'A', 'session': '2026-10-09', 'n': n,
            'issuedAt': '2026-10-09T12:00:00+00:00', 'dataCutoff': '2026-10-08T16:00:00-04:00',
            'high': dict(side), 'low': dict(side)}


class LedgerTests(unittest.TestCase):
    def test_chain_detects_edits(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'ledger.jsonl'
            hilo.append_record(ledger_rec(1), path)
            hilo.append_record(ledger_rec(2), path)
            self.assertEqual(hilo.verify_ledger(path), {'ok': True, 'records': 2})
            lines = path.read_text().splitlines()
            path.write_text(lines[0].replace('"n": 1', '"n": 9') + '\n' + lines[1] + '\n')
            self.assertFalse(hilo.verify_ledger(path)['ok'])

    def test_chain_detects_deletion_and_reordering(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'ledger.jsonl'
            for n in range(3):
                hilo.append_record(ledger_rec(n), path)
            lines = path.read_text().splitlines()
            path.write_text('\n'.join([lines[0], lines[2]]) + '\n')          # middle record deleted
            self.assertFalse(hilo.verify_ledger(path)['ok'])
            path.write_text('\n'.join(lines[1:]) + '\n')                     # first record deleted
            self.assertFalse(hilo.verify_ledger(path)['ok'])
            path.write_text('\n'.join([lines[1], lines[0], lines[2]]) + '\n')  # reordered
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


class ReviewFixTests(unittest.TestCase):
    """Cases from the 2026-10-09 review of 89c4934."""

    def root(self, tmp, day=date(2026, 10, 9), today=None, n=30):
        root = Path(tmp)
        (root / 'tickers.txt').write_text('TST\n')
        days = sessions_before(day, n)
        bars = {d: synthetic_bars(d, 100 + i * 0.1) for i, d in enumerate(days)}
        if today:
            bars[day] = today
        write_csv(root / 'TST_15m.csv', bars)
        return root

    def intraday(self, root):
        return [x for x in hilo.read_ledger(root / hilo.LEDGER) if x['kind'] == 'intraday']

    def test_late_checkpoint_freezes_exact_bars_and_is_not_scored(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self.root(tmp, today=synthetic_bars(date(2026, 10, 9), 103))
            hilo.run(now=et(2026, 10, 9, 10, 55), root=root)      # five bars done, checkpoint 4
            rec = self.intraday(root)[0]
            self.assertEqual((rec['checkpoint'], rec['observed']['bars']), (4, 4))
            self.assertEqual(rec['lastBar'], '2026-10-09 10:15')
            self.assertEqual(rec['dataCutoff'], et(2026, 10, 9, 10, 30).isoformat())
            self.assertTrue(rec['late'])                          # issued 25 min after its cutoff
            r = hilo.run(now=et(2026, 10, 9, 17, 0), root=root)
            self.assertEqual(r['forward']['intraday']['high']['n'], 0)
            self.assertEqual(r['lateIntradayRecords'], 1)

    def test_skipped_checkpoints_are_not_backfilled(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self.root(tmp, today=synthetic_bars(date(2026, 10, 9), 103))
            hilo.run(now=et(2026, 10, 9, 11, 35), root=root)      # first run after 11:30
            self.assertEqual([x['checkpoint'] for x in self.intraday(root)], [8])

    def test_timely_checkpoint_is_scored(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self.root(tmp, today=synthetic_bars(date(2026, 10, 9), 103))
            hilo.run(now=et(2026, 10, 9, 10, 31), root=root)
            self.assertFalse(self.intraday(root)[0]['late'])
            r = hilo.run(now=et(2026, 10, 9, 17, 0), root=root)
            self.assertEqual(r['forward']['intraday']['high']['n'], 1)

    def test_half_day_checkpoint_uses_same_bar_count(self):
        day = date(2026, 11, 27)
        with tempfile.TemporaryDirectory() as tmp:
            root = self.root(tmp, day=day, today=synthetic_bars(day, 103))
            hilo.run(now=et(2026, 11, 27, 12, 50), root=root)     # 13 bars done of 14
            rec = self.intraday(root)[0]
            self.assertEqual((rec['checkpoint'], rec['observed']['bars']), (13, 13))
            r = hilo.run(now=et(2026, 11, 27, 17, 0), root=root)
            self.assertEqual(r['forward']['intradayByCheckpoint']['13']['high']['n'], 0)   # half days kept apart
            self.assertEqual(r['forward']['intraday']['high']['n'], 1)

    def test_invalid_chain_blocks_append_and_scoring(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self.root(tmp)
            hilo.run(now=et(2026, 10, 9, 8, 0), root=root)
            path = root / hilo.LEDGER
            line = path.read_text().splitlines()[0]
            rec = json.loads(line)
            rec['high']['price'] = rec['high']['price'] + 1             # parseable but altered
            path.write_text(json.dumps(rec, sort_keys=True) + '\n')
            r = hilo.run(now=et(2026, 10, 12, 8, 0), root=root)
            self.assertTrue(r['failed'])
            self.assertEqual(len(path.read_text().splitlines()), 1)     # nothing appended
            self.assertNotIn('forward', r)
            with self.assertRaises(ValueError):
                hilo.append_record({'ticker': 'X'}, path)

    def test_failure_marks_page_state_stale(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self.root(tmp)
            hilo.run(now=et(2026, 10, 9, 8, 0), root=root)
            hilo.mark_failed('boom', root=root)
            out = json.loads((root / hilo.OUT).read_text())
            self.assertTrue(out['stale'])
            self.assertEqual(out['failed']['reason'], 'boom')

    def test_other_model_records_are_not_mixed_in(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self.root(tmp, today=synthetic_bars(date(2026, 10, 9), 103))
            hilo.run(now=et(2026, 10, 9, 8, 0), root=root)
            first = hilo.read_ledger(root / hilo.LEDGER)[0]
            other = {k: v for k, v in first.items() if k not in ('id', 'prevHash')}
            other['model'] = 'hilo-0'
            hilo.append_record(other, root / hilo.LEDGER)
            r = hilo.run(now=et(2026, 10, 9, 17, 0), root=root)
            self.assertEqual(r['otherModelRecords'], 1)
            self.assertEqual(r['forward']['premarket']['high']['n'], 1)

    def test_multimodal_time_reports_mode_and_window_separately(self):
        bins = list(range(570, 960, 15))
        b = hilo.time_block([570] * 10 + [945] * 10, bins)
        self.assertEqual(b['time'], '09:30')                       # tie goes to the earliest bar
        self.assertEqual(b['pBar'], 0.5)
        self.assertEqual(b['window']['p60'], 0.5)
        self.assertEqual({x['time'] for x in b['topBins']}, {'09:30', '15:45'})

    def test_intraday_time_distribution_includes_already_set_mass(self):
        day = date(2026, 10, 9)
        store = build_store(sessions_before(day, 30))
        today = synthetic_bars(day, 103, hi_bar=1, lo_bar=3)[:4]
        f, _ = hilo.intraday_forecast(store['TST'], day, today)
        for side in ('high', 'low'):
            blk = f[side]
            total = sum(x['p'] for x in blk['topBins'])
            self.assertLessEqual(total, 1.0001)
            obs_t = f['observed'][side + 'Time']
            got = next((x['p'] for x in blk['topBins'] if x['time'] == obs_t), 0)
            self.assertGreaterEqual(got + 1e-9, blk['pAlreadySet'] if blk['time'] == obs_t else 0)
            self.assertLessEqual(blk['window']['p60'], 1)

    def test_malformed_bars_leave_session_incomplete(self):
        day = date(2026, 10, 8)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'X_15m.csv'
            bars = synthetic_bars(day, 100)
            write_csv(path, {day: bars})
            lines = path.read_text().splitlines()
            lines[3] = lines[3].rsplit(',', 4)[0] + ',nan,99,100,0'     # non-finite high
            lines[5] = lines[5].rsplit(',', 4)[0] + ',101,90,110,0'     # low above high
            path.write_text('\n'.join(lines) + '\n')
            days = hilo.read_bars_csv(path)
            self.assertEqual(len(days[day]), len(bars) - 2)
            store = {}
            hilo.update_store(store, 'X', days, et(2026, 10, 9, 9, 0))
            self.assertNotIn('2026-10-08', store['X'])


class HistoryTests(unittest.TestCase):
    def test_scored_history_and_per_model_results(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'tickers.txt').write_text('TST\n')
            day = date(2026, 10, 9)
            days = sessions_before(day, 30)
            bars = {d: synthetic_bars(d, 100 + i * 0.1) for i, d in enumerate(days)}
            bars[day] = synthetic_bars(day, 103)
            write_csv(root / 'TST_15m.csv', bars)
            hilo.run(now=et(2026, 10, 9, 8, 0), root=root)
            r = hilo.run(now=et(2026, 10, 9, 17, 0), root=root)
            self.assertEqual(len(r['history']), 2)                   # high and low of one premarket record
            row = r['history'][0]
            for k in ('pred', 'actual', 'predTime', 'actualTime', 'err', 'model'):
                self.assertIn(k, row)
            self.assertEqual(list(r['forwardByModel']), [hilo.MODEL])
            self.assertEqual(r['forwardByModel'][hilo.MODEL]['premarket']['high']['n'], 1)


class CoherentTimingTests(unittest.TestCase):
    def test_marginal_modes_both_at_open_become_distinct_early_late(self):
        bins = list(range(570, 960, 15))
        pairs = [(570, 945)] * 10 + [(945, 570)] * 10          # half high-first, half low-first
        t = hilo.timing_block(pairs, bins)
        self.assertEqual((t['early']['time'], t['late']['time']), ('09:30', '15:45'))
        self.assertEqual(t['pHighFirst'], 0.5)
        self.assertFalse(t['resolved'])                          # order is a coin flip: not called
        out = {'high': {'time': '09:30'}, 'low': {'time': '09:30'}}
        hilo.apply_timing(out, pairs, bins)
        # unresolved: the early/late bars are NOT attached to high or low
        self.assertEqual(out['high']['timeBasis'], 'marginal mode')
        self.assertEqual(out['timing']['n'], 20)

    def test_order_called_only_when_history_agrees(self):
        bins = list(range(570, 960, 15))
        t = hilo.timing_block([(600, 900)] * 14 + [(900, 600)] * 6, bins)
        self.assertTrue(t['resolved'])
        self.assertEqual(t['pHighFirst'], 0.7)

    def test_forecasts_time_early_and_late_extremes_separately(self):
        day = date(2026, 10, 9)
        store = build_store(sessions_before(day, 30))
        f, _ = hilo.premarket_forecast(store['TST'], day)
        self.assertNotEqual(f['timing']['early']['time'], f['timing']['late']['time'])
        self.assertTrue(f['timing']['resolved'])                   # synthetic highs always come first
        self.assertEqual(f['high']['timeBasis'], 'order-assigned')
        self.assertNotEqual(f['high']['time'], f['low']['time'])
        g, _ = hilo.intraday_forecast(store['TST'], day, synthetic_bars(day, 103, hi_bar=1, lo_bar=3)[:4])
        self.assertNotEqual(g['timing']['early']['time'], g['timing']['late']['time'])

    def test_period_actuals_use_only_completed_days_in_period(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'X_daily.csv'
            rows = [('2026-09-30', 120, 90), ('2026-10-01', 110, 100), ('2026-10-05', 115, 95),
                    ('2026-10-08', 112, 99), ('2026-10-09', 999, 1)]      # 10/09 is the target day: excluded
            path.write_text('Datetime,Open,High,Low,Close,Volume\n' + ''.join(
                f'{d} 00:00:00-04:00,100,{h},{l},100,0\n' for d, h, l in rows))
            pa = hilo.period_actuals(path, date(2026, 10, 9))
            self.assertEqual(pa['W']['high'], {'price': 115.0, 'date': '2026-10-05'})
            self.assertEqual(pa['M']['low'], {'price': 95.0, 'date': '2026-10-05'})
            self.assertEqual(pa['Y']['high'], {'price': 120.0, 'date': '2026-09-30'})


class TimingSupportTests(unittest.TestCase):
    bins = list(range(570, 960, 15))

    def test_same_bar_evidence_is_allowed_not_replaced_by_an_unsupported_bar(self):
        t = hilo.timing_block([(570, 570)] * 12 + [(570, 600)] * 3, self.bins)
        self.assertEqual((t['early']['time'], t['late']['time']), ('09:30', '09:30'))
        self.assertGreater(t['late']['pBar'], 0)                 # never a zero-support time
        self.assertEqual(t['pSameBar'], 0.8)

    def test_late_mode_before_early_mode_is_flagged_not_reported_as_an_order(self):
        # early mostly 10:30, late mostly 10:00: the two modes reverse
        pairs = [(630, 645)] * 6 + [(570, 600)] * 3 + [(600, 990 - 30)] * 5
        t = hilo.timing_block(pairs, self.bins)
        if t['late']['time'] < t['early']['time']:
            self.assertFalse(t['consistent'])
            self.assertFalse(t['resolved'])

    def test_every_reported_bar_has_support(self):
        import random
        rng = random.Random(3)
        for _ in range(200):
            pairs = [tuple(rng.choice(self.bins) for _ in range(2)) for _ in range(rng.randint(5, 40))]
            t = hilo.timing_block(pairs, self.bins)
            self.assertGreater(t['early']['pBar'], 0)
            self.assertGreater(t['late']['pBar'], 0)


class ReviewB1Regressions(unittest.TestCase):
    """Exact reproductions from the 2026-10-09 review of 180ab1e."""
    bins = list(range(570, 960, 15))

    def test_all_same_bar_pairs_keep_late_on_its_supported_bar(self):
        t = hilo.timing_block([(600, 600)] * 20, self.bins)
        self.assertEqual((t['early']['time'], t['late']['time']), ('10:00', '10:00'))
        self.assertEqual((t['early']['pBar'], t['late']['pBar']), (1.0, 1.0))
        self.assertFalse(t['resolved'])                         # one bar for both: no order to call

    def test_mixed_pairs_do_not_produce_a_reversed_resolved_order(self):
        t = hilo.timing_block([(600, 600)] * 11 + [(570, 585)] * 9, self.bins)
        self.assertGreaterEqual(t['late']['time'], t['early']['time'])
        self.assertGreater(t['late']['pBar'], 0)
        if t['late']['time'] == t['early']['time']:
            self.assertFalse(t['resolved'])


    def test_all_high_first_pairs_give_a_supported_ordered_pair(self):
        pairs = [(600, 615)] * 3 + [(600, 630)] * 3 + [(600, 645)] * 3 + [(600, 660)] * 3 + [(570, 585)] * 8
        t = hilo.timing_block(pairs, self.bins)
        self.assertEqual((t['early']['time'], t['late']['time']), ('09:30', '09:45'))
        self.assertEqual(t['pPair'], 0.4)
        self.assertEqual(t['pHighFirst'], 1.0)
        self.assertTrue(t['resolved'])
        self.assertLess(t['early']['time'], t['late']['time'])


if __name__ == '__main__':
    unittest.main()
