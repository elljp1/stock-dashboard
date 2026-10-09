"""Daily high/low forecaster: four outputs per stock and session.

High price, high time, low price and low time, each with its uncertainty.

Two kinds of record are written, and both are frozen once written:
- premarket: issued before the target session opens, from completed sessions only;
- intraday: a revision for the rest of today's session, from today's completed
  15-minute bars so far plus earlier completed sessions.

Records go to an append-only, hash-chained ledger (hilo_ledger.jsonl) with the
issue time and the data cutoff. They are scored only after the session is
complete (every regular-hours bar present, per the NYSE calendar including
half-days), against paired baselines built from the same information.

Model hilo-1 is the simple walk-forward rule that beat the legacy forecasts in
the 2026-10-09 audit, with empirical uncertainty added. It is a baseline to
improve on, not a claimed edge.
"""
import csv
import hashlib
import json
import os
import random
from datetime import datetime, timedelta, timezone
from pathlib import Path
from statistics import median

import market_calendar as cal
from market_time import EASTERN

MODEL = 'hilo-1'
LEDGER = 'hilo_ledger.jsonl'
SESSIONS = 'hilo_sessions.json'
OUT = 'hilo.json'
BAR_MIN = 15
MEDIAN_SESSIONS = 20      # price point: median move over the last 20 sessions
HISTORY_SESSIONS = 60     # bands and time distribution: up to the last 60
MIN_HISTORY = 20
WINDOW_MIN = 60           # "near" for time: within +/- 60 minutes
FORWARD_SESSIONS_NEEDED = 20
BOOT = 2000
# Intraday revisions are frozen at these completed-bar counts (10:00, 10:30, 11:30,
# 12:45, 14:00 and 15:00 on a full day) to keep the public ledger small.
CHECKPOINTS = (2, 4, 8, 13, 18, 22)


# ---------------------------------------------------------------- bars

def minutes(hhmm):
    h, m = hhmm.split(':')
    return int(h) * 60 + int(m)


def hhmm(mins):
    return f'{mins // 60:02d}:{mins % 60:02d}'


def read_bars_csv(path):
    """15-minute bars from fetch_data.py's CSV -> {date: [(HH:MM, high, low, close)]}."""
    days = {}
    with open(path, newline='', encoding='utf-8') as f:
        for row in csv.DictReader(f):
            try:
                ts = datetime.fromisoformat(row['Datetime']).astimezone(EASTERN)
                bar = (ts.strftime('%H:%M'), float(row['High']), float(row['Low']), float(row['Close']))
            except (KeyError, ValueError):
                continue
            days.setdefault(ts.date(), []).append(bar)
    return {d: sorted(b) for d, b in days.items()}


def regular_bars(day, bars):
    """Only bars that start inside the regular session; None if the calendar is unknown."""
    if not cal.known(day):
        return None
    bounds = cal.session_bounds(day)
    if bounds is None:
        return []
    lo, hi = minutes(bounds[0].strftime('%H:%M')), minutes(bounds[1].strftime('%H:%M'))
    return [b for b in bars if lo <= minutes(b[0]) < hi]


def contiguous_from_open(day, bars):
    """Number of leading bars that run without a gap from the open."""
    start = minutes(cal.session_bounds(day)[0].strftime('%H:%M'))
    n = 0
    for b in bars:
        if minutes(b[0]) != start + n * BAR_MIN:
            break
        n += 1
    return n


def complete_session(day, bars, now):
    """True when the session has closed and every expected bar is present."""
    bounds = cal.session_bounds(day)
    if bounds is None or now < bounds[1]:
        return False
    exp = cal.expected_bars(day, BAR_MIN)
    return len(bars) == exp and contiguous_from_open(day, bars) == exp


def update_store(store, ticker, days, now):
    """Add newly completed sessions. A stored session is never rewritten."""
    tick = store.setdefault(ticker, {})
    added = revised = 0
    for day, bars in sorted(days.items()):
        reg = regular_bars(day, bars)
        if not reg or not complete_session(day, reg, now):
            continue
        key = day.isoformat()
        rec = [[t, round(h, 4), round(l, 4), round(c, 4)] for t, h, l, c in reg]
        if key in tick:
            old = tick[key]['bars']
            if max(abs(a[1] - b[1]) / b[1] for a, b in zip(rec, old)) > 0.001:
                tick[key]['providerRevisions'] = tick[key].get('providerRevisions', 0) + 1
                revised += 1
            continue
        tick[key] = {'bars': rec, 'expected': cal.expected_bars(day, BAR_MIN),
                     'storedAt': now.astimezone(timezone.utc).isoformat(timespec='seconds')}
        added += 1
    return added, revised


