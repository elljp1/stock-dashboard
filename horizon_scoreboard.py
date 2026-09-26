"""Grade the first daily/weekly/monthly high-low call for each period.

Each call is scored on price, day and time of day against simple baselines:
- price: last period's actual high/low used as the forecast;
- day: a random session in the period;
- time: a random minute of the session, and "the open" (9:30 ET).
Only the first logged call per ticker/horizon/side/period counts, and calls
that merely report an extreme already set ("actual") are not predictions.

It also grades a simple daily forecast built only from each ticker's own past
sessions (last close times the typical move to the high/low, and the most
common bar for each), walked forward one session at a time, so the app has a
concrete bar to beat.
"""
import json
import re
from collections import Counter
from datetime import date, timedelta
from pathlib import Path
from statistics import median

OUT = 'horizon_scoreboard.json'
HORIZONS = ('daily', 'weekly', 'monthly')
OPEN_MIN, CLOSE_MIN = 9 * 60 + 30, 16 * 60
SESSION_MIN = CLOSE_MIN - OPEN_MIN
NEAR_MIN = 60
SIMPLE_RANGE_SESSIONS = 20
SIMPLE_TIME_SESSIONS = 60
SIMPLE_MIN_HISTORY = 40


def period_key(horizon, day):
    d = date.fromisoformat(day)
    if horizon == 'daily':
        return day
    if horizon == 'weekly':
        y, w, _ = d.isocalendar()
        return f'{y}-W{w:02d}'
    return day[:7]


def clock_minutes(text):
    """Midpoint of the first 'H:MM-H:MM AM' window, or a single 'H:MM AM'."""
    if not text:
        return None
    m = re.search(r'(\d{1,2}):(\d{2})\s*(?:(AM|PM)\s*)?-\s*(\d{1,2}):(\d{2})\s*(AM|PM)', text)
    if m:
        end_ampm = m.group(6)
        start_ampm = m.group(3) or end_ampm

        def mins(h, mm, ampm):
            return (int(h) % 12 + (12 if ampm == 'PM' else 0)) * 60 + int(mm)
        a, b = mins(m.group(1), m.group(2), start_ampm), mins(m.group(4), m.group(5), end_ampm)
        if b < a and start_ampm == end_ampm == 'PM':
            a -= 12 * 60
        return (a + b) // 2
    m = re.search(r'(\d{1,2}):(\d{2})\s*(AM|PM)', text)
    if m:
        return (int(m.group(1)) % 12 + (12 if m.group(3) == 'PM' else 0)) * 60 + int(m.group(2))
    return None


def called_day(text, session):
    """'Mon 09/28' or 'Tue 09-29' -> ISO date in the session's year."""
    m = re.search(r'(\d{2})[/-](\d{2})', text or '')
    if not m:
        return None
    year = int(session[:4])
    try:
        return date(year, int(m.group(1)), int(m.group(2))).isoformat()
    except ValueError:
        return None


def bar_minutes(hhmm):
    try:
        h, m = hhmm.split(':')
        return int(h) * 60 + int(m)
    except (AttributeError, ValueError):
        return None


def actual_extremes(days, horizon):
    """Per period: high/low price, the session it came on and its bar time."""
    out = {}
    for day in sorted(days):
        rec = days[day]
        if len(rec) < 5:
            continue
        key = period_key(horizon, day)
        cur = out.setdefault(key, {'sessions': [], 'high': None, 'low': None})
        cur['sessions'].append(day)
        if cur['high'] is None or rec[0] > cur['high'][0]:
            cur['high'] = (rec[0], day, rec[3])
        if cur['low'] is None or rec[1] < cur['low'][0]:
            cur['low'] = (rec[1], day, rec[4])
    return out


def complete_periods(extremes, last_day):
    """A period is complete once a later session exists in the data."""
    return {k for k, v in extremes.items() if v['sessions'][-1] < last_day}


def random_time_chance(actual_min):
    lo, hi = max(OPEN_MIN, actual_min - NEAR_MIN), min(CLOSE_MIN, actual_min + NEAR_MIN)
    return max(0, hi - lo) / SESSION_MIN


