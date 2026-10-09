"""Daily high/low forecaster: four outputs per stock and session.

High price, high time, low price and low time, each with its uncertainty.

Two kinds of record are written, and both are frozen once written:
- premarket: issued before the target session opens, from completed sessions only;
- intraday: a revision of today's FINAL full-session high and low (including what
  has already traded), frozen at fixed checkpoints from exactly the first N
  completed 15-minute bars plus earlier completed sessions.

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
import math
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
MAX_LAG_MIN = 20           # intraday records issued later than this after their cutoff are "late"
BOOT = 2000
# Intraday revisions are frozen at these completed-bar counts. On a full day the data
# cutoffs are 10:00, 10:30, 11:30, 12:45, 14:00 and 15:00. A record for checkpoint N
# uses exactly the first N bars, whatever time the run happens.
CHECKPOINTS = (2, 4, 8, 13, 18, 22)


# ---------------------------------------------------------------- bars

def minutes(hhmm):
    h, m = hhmm.split(':')
    return int(h) * 60 + int(m)


def hhmm(mins):
    return f'{mins // 60:02d}:{mins % 60:02d}'


def valid_bar(bar):
    """Finite, positive OHLC with low <= close <= high."""
    _, h, l, c = bar
    if not all(math.isfinite(v) and v > 0 for v in (h, l, c)):
        return False
    return l <= h and l - 1e-9 <= c <= h + 1e-9


def read_bars_csv(path):
    """15-minute bars from fetch_data.py's CSV -> {date: [(HH:MM, high, low, close)]}."""
    days = {}
    with open(path, newline='', encoding='utf-8') as f:
        for row in csv.DictReader(f):
            try:
                ts = datetime.fromisoformat(row['Datetime']).astimezone(EASTERN)
                bar = (ts.strftime('%H:%M'), float(row['High']), float(row['Low']), float(row['Close']))
            except (KeyError, ValueError, TypeError):
                continue
            if not valid_bar(bar):
                continue        # a dropped bar leaves its session incomplete, so it is never scored
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


def time_block(times, bins):
    """Whole distribution of the extreme's 15-minute bar over `times` (one entry per scenario).

    time   = the modal bar: the single most likely bar (ties: earliest), with pBar.
    window = a separate output: the centre of the +/-60 minute window that holds the
             most probability, with p60 (and p30 around that same centre). It is a
             window centre, not the most likely time.
    """
    n = len(times)
    counts = {b: sum(1 for m in times if b <= m < b + BAR_MIN) for b in bins}
    mode = max(bins, key=lambda b: (counts[b], -b))
    centre = best_time(times, bins)
    share = lambda c, w: round(sum(abs(c - m) <= w for m in times) / n, 3)
    top = sorted(((c, -b) for b, c in counts.items() if c), reverse=True)[:3]
    return {'time': hhmm(mode), 'pBar': round(counts[mode] / n, 3),
            'topBins': [{'time': hhmm(-b), 'p': round(c / n, 3)} for c, b in top],
            'window': {'centre': hhmm(centre), 'p60': share(centre, WINDOW_MIN), 'p30': share(centre, 30)}}


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
    high = price_block(anchor * (1 + median(m[1] for m in recent)),
                       anchor * (1 + quantile(ups, 0.1)), anchor * (1 + quantile(ups, 0.9)))
    low = price_block(anchor * (1 + median(m[2] for m in recent)),
                      anchor * (1 + quantile(dns, 0.1)), anchor * (1 + quantile(dns, 0.9)))
    high.update(time_block([m[3] for m in moves], bins))
    low.update(time_block([m[4] for m in moves], bins))
    cutoff = cal.session_bounds(cal.as_date(prev))[1]
    return {'target': f'full-session high and low of {day.isoformat()}',
            'anchor': round(anchor, 4), 'anchorKind': 'prior close', 'high': high, 'low': low,
            'history': {'n': len(moves), 'from': moves[0][0], 'to': moves[-1][0]},
            'dataCutoff': cutoff.isoformat(), 'lastBar': f'{prev} {store_t[prev]["bars"][-1][0]}'}, None