def extremes(bars):
    hi = max(bars, key=lambda b: b[1])
    lo = min(bars, key=lambda b: b[2])
    return {'high': hi[1], 'highTime': hi[0], 'low': lo[2], 'lowTime': lo[0], 'close': bars[-1][3]}


# ---------------------------------------------------------------- model

def quantile(values, q):
    s = sorted(values)
    if not s:
        return None
    pos = (len(s) - 1) * q
    i = int(pos)
    j = min(i + 1, len(s) - 1)
    return s[i] + (s[j] - s[i]) * (pos - i)


def best_time(times, bins):
    """Bin whose +/-60 minute window holds the most of `times` (ties: nearest overall, then earliest)."""
    if not times or not bins:
        return None
    return max(bins, key=lambda c: (sum(abs(c - m) <= WINDOW_MIN for m in times),
                                    -sum(abs(c - m) for m in times), -c))


def session_bins(day):
    o, c = cal.session_bounds(day)
    start, end = minutes(o.strftime('%H:%M')), minutes(c.strftime('%H:%M'))
    return list(range(start, end, BAR_MIN))


def history_before(store_t, day, n=HISTORY_SESSIONS):
    keys = sorted(k for k in store_t if k < day.isoformat())
    return keys[-n:], keys


def daily_moves(store_t, keys, all_keys):
    """(session, high/prevClose-1, low/prevClose-1, highMin, lowMin) where the previous session is stored."""
    out = []
    for k in keys:
        i = all_keys.index(k)
        if i == 0:
            continue
        prev = all_keys[i - 1]
        if prev != cal.previous_session(cal.as_date(k)).isoformat():
            continue
        pc = store_t[prev]['bars'][-1][3]
        e = extremes(store_t[k]['bars'])
        out.append((k, e['high'] / pc - 1, e['low'] / pc - 1, minutes(e['highTime']), minutes(e['lowTime'])))
    return out


def price_block(point, lo, hi, digits=2):
    return {'price': round(point, digits), 'lo': round(lo, digits), 'hi': round(hi, digits)}


def time_block(point, times, bins):
    within = lambda w: round(sum(abs(point - m) <= w for m in times) / len(times), 3) if times else None
    top = sorted(((sum(1 for m in times if b <= m < b + BAR_MIN), b) for b in bins), reverse=True)[:3]
    return {'time': hhmm(point), 'p60': within(WINDOW_MIN), 'p30': within(30),
            'topBins': [{'time': hhmm(b), 'p': round(c / len(times), 3)} for c, b in top if c]}


def premarket_forecast(store_t, day):
    """Forecast for `day` from completed sessions before it, or (None, reason)."""
    keys, all_keys = history_before(store_t, day)
    prev = cal.previous_session(day).isoformat()
    if not all_keys or all_keys[-1] != prev:
        return None, f'prior session {prev} not complete in store'
    moves = daily_moves(store_t, keys, all_keys)
    if len(moves) < MIN_HISTORY:
        return None, f'only {len(moves)} usable history sessions (need {MIN_HISTORY})'
    anchor = store_t[prev]['bars'][-1][3]
    recent = moves[-MEDIAN_SESSIONS:]
    bins = session_bins(day)
    ups, dns = [m[1] for m in moves], [m[2] for m in moves]
    hi_t, lo_t = [m[3] for m in moves], [m[4] for m in moves]
    hi_point = anchor * (1 + median(m[1] for m in recent))
    lo_point = anchor * (1 + median(m[2] for m in recent))
    high = price_block(hi_point, anchor * (1 + quantile(ups, 0.1)), anchor * (1 + quantile(ups, 0.9)))
    low = price_block(lo_point, anchor * (1 + quantile(dns, 0.1)), anchor * (1 + quantile(dns, 0.9)))
    high.update(time_block(best_time(hi_t, bins), hi_t, bins))
    low.update(time_block(best_time(lo_t, bins), lo_t, bins))
    cutoff = cal.session_bounds(cal.as_date(prev))[1]
    return {'anchor': round(anchor, 4), 'anchorKind': 'prior close', 'high': high, 'low': low,
            'history': {'n': len(moves), 'from': moves[0][0], 'to': moves[-1][0]},
            'dataCutoff': cutoff.isoformat(), 'lastBar': f'{prev} {store_t[prev]["bars"][-1][0]}'}, None