def grade(entries, extremes_by_ticker):
    rows = []
    for ticker, days in extremes_by_ticker.items():
        if not days:
            continue
        last_day = max(days)
        for horizon in HORIZONS:
            ext = actual_extremes(days, horizon)
            done = complete_periods(ext, last_day)
            order = sorted(ext)
            firsts = {}
            for e in sorted((e for e in entries if e['ticker'] == ticker), key=lambda e: e['logged']):
                block = (e.get('h') or {}).get(horizon) or {}
                for side in ('high', 'low'):
                    call = block.get(side)
                    if not isinstance(call, dict) or call.get('src') == 'actual':
                        continue
                    if str(call.get('date', '')).startswith('already set'):
                        continue
                    key = (side, period_key(horizon, e['session']))
                    firsts.setdefault(key, (e, call))
            for (side, key), (e, call) in firsts.items():
                if key not in done or not call.get('price'):
                    continue
                period = ext[key]
                price, day, bar = period[side]
                prior = order.index(key) - 1
                naive = ext[order[prior]][side][0] if prior >= 0 else None
                pred_day = e['session'] if horizon == 'daily' else called_day(call.get('date'), e['session'])
                pred_min, act_min = clock_minutes(call.get('time')), bar_minutes(bar)
                same_day = pred_day == day
                row = {'ticker': ticker, 'horizon': horizon, 'side': side, 'period': key,
                       'logged': e['logged'], 'predPrice': call['price'], 'actualPrice': price,
                       'priceErrPct': round(100 * (call['price'] - price) / price, 2),
                       'naiveErrPct': round(100 * (naive - price) / price, 2) if naive else None,
                       'predDay': pred_day, 'actualDay': day, 'sessions': len(period['sessions']),
                       'dayHit': same_day, 'actualTime': bar}
                if same_day and pred_min is not None and act_min is not None:
                    row.update(timeErrMin=pred_min - act_min,
                               randomTimeChance=round(random_time_chance(act_min), 3),
                               openWithin=act_min <= OPEN_MIN + NEAR_MIN)
                rows.append(row)
    return rows


def summarize(rows):
    if not rows:
        return {'n': 0}
    err = [abs(r['priceErrPct']) for r in rows]
    naive = [abs(r['naiveErrPct']) for r in rows if r['naiveErrPct'] is not None]
    timed = [r for r in rows if 'timeErrMin' in r]
    out = {'n': len(rows),
           'medianPriceErrPct': round(median(err), 2),
           'medianNaivePriceErrPct': round(median(naive), 2) if naive else None,
           'dayHitPct': round(100 * sum(r['dayHit'] for r in rows) / len(rows), 1),
           'randomDayPct': round(100 * sum(1 / r['sessions'] for r in rows) / len(rows), 1),
           'timed': len(timed)}
    if timed:
        out.update(
            withinHourPct=round(100 * sum(abs(r['timeErrMin']) <= NEAR_MIN for r in timed) / len(timed), 1),
            randomWithinHourPct=round(100 * sum(r['randomTimeChance'] for r in timed) / len(timed), 1),
            openWithinHourPct=round(100 * sum(r['openWithin'] for r in timed) / len(timed), 1),
            medianTimeErrMin=int(median(abs(r['timeErrMin']) for r in timed)))
    return out


def full_sessions(days):
    return {k: v for k, v in days.items() if len(v) >= 5}


def simple_call(days, keys):
    """Next-session daily high/low from the sessions in keys (oldest first) only."""
    last = days[keys[-1]]
    call = {'basis': keys[-1]}
    for side, pi, ti in (('high', 0, 3), ('low', 1, 4)):
        moves = [days[keys[j]][pi] / days[keys[j - 1]][2] - 1
                 for j in range(max(1, len(keys) - SIMPLE_RANGE_SESSIONS), len(keys))]
        bars = [bar_minutes(days[k][ti]) for k in keys[-SIMPLE_TIME_SESSIONS:]]
        bars = [m for m in bars if m is not None and OPEN_MIN <= m < CLOSE_MIN]
        c = {'price': round(last[2] * (1 + median(moves)), 2) if moves else None, 'time': None}
        if len(bars) * 2 >= min(len(keys), SIMPLE_TIME_SESSIONS):
            mode = Counter(bars).most_common(1)[0][0]
            c['time'] = mode
            c['timeSharePct'] = round(100 * sum(abs(m - mode) <= NEAR_MIN for m in bars) / len(bars), 1)
        call[side] = c
    return call