def intraday_forecast(store_t, day, today_bars):
    """Today's final full-session high/low given exactly `today_bars`, or (None, reason)."""
    k = len(today_bars)
    exp = cal.expected_bars(day, BAR_MIN)
    if k == 0 or k >= exp:
        return None, 'no completed bars yet' if k == 0 else 'session complete'
    if contiguous_from_open(day, today_bars) != k:
        return None, 'gap in today\'s bars'
    keys, _ = history_before(store_t, day)
    if len(keys) < MIN_HISTORY:
        return None, f'only {len(keys)} history sessions (need {MIN_HISTORY})'
    close_min = minutes(cal.session_bounds(day)[1].strftime('%H:%M'))
    seen = extremes(today_bars)
    last = today_bars[-1][3]
    scen = []                    # (rest-up move, rest-down move, rest-high bar, rest-low bar) per earlier session
    for key in keys:
        bars = [b for b in store_t[key]['bars'] if minutes(b[0]) < close_min]
        if len(bars) <= k:
            continue
        ref, rest = bars[k - 1][3], bars[k:]
        hi_b = max(rest, key=lambda b: b[1])
        lo_b = min(rest, key=lambda b: b[2])
        scen.append((hi_b[1] / ref - 1, lo_b[2] / ref - 1, minutes(hi_b[0]), minutes(lo_b[0])))
    if len(scen) < MIN_HISTORY:
        return None, f'only {len(scen)} history sessions reach bar {k}'
    bins = session_bins(day)
    out = {'target': f'final full-session high and low of {day.isoformat()}, including bars already traded',
           'anchor': round(last, 4), 'anchorKind': 'last completed bar close',
           'observed': {'high': seen['high'], 'highTime': seen['highTime'],
                        'low': seen['low'], 'lowTime': seen['lowTime'], 'bars': k},
           'history': {'n': len(scen), 'from': keys[0], 'to': keys[-1]}}
    for side, idx, obs, obs_t, better in (('high', 0, seen['high'], seen['highTime'], max),
                                          ('low', 1, seen['low'], seen['lowTime'], min)):
        cands, times = [], []
        for sc in scen:
            c = better(obs, last * (1 + sc[idx]))
            cands.append(c)
            # one scenario = one final extreme: either the one already traded, or a later one
            times.append(minutes(obs_t) if c == obs else sc[idx + 2])
        block = price_block(median(cands), quantile(cands, 0.1), quantile(cands, 0.9))
        block.update(time_block(times, bins))
        block['pAlreadySet'] = round(sum(c == obs for c in cands) / len(cands), 3)
        out[side] = block
    end = datetime.combine(day, datetime.strptime(today_bars[-1][0], '%H:%M').time(), EASTERN) + timedelta(minutes=BAR_MIN)
    out['dataCutoff'] = end.isoformat()
    out['lastBar'] = f'{day.isoformat()} {today_bars[-1][0]}'
    return out, None


# ---------------------------------------------------------------- ledger

def _sha(text):
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


def _lines(path):
    p = Path(path)
    return [line for line in p.read_text(encoding='utf-8').splitlines() if line.strip()] if p.exists() else []


def valid_record(rec):
    """Schema and sanity check for one ledger record."""
    try:
        if rec['kind'] not in ('premarket', 'intraday') or not rec.get('model'):
            return False
        issued = datetime.fromisoformat(rec['issuedAt'])
        cutoff = datetime.fromisoformat(rec['dataCutoff'])
        if issued.tzinfo is None or cutoff.tzinfo is None or cutoff > issued:
            return False
        cal.as_date(rec['session'])
        for side in ('high', 'low'):
            b = rec[side]
            vals = (b['price'], b['lo'], b['hi'])
            if not all(isinstance(v, (int, float)) and math.isfinite(v) and v > 0 for v in vals):
                return False
            if not b['lo'] <= b['price'] <= b['hi']:
                return False
            minutes(b['time'])
            minutes(b['window']['centre'])
        if rec['kind'] == 'intraday' and rec.get('checkpoint') not in CHECKPOINTS:
            return False
        return True
    except (KeyError, TypeError, ValueError, AttributeError):
        return False