def intraday_forecast(store_t, day, today_bars):
    """Rest-of-session revision after len(today_bars) completed bars, or (None, reason)."""
    k = len(today_bars)
    exp = cal.expected_bars(day, BAR_MIN)
    if k == 0 or k >= exp:
        return None, 'no completed bars yet' if k == 0 else 'session complete'
    if contiguous_from_open(day, today_bars) != k:
        return None, 'gap in today\'s bars'
    keys, all_keys = history_before(store_t, day)
    if len(keys) < MIN_HISTORY:
        return None, f'only {len(keys)} history sessions (need {MIN_HISTORY})'
    close_min = minutes(cal.session_bounds(day)[1].strftime('%H:%M'))
    seen = extremes(today_bars)
    last = today_bars[-1][3]
    last_min = minutes(today_bars[-1][0])
    r_up, r_dn, up_t, dn_t = [], [], [], []
    for key in keys:
        bars = [b for b in store_t[key]['bars'] if minutes(b[0]) < close_min]
        if len(bars) <= k:
            continue
        ref, rest = bars[k - 1][3], bars[k:]
        hi_b = max(rest, key=lambda b: b[1])
        lo_b = min(rest, key=lambda b: b[2])
        r_up.append(hi_b[1] / ref - 1)
        r_dn.append(lo_b[2] / ref - 1)
        up_t.append(minutes(hi_b[0]))
        dn_t.append(minutes(lo_b[0]))
    if len(r_up) < MIN_HISTORY:
        return None, f'only {len(r_up)} history sessions reach bar {k}'
    bins = [b for b in session_bins(day) if b > last_min]
    out = {'anchor': round(last, 4), 'anchorKind': 'last completed bar close',
           'observed': {'high': seen['high'], 'highTime': seen['highTime'],
                        'low': seen['low'], 'lowTime': seen['lowTime'], 'bars': k},
           'history': {'n': len(r_up), 'from': keys[0], 'to': keys[-1]}}
    for side, rs, ts, obs, obs_t, better in (
            ('high', r_up, up_t, seen['high'], seen['highTime'], max),
            ('low', r_dn, dn_t, seen['low'], seen['lowTime'], min)):
        cands = [better(obs, last * (1 + r)) for r in rs]
        p_set = sum(c == obs for c in cands) / len(cands)
        block = price_block(median(cands), quantile(cands, 0.1), quantile(cands, 0.9))
        later_t = [t for t, c in zip(ts, cands) if c != obs]
        if p_set >= 0.5 or not later_t:
            block.update({'time': obs_t, 'p60': round(p_set, 3), 'p30': round(p_set, 3), 'topBins': []})
        else:
            tb = time_block(best_time(later_t, bins), later_t, bins)
            tb['p60'] = round((1 - p_set) * tb['p60'], 3)
            tb['p30'] = round((1 - p_set) * tb['p30'], 3)
            block.update(tb)
        block['pAlreadySet'] = round(p_set, 3)
        out[side] = block
    end = datetime.combine(day, datetime.strptime(today_bars[-1][0], '%H:%M').time(), EASTERN) + timedelta(minutes=BAR_MIN)
    out['dataCutoff'] = end.isoformat()
    out['lastBar'] = f'{day.isoformat()} {today_bars[-1][0]}'
    return out, None


# ---------------------------------------------------------------- ledger

def _sha(text):
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


def read_ledger(path=LEDGER):
    p = Path(path)
    if not p.exists():
        return []
    return [json.loads(line) for line in p.read_text(encoding='utf-8').splitlines() if line.strip()]


def verify_ledger(path=LEDGER):
    """Check the hash chain: each line names the hash of the line before it."""
    p = Path(path)
    if not p.exists():
        return {'ok': True, 'records': 0}
    prev = '0' * 64
    lines = [line for line in p.read_text(encoding='utf-8').splitlines() if line.strip()]
    for i, line in enumerate(lines):
        rec = json.loads(line)
        if rec.get('prevHash') != prev:
            return {'ok': False, 'records': len(lines), 'firstBad': i}
        body = {k: v for k, v in rec.items() if k != 'id'}
        if rec.get('id') != _sha(json.dumps(body, sort_keys=True))[:16]:
            return {'ok': False, 'records': len(lines), 'firstBad': i}
        prev = _sha(line)
    return {'ok': True, 'records': len(lines)}