def simple_grade(days):
    days = full_sessions(days)
    keys = sorted(days)
    rows = []
    for i in range(SIMPLE_MIN_HISTORY, len(keys)):
        call = simple_call(days, keys[:i])
        today, prev = days[keys[i]], days[keys[i - 1]]
        for side, pi, ti in (('high', 0, 3), ('low', 1, 4)):
            c, actual = call[side], today[pi]
            if c['price'] is None:
                continue
            row = {'side': side, 'session': keys[i],
                   'errPct': abs(c['price'] - actual) / actual * 100,
                   'naivePct': abs(prev[pi] - actual) / actual * 100}
            act = bar_minutes(today[ti])
            if c['time'] is not None and act is not None and OPEN_MIN <= act < CLOSE_MIN:
                row.update(timeHit=abs(c['time'] - act) <= NEAR_MIN, openHit=act <= OPEN_MIN + NEAR_MIN,
                           randomChance=random_time_chance(act))
            rows.append(row)
    return rows


def simple_summary(rows):
    if not rows:
        return {'n': 0}
    timed = [r for r in rows if 'timeHit' in r]
    out = {'n': len(rows), 'from': min(r['session'] for r in rows), 'to': max(r['session'] for r in rows),
           'medianPriceErrPct': round(median(r['errPct'] for r in rows), 2),
           'medianNaivePriceErrPct': round(median(r['naivePct'] for r in rows), 2), 'timed': len(timed)}
    if timed:
        out.update(withinHourPct=round(100 * sum(r['timeHit'] for r in timed) / len(timed), 1),
                   openWithinHourPct=round(100 * sum(r['openHit'] for r in timed) / len(timed), 1),
                   randomWithinHourPct=round(100 * sum(r['randomChance'] for r in timed) / len(timed), 1))
    return out


def simple_board(extremes_by_ticker):
    graded = {t: simple_grade(days) for t, days in extremes_by_ticker.items() if days}
    table = {}
    for scope in sorted(graded) + ['ALL']:
        rows = [r for t, rs in graded.items() if scope in ('ALL', t) for r in rs]
        table[scope] = {s: simple_summary([r for r in rows if r['side'] == s]) for s in ('high', 'low')}
    nxt = {}
    for t, days in extremes_by_ticker.items():
        full = full_sessions(days)
        if len(full) >= SIMPLE_MIN_HISTORY:
            nxt[t] = simple_call(full, sorted(full))
    return {'method': f'Walk-forward: each session is forecast from earlier sessions only. Price = last close x the median '
                      f'move to the high/low over the last {SIMPLE_RANGE_SESSIONS} sessions; time = the most common '
                      f'15-minute bar for the high/low over the last {SIMPLE_TIME_SESSIONS} regular sessions.',
            'table': table, 'next': nxt}


def scoreboard(entries, extremes_by_ticker):
    rows = grade(entries, extremes_by_ticker)
    table = {}
    for scope in sorted({r['ticker'] for r in rows}) + ['ALL']:
        scoped = [r for r in rows if scope == 'ALL' or r['ticker'] == scope]
        table[scope] = {h: {s: summarize([r for r in scoped if r['horizon'] == h and r['side'] == s])
                            for s in ('high', 'low')} for h in HORIZONS}
    return {'method': 'First logged daily/weekly/monthly high-low call per period; calls that report an '
                      'extreme already set are excluded. Price vs last period\'s actual extreme; day vs a random '
                      'session in the period; time (only when the day is right) vs a random minute and vs the open. '
                      'Times use 15-minute bars. Hourly and yearly calls are not graded yet.',
            'rows': len(rows), 'table': table, 'simple': simple_board(extremes_by_ticker),
            'recent': sorted(rows, key=lambda r: (r['period'], r['ticker']), reverse=True)[:40]}


def main():
    entries = json.loads(Path('horizons_log.json').read_text())['entries']
    extremes = json.loads(Path('daily_extremes.json').read_text())
    report = scoreboard(entries, extremes)
    Path(OUT).write_text(json.dumps(report, indent=1))
    a = report['table'].get('ALL', {})
    for h in HORIZONS:
        for s in ('high', 'low'):
            print(h, s, a.get(h, {}).get(s))
    for s in ('high', 'low'):
        print('simple daily', s, report['simple']['table'].get('ALL', {}).get(s))


if __name__ == '__main__':
    main()