def verify_ledger(path=LEDGER):
    """Chain and schema check. Catches edits, deletions (except of the newest lines) and
    reordering. A whole-file rewrite with a fresh chain needs an external anchor (Git)."""
    prev = '0' * 64
    lines = _lines(path)
    for i, line in enumerate(lines):
        try:
            rec = json.loads(line)
        except ValueError:
            return {'ok': False, 'records': len(lines), 'firstBad': i, 'why': 'unparseable line'}
        if rec.get('prevHash') != prev:
            return {'ok': False, 'records': len(lines), 'firstBad': i, 'why': 'chain broken'}
        body = {k: v for k, v in rec.items() if k != 'id'}
        if rec.get('id') != _sha(json.dumps(body, sort_keys=True))[:16]:
            return {'ok': False, 'records': len(lines), 'firstBad': i, 'why': 'record altered'}
        if not valid_record(rec):
            return {'ok': False, 'records': len(lines), 'firstBad': i, 'why': 'invalid record'}
        prev = _sha(line)
    return {'ok': True, 'records': len(lines)}


def read_ledger(path=LEDGER):
    return [json.loads(line) for line in _lines(path)]


def append_record(rec, path=LEDGER):
    """Append one record, chained to the previous line. Refuses to write onto an invalid ledger."""
    check = verify_ledger(path)
    if not check['ok']:
        raise ValueError(f'ledger invalid at line {check["firstBad"]}: {check["why"]}')
    lines = _lines(path)
    rec = dict(rec, prevHash=_sha(lines[-1]) if lines else '0' * 64)
    rec['id'] = _sha(json.dumps(rec, sort_keys=True))[:16]
    if not valid_record(rec):
        raise ValueError('refusing to append an invalid record')
    with open(path, 'a', encoding='utf-8') as f:
        f.write(json.dumps(rec, sort_keys=True) + '\n')
    return rec


def record_key(rec):
    return (rec['ticker'], rec['session'], rec['kind'], rec.get('checkpoint'))


def checkpoint(k):
    passed = [c for c in CHECKPOINTS if c <= k]
    return passed[-1] if passed else None


def lag_minutes(rec):
    return (datetime.fromisoformat(rec['issuedAt']) - datetime.fromisoformat(rec['dataCutoff'])).total_seconds() / 60


# ---------------------------------------------------------------- evaluation

def _err(pred, actual):
    return abs(pred - actual) / actual * 100


def score_rows(ledger, store, legacy=None, model=MODEL):
    """One row per record and side once its session is complete, with paired comparators.

    Only records of `model` that pass the issue/cutoff gates are scored. Intraday records
    issued more than MAX_LAG_MIN after their cutoff are kept in the ledger but not scored.
    """
    rows = []
    for rec in ledger:
        if rec.get('model') != model:
            continue
        st = store.get(rec['ticker'], {})
        sess = st.get(rec['session'])
        if not sess:
            continue
        day = cal.as_date(rec['session'])
        open_ = cal.session_bounds(day)[0]
        issued = datetime.fromisoformat(rec['issuedAt'])
        if datetime.fromisoformat(rec['dataCutoff']) > issued:
            continue
        if rec['kind'] == 'premarket' and issued >= open_:
            continue
        if rec['kind'] == 'intraday' and lag_minutes(rec) > MAX_LAG_MIN:
            continue
        actual = extremes(sess['bars'])
        keys = sorted(k for k in st if k < rec['session'])
        prior_ok = bool(keys) and keys[-1] == cal.previous_session(day).isoformat()
        for side in ('high', 'low'):
            f = rec[side]
            a_p, a_t = actual[side], minutes(actual[side + 'Time'])
            row = {'ticker': rec['ticker'], 'session': rec['session'], 'kind': rec['kind'], 'side': side,
                   'model': rec.get('model'), 'issuedAt': rec['issuedAt'], 'pred': f['price'], 'actual': a_p,
                   'predTime': f['time'], 'actualTime': actual[side + 'Time'],
                   'checkpoint': rec.get('checkpoint'), 'halfDay': cal.expected_bars(day) < 26,
                   'err': _err(f['price'], a_p), 'inBand': f['lo'] <= a_p <= f['hi'],
                   'barHit': minutes(f['time']) == a_t, 'tErr': abs(minutes(f['time']) - a_t),
                   'near60': abs(minutes(f['time']) - a_t) <= WINDOW_MIN,
                   'winHit': abs(minutes(f['window']['centre']) - a_t) <= WINDOW_MIN}
            if rec['kind'] == 'premarket':
                if prior_ok:
                    row['cmpErr'] = {'prior-day extreme': _err(extremes(st[keys[-1]]['bars'])[side], a_p)}
                o = minutes(open_.strftime('%H:%M'))
                # time comparators: the opening bar, and the best fixed +/-60 window over prior sessions
                row['cmpBar'] = {'opening bar': o == a_t}
                row['cmpWin'] = {'the open +/-60': abs(o - a_t) <= WINDOW_MIN,
                                 'prior-60 best fixed window': row['winHit']}
                lg = (legacy or {}).get((rec['ticker'], rec['session'], side))
                if lg:
                    row.setdefault('cmpErr', {})['legacy app'] = _err(lg['price'], a_p)
                    if lg.get('min') is not None:
                        row['cmpWin']['legacy app'] = abs(lg['min'] - a_t) <= WINDOW_MIN
            else:
                obs = rec['observed']
                row['cmpErr'] = {'extreme so far stands': _err(obs[side], a_p)}
                row['cmpBar'] = {'extreme so far stands': minutes(obs[side + 'Time']) == a_t}
                row['cmpWin'] = {'extreme so far stands': abs(minutes(obs[side + 'Time']) - a_t) <= WINDOW_MIN}
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