def append_record(rec, path=LEDGER):
    """Append one record, chained to the previous line. Never edits existing lines."""
    p = Path(path)
    prev = '0' * 64
    if p.exists():
        lines = [line for line in p.read_text(encoding='utf-8').splitlines() if line.strip()]
        if lines:
            prev = _sha(lines[-1])
    rec = dict(rec, prevHash=prev)
    rec['id'] = _sha(json.dumps(rec, sort_keys=True))[:16]
    line = json.dumps(rec, sort_keys=True)
    with open(p, 'a', encoding='utf-8') as f:
        f.write(line + '\n')
    return rec


def record_key(rec):
    return (rec['ticker'], rec['session'], rec['kind'], rec.get('checkpoint'))


def checkpoint(k):
    passed = [c for c in CHECKPOINTS if c <= k]
    return passed[-1] if passed else None


# ---------------------------------------------------------------- evaluation

def _err(pred, actual):
    return abs(pred - actual) / actual * 100


def score_rows(ledger, store, legacy=None):
    """One row per ledger record per side whose session is complete, with paired baselines."""
    rows = []
    for rec in ledger:
        st = store.get(rec['ticker'], {})
        sess = st.get(rec['session'])
        if not sess:
            continue
        issued = datetime.fromisoformat(rec['issuedAt'])
        cutoff = datetime.fromisoformat(rec['dataCutoff'])
        open_ = cal.session_bounds(cal.as_date(rec['session']))[0]
        if cutoff > issued or (rec['kind'] == 'premarket' and issued >= open_):
            continue                                  # fails the issue/cutoff gate
        actual = extremes(sess['bars'])
        keys = sorted(k for k in st if k < rec['session'])
        prev = st[keys[-1]] if keys else None
        for side in ('high', 'low'):
            f = rec[side]
            a_p, a_t = actual[side], minutes(actual[side + 'Time'])
            row = {'ticker': rec['ticker'], 'session': rec['session'], 'kind': rec['kind'], 'side': side,
                   'err': _err(f['price'], a_p), 'inBand': f['lo'] <= a_p <= f['hi'],
                   'tErr': abs(minutes(f['time']) - a_t)}
            if rec['kind'] == 'premarket':
                if prev and keys[-1] == cal.previous_session(cal.as_date(rec['session'])).isoformat():
                    row['naiveErr'] = _err(extremes(prev['bars'])[side], a_p)
                row['openTErr'] = abs(minutes(cal.session_bounds(cal.as_date(rec['session']))[0].strftime('%H:%M')) - a_t)
                lg = (legacy or {}).get((rec['ticker'], rec['session'], side))
                if lg:
                    row['legacyErr'] = _err(lg['price'], a_p)
                    if lg.get('min') is not None:
                        row['legacyTErr'] = abs(lg['min'] - a_t)
            else:
                obs = rec['observed']
                row['naiveErr'] = _err(obs[side], a_p)          # "the extreme so far stands"
                row['openTErr'] = abs(minutes(obs[side + 'Time']) - a_t)
                row['hour'] = rec['lastBar'][-5:-3]
            rows.append(row)
    return rows


def _boot_ci(rows, fn, seed=1):
    by = {}
    for r in rows:
        by.setdefault(r['session'], []).append(r)
    days = sorted(by)
    if len(days) < 2:
        return None
    rng = random.Random(seed)
    vals = sorted(fn([r for d in rng.choices(days, k=len(days)) for r in by[d]]) for _ in range(BOOT))
    return [round(vals[int(0.025 * BOOT)], 3), round(vals[int(0.975 * BOOT)], 3)]


def summarize(rows):
    """Paired summary: model and baselines on exactly the same rows."""
    if not rows:
        return {'n': 0}
    pr = [r for r in rows if 'naiveErr' in r]
    med = lambda k, rs: round(median(r[k] for r in rs), 3) if rs else None
    rate = lambda pred, rs: round(100 * sum(1 for r in rs if pred(r)) / len(rs), 1) if rs else None
    out = {'n': len(rows), 'sessions': len({r['session'] for r in rows}),
           'from': min(r['session'] for r in rows), 'to': max(r['session'] for r in rows),
           'price': {'model': med('err', rows), 'within05': rate(lambda r: r['err'] <= 0.5, rows),
                     'within1': rate(lambda r: r['err'] <= 1, rows), 'bandCoverage': rate(lambda r: r['inBand'], rows)},
           'time': {'within30': rate(lambda r: r['tErr'] <= 30, rows), 'within60': rate(lambda r: r['tErr'] <= 60, rows),
                    'medianMin': med('tErr', rows)}}
    if pr:
        mean = lambda k, rs: round(sum(r[k] for r in rs) / len(rs), 3)
        out['price'].update(pairedN=len(pr), naive=med('naiveErr', pr), modelSameRows=med('err', pr),
                            meanModel=mean('err', pr), meanNaive=mean('naiveErr', pr),
                            diffCI=_boot_ci(pr, lambda s: median(r['err'] - r['naiveErr'] for r in s)),
                            meanDiffCI=_boot_ci(pr, lambda s: sum(r['err'] - r['naiveErr'] for r in s) / len(s)))
    tr = [r for r in rows if 'openTErr' in r]
    if tr:
        out['time'].update(pairedN=len(tr), baseline60=rate(lambda r: r['openTErr'] <= 60, tr),
                           model60SameRows=rate(lambda r: r['tErr'] <= 60, tr),
                           diffCI=_boot_ci(tr, lambda s: 100 * (sum(r['tErr'] <= 60 for r in s)
                                                                - sum(r['openTErr'] <= 60 for r in s)) / len(s)))
    lg = [r for r in rows if 'legacyErr' in r]
    if lg:
        out['legacy'] = {'n': len(lg), 'legacyPrice': med('legacyErr', lg), 'modelPrice': med('err', lg)}
        lt = [r for r in lg if 'legacyTErr' in r]
        if lt:
            out['legacy'].update(timeN=len(lt), legacy60=rate(lambda r: r['legacyTErr'] <= 60, lt),
                                 model60=rate(lambda r: r['tErr'] <= 60, lt))
    return out


def board(rows):
    out = {}
    for kind in ('premarket', 'intraday'):
        out[kind] = {s: summarize([r for r in rows if r['kind'] == kind and r['side'] == s]) for s in ('high', 'low')}
    return out


def forward_status(fwd):
    """Per output: forward-proven only with enough sessions and a paired interval that excludes zero."""
    st = {}
    for side in ('high', 'low'):
        s = fwd['premarket'][side]
        n = s.get('sessions', 0)
        p_ci = s.get('price', {}).get('diffCI')
        t_ci = s.get('time', {}).get('diffCI')
        st[f'{side}Price'] = {'sessions': n, 'needed': FORWARD_SESSIONS_NEEDED,
                              'proven': bool(n >= FORWARD_SESSIONS_NEEDED and p_ci and p_ci[1] < 0
                                             and (s['price'].get('meanDiffCI') or [0, 0])[1] < 0)}
        st[f'{side}Time'] = {'sessions': n, 'needed': FORWARD_SESSIONS_NEEDED,
                             'proven': bool(n >= FORWARD_SESSIONS_NEEDED and t_ci and t_ci[0] > 0)}
    return st


def retrospective(store, checkpoints=(4, 8, 13, 18)):
    """Walk-forward replay over stored sessions. Not frozen in advance: labeled retrospective."""
    recs = []
    for ticker, st in store.items():
        for key in sorted(st):
            day = cal.as_date(key)
            sub = {k: v for k, v in st.items() if k < key}
            f, _ = premarket_forecast(sub, day)
            if f:
                recs.append(dict(f, ticker=ticker, session=key, kind='premarket',
                                 issuedAt=f['dataCutoff']))
            for k in checkpoints:
                bars = [tuple(b) for b in st[key]['bars'][:k]]
                g, _ = intraday_forecast(sub, day, bars)
                if g:
                    recs.append(dict(g, ticker=ticker, session=key, kind='intraday', issuedAt=g['dataCutoff']))
    return board(score_rows(recs, store))


def legacy_calls(path='horizons_log.json'):
    """First logged legacy daily call per ticker/session/side, logged before the session."""
    try:
        entries = json.loads(Path(path).read_text(encoding='utf-8'))['entries']
    except Exception:
        return {}
    from horizon_scoreboard import clock_minutes
    out = {}
    for e in sorted(entries, key=lambda e: e['logged']):
        if e['logged'] >= e['session']:
            continue
        for side in ('high', 'low'):
            c = ((e.get('h') or {}).get('daily') or {}).get(side)
            if isinstance(c, dict) and c.get('price') and c.get('src') != 'actual':
                out.setdefault((e['ticker'], e['session'], side),
                               {'price': c['price'], 'min': clock_minutes(c.get('time'))})
    return out