def _rate(rs, pred):
    return round(100 * sum(1 for r in rs if pred(r)) / len(rs), 1) if rs else None


def summarize(rows):
    """Model and every comparator on exactly the same rows; the strongest comparator is named."""
    if not rows:
        return {'n': 0}
    med = lambda vals: round(median(vals), 3)
    out = {'n': len(rows), 'sessions': len({r['session'] for r in rows}),
           'from': min(r['session'] for r in rows), 'to': max(r['session'] for r in rows),
           'price': {'model': med([r['err'] for r in rows]), 'within05': _rate(rows, lambda r: r['err'] <= 0.5),
                     'within1': _rate(rows, lambda r: r['err'] <= 1), 'bandCoverage': _rate(rows, lambda r: r['inBand'])},
           'timeBar': {'model': _rate(rows, lambda r: r['barHit']),
                       'within30': _rate(rows, lambda r: r['tErr'] <= 30), 'within60': _rate(rows, lambda r: r['tErr'] <= 60)},
           'timeNear': {'model': _rate(rows, lambda r: r['near60'])},
           'timeWindow': {'model': _rate(rows, lambda r: r['winHit'])}}
    names = sorted({k for r in rows for k, v in (r.get('cmpErr') or {}).items() if v is not None})
    cmp_p = {}
    for name in names:
        rs = [r for r in rows if (r.get('cmpErr') or {}).get(name) is not None]
        cmp_p[name] = {'n': len(rs), 'comparator': med([r['cmpErr'][name] for r in rs]),
                       'modelSameRows': med([r['err'] for r in rs])}
    if cmp_p:
        best = min(cmp_p, key=lambda k: cmp_p[k]['comparator'])
        rs = [r for r in rows if (r.get('cmpErr') or {}).get(best) is not None]
        cmp_p[best]['diffCI'] = _boot_ci(rs, lambda s: median(r['err'] - r['cmpErr'][best] for r in s))
        out['price'].update(comparators=cmp_p, strongest=best)
    # timeBar: modal bar exactly right; timeNear: modal bar within +/-60 min (fixed-window comparator
    # included); timeWindow: the separate window-centre output against the other comparators.
    for block, key, model_hit in (('timeBar', 'cmpBar', 'barHit'), ('timeNear', 'cmpWin', 'near60'),
                                  ('timeWindow', 'cmpWin', 'winHit')):
        names = sorted({k for r in rows for k in (r.get(key) or {})})
        cmp_t = {}
        for name in names:
            rs = [r for r in rows if name in (r.get(key) or {})]
            cmp_t[name] = {'n': len(rs), 'comparator': _rate(rs, lambda r: r[key][name]),
                           'modelSameRows': _rate(rs, lambda r: r[model_hit])}
        others = {k: v for k, v in cmp_t.items() if not (block == 'timeWindow' and k == 'prior-60 best fixed window')}
        if others:
            best = max(others, key=lambda k: others[k]['comparator'])
            rs = [r for r in rows if best in (r.get(key) or {})]
            cmp_t[best]['diffCI'] = _boot_ci(rs, lambda s: 100 * (sum(r[model_hit] for r in s)
                                                                  - sum(r[key][best] for r in s)) / len(s))
            out[block].update(comparators=cmp_t, strongest=best)
        elif cmp_t:
            out[block]['comparators'] = cmp_t
    return out