# ---------------------------------------------------------------- run

def tickers(path='tickers.txt'):
    names = [t.strip().upper() for t in Path(path).read_text().splitlines() if t.strip()]
    return [t for t in names if '=' not in t], [t for t in names if '=' in t]


def run(now=None, root='.'):
    now = now or datetime.now(timezone.utc)
    root = Path(root)
    store_path = root / SESSIONS
    store = json.loads(store_path.read_text()) if store_path.exists() else {}
    ledger_path = root / LEDGER
    ledger = read_ledger(ledger_path)
    have = {record_key(r) for r in ledger}
    equities, excluded = tickers(root / 'tickers.txt')
    day, kind = cal.target_session(now)
    issued = now.astimezone(timezone.utc).isoformat(timespec='seconds')
    notes, latest = {}, {}
    for t in equities:
        path = root / f'{t}_15m.csv'
        if not path.exists():
            notes[t] = 'no 15-minute bars downloaded'
            continue
        days = read_bars_csv(path)
        update_store(store, t, days, now)
        st = store.get(t, {})
        if kind == 'premarket':
            f, why = premarket_forecast(st, day)
        else:
            reg = regular_bars(day, days.get(day, [])) or []
            done = [b for b in reg if datetime.combine(day, datetime.strptime(b[0], '%H:%M').time(), EASTERN)
                    + timedelta(minutes=BAR_MIN) <= now.astimezone(EASTERN)]
            cp = checkpoint(len(done))
            f, why = intraday_forecast(st, day, done) if cp else (None, 'before the first intraday checkpoint')
            if f:
                f['checkpoint'] = cp
        if not f:
            notes[t] = why
            continue
        rec = dict(f, v=1, model=MODEL, ticker=t, session=day.isoformat(), kind=kind, issuedAt=issued)
        if datetime.fromisoformat(rec['dataCutoff']) > now:
            notes[t] = 'data cutoff after issue time; not recorded'
            continue
        if record_key(rec) not in have:
            rec = append_record(rec, ledger_path)
            ledger.append(rec)
            have.add(record_key(rec))
    store_path.write_text(json.dumps(store, separators=(',', ':')) + '\n')
    for rec in ledger:
        if rec['session'] == day.isoformat():
            slot = latest.setdefault(rec['ticker'], {})
            if rec['kind'] == 'intraday' or 'premarket' not in slot:
                slot[rec['kind']] = rec              # first premarket call, latest intraday revision
    fwd = board(score_rows(ledger, store, legacy_calls(root / 'horizons_log.json')))
    report = {
        'generatedAt': issued, 'model': MODEL, 'targetSession': day.isoformat(), 'kind': kind,
        'method': (f'Price: prior close x (1 + median move to the high/low over the last {MEDIAN_SESSIONS} '
                   f'sessions); band = 10th-90th percentile of that move over up to {HISTORY_SESSIONS} sessions. '
                   f'Time: the 15-minute bar whose +/-{WINDOW_MIN} min window held the most highs/lows over up to '
                   f'{HISTORY_SESSIONS} sessions; p60 = share of those sessions inside that window. Intraday '
                   'revisions condition on the bars so far: they replay the rest of each earlier session from the '
                   'same bar. Regular session only; NYSE holidays and half-days applied.'),
        'latest': latest, 'notes': notes,
        'excluded': {t: 'futures session calendar not implemented' for t in excluded},
        'ledger': verify_ledger(ledger_path),
        'storedSessions': {t: len(v) for t, v in store.items()},
        'forward': fwd, 'status': forward_status(fwd),
        'retrospective': retrospective(store),
        'build': {'commit': os.environ.get('GITHUB_SHA', 'local'), 'run': os.environ.get('GITHUB_RUN_ID')},
    }
    (root / OUT).write_text(json.dumps(report, indent=1) + '\n')
    return report


def main():
    report = run()
    print('hilo:', report['kind'], report['targetSession'], 'ledger', report['ledger'],
          'notes', report['notes'] or 'none')
    for kind in ('premarket', 'intraday'):
        for side in ('high', 'low'):
            print('retrospective', kind, side, json.dumps(report['retrospective'][kind][side])[:300])


if __name__ == '__main__':
    main()