def board(rows):
    out = {}
    for kind in ('premarket', 'intraday'):
        out[kind] = {s: summarize([r for r in rows if r['kind'] == kind and r['side'] == s]) for s in ('high', 'low')}
    out['intradayByCheckpoint'] = {
        str(cp): {s: summarize([r for r in rows if r['kind'] == 'intraday' and r['checkpoint'] == cp
                                and r['side'] == s and not r['halfDay']]) for s in ('high', 'low')}
        for cp in CHECKPOINTS}
    return out


def forward_status(fwd):
    """Observed prospective results per output. Observational only: no sample size proves an edge."""
    st = {}
    for side in ('high', 'low'):
        s = fwd['premarket'][side]
        for name, blocks in ((f'{side}Price', ('price',)), (f'{side}Time', ('timeBar', 'timeNear'))):
            st[name] = {'sessions': s.get('sessions', 0), 'records': s.get('n', 0),
                        'note': 'observational; not proof of an edge'}
            for block in blocks:
                b = s.get(block, {})
                best = b.get('strongest')
                st[name][block] = {'model': b.get('model'), 'strongestComparator': best,
                                   'comparison': (b.get('comparators') or {}).get(best)}
    return st


def retrospective(store):
    """Walk-forward replay over stored sessions. Not frozen in advance: labeled retrospective."""
    recs = []
    for ticker, st in store.items():
        for key in sorted(st):
            day = cal.as_date(key)
            sub = {k: v for k, v in st.items() if k < key}
            f, _ = premarket_forecast(sub, day)
            if f:
                recs.append(dict(f, model=MODEL, ticker=ticker, session=key, kind='premarket',
                                 issuedAt=f['dataCutoff']))
            for cp in CHECKPOINTS:
                g, _ = intraday_forecast(sub, day, [tuple(b) for b in st[key]['bars'][:cp]])
                if g:
                    recs.append(dict(g, model=MODEL, ticker=ticker, session=key, kind='intraday',
                                     checkpoint=cp, issuedAt=g['dataCutoff']))
    return board(score_rows(recs, store))


def legacy_calls(path='horizons_log.json'):
    """First logged legacy daily call per ticker/session/side, logged before the session."""
    try:
        entries = json.loads(Path(path).read_text(encoding='utf-8'))['entries']
        from horizon_scoreboard import clock_minutes
    except Exception:
        return {}
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

METHOD = (f'Price: prior close x (1 + median move to the high/low over the last {MEDIAN_SESSIONS} sessions); '
          f'80% band = 10th-90th percentile of that move over up to {HISTORY_SESSIONS} sessions. Time: the modal '
          f'15-minute bar of past highs/lows (up to {HISTORY_SESSIONS} sessions) with its probability; separately, '
          f'the centre of the +/-{WINDOW_MIN} min window holding the most probability (a window centre, not the '
          'likeliest time). Intraday revisions forecast the FINAL full-session high/low, including what already '
          'traded, from exactly the bars up to a fixed checkpoint, by replaying the rest of each earlier session '
          'from the same bar. Regular session only; NYSE holidays and half-days applied.')


def tickers(path='tickers.txt'):
    names = [t.strip().upper() for t in Path(path).read_text().splitlines() if t.strip()]
    return [t for t in names if '=' not in t], [t for t in names if '=' in t]


def run(now=None, root='.'):
    now = now or datetime.now(timezone.utc)
    root = Path(root)
    ledger_path = root / LEDGER
    issued = now.astimezone(timezone.utc).isoformat(timespec='seconds')
    day, kind = cal.target_session(now)
    check = verify_ledger(ledger_path)
    if not check['ok']:
        # fail closed: nothing appended, nothing scored, page shows the failure
        report = {'generatedAt': issued, 'model': MODEL, 'targetSession': day.isoformat(), 'kind': kind,
                  'failed': {'at': issued, 'reason': f'ledger check failed: {check}'}, 'stale': True,
                  'ledger': check, 'latest': {}}
        (root / OUT).write_text(json.dumps(report, indent=1) + '\n')
        return report
    store_path = root / SESSIONS
    store = json.loads(store_path.read_text()) if store_path.exists() else {}
    ledger = read_ledger(ledger_path)
    have = {record_key(r) for r in ledger}
    equities, excluded = tickers(root / 'tickers.txt')
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
            if cp is None:
                f, why = None, 'before the first intraday checkpoint'
            elif (t, day.isoformat(), 'intraday', cp) in have:
                f, why = None, f'checkpoint {cp} already recorded'
            else:
                # freeze exactly the first cp bars; skipped earlier checkpoints are not backfilled
                f, why = intraday_forecast(st, day, done[:cp])
                if f:
                    f['checkpoint'] = cp
        if not f:
            notes[t] = why
            continue
        rec = dict(f, v=1, model=MODEL, ticker=t, session=day.isoformat(), kind=kind, issuedAt=issued)
        if kind == 'intraday':
            rec['lagMin'] = round(lag_minutes(rec), 1)
            rec['late'] = rec['lagMin'] > MAX_LAG_MIN
        if record_key(rec) not in have:
            rec = append_record(rec, ledger_path)
            ledger.append(rec)
            have.add(record_key(rec))
    store_path.write_text(json.dumps(store, separators=(',', ':')) + '\n')
    for rec in ledger:
        if rec['session'] == day.isoformat() and rec.get('model') == MODEL:
            slot = latest.setdefault(rec['ticker'], {})
            if rec['kind'] == 'intraday' or 'premarket' not in slot:
                slot[rec['kind']] = rec              # first premarket call, latest intraday checkpoint
    check = verify_ledger(ledger_path)
    legacy = legacy_calls(root / 'horizons_log.json')
    fwd_rows = score_rows(ledger, store, legacy) if check['ok'] else []
    fwd = board(fwd_rows) if check['ok'] else None
    # every model version in the ledger is scored on its own frozen records, so a new candidate
    # logged alongside hilo-1 can be compared on the same future sessions; nothing is promoted here
    by_model = {m: board(score_rows(ledger, store, legacy, model=m))
                for m in sorted({r.get('model') for r in ledger if r.get('model')})} if check['ok'] else None
    keep = ('ticker', 'session', 'kind', 'side', 'model', 'checkpoint', 'issuedAt', 'pred', 'actual',
            'err', 'inBand', 'predTime', 'actualTime', 'tErr', 'barHit')
    history = [{k: (round(r[k], 3) if isinstance(r.get(k), float) else r.get(k)) for k in keep}
               for r in sorted(fwd_rows, key=lambda r: (r['session'], r['issuedAt']), reverse=True)[:60]]
    report = {
        'generatedAt': issued, 'model': MODEL, 'targetSession': day.isoformat(), 'kind': kind,
        'method': METHOD, 'latest': latest, 'notes': notes,
        'excluded': {t: 'futures session calendar not implemented' for t in excluded},
        'ledger': check, 'otherModelRecords': sum(1 for r in ledger if r.get('model') != MODEL),
        'lateIntradayRecords': sum(1 for r in ledger if r.get('late')),
        'storedSessions': {t: len(v) for t, v in store.items()},
        'forward': fwd, 'status': forward_status(fwd) if fwd else None,
        'forwardByModel': by_model, 'history': history,
        'retrospective': retrospective(store),
        'build': {'commit': os.environ.get('GITHUB_SHA', 'local'), 'run': os.environ.get('GITHUB_RUN_ID')},
    }
    if not check['ok']:
        report.update(failed={'at': issued, 'reason': f'ledger check failed: {check}'}, stale=True, latest={})
    (root / OUT).write_text(json.dumps(report, indent=1) + '\n')
    return report


def mark_failed(reason, root='.'):
    """After a crash: keep the old file for the record but flag it so the page shows no forecast."""
    path = Path(root) / OUT
    try:
        report = json.loads(path.read_text())
    except Exception:
        report = {}
    now = datetime.now(timezone.utc).isoformat(timespec='seconds')
    report.update(failed={'at': now, 'reason': reason}, stale=True)
    path.write_text(json.dumps(report, indent=1) + '\n')


def main(argv=None):
    import sys
    argv = sys.argv[1:] if argv is None else argv
    if argv[:1] == ['--mark-failed']:
        mark_failed(' '.join(argv[1:]) or 'forecaster failed')
        print('hilo: marked failed')
        return
    report = run()
    print('hilo:', report['kind'], report['targetSession'], 'ledger', report['ledger'],
          'notes', report.get('notes') or 'none')
    if report.get('failed'):
        sys.exit('hilo: ' + report['failed']['reason'])


if __name__ == '__main__':
    main()
