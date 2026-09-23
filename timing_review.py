"""Independent, price-target-free audit of immutable dated turning-point calls.

Protocol v1 is fixed before forward collection begins. Historical scores are an
audit, not an unseen test. This module never changes forecasts or model weights.
"""
from datetime import datetime
from statistics import median
from zoneinfo import ZoneInfo

VERSION = 'daily-close-turns-v1'
FORWARD_START = '2026-09-24T00:00:00-04:00'
FLANK = 2
TOLERANCE = 2


def eastern_day(stamp):
    value = datetime.fromisoformat(stamp)
    if value.tzinfo is None:
        raise ValueError('Forecast timestamps must include a timezone')
    return value.astimezone(ZoneInfo('America/New_York')).date().isoformat()


def confirmed_turns(dates, closes):
    """Strict five-session closing extremes; two later closed bars confirm.

    Ties are not a unique turn. Price targets, future model pivots and the
    engine's adaptive zigzag threshold are deliberately not inputs.
    """
    turns = []
    for i in range(FLANK, len(dates) - FLANK):
        peers = closes[i-FLANK:i] + closes[i+1:i+FLANK+1]
        kind = 'high' if closes[i] > max(peers) else 'low' if closes[i] < min(peers) else None
        if kind:
            turns.append({'date': dates[i], 'type': kind, 'index': i,
                          'confirmedDate': dates[i+FLANK]})
    return turns


def summarize(results):
    hits = [r for r in results if r['status'] == 'hit']
    errors = [r['errorSessions'] for r in hits]
    return {'scored': len(results), 'hits': len(hits),
            'falseAlarms': len(results)-len(hits),
            'hitRatePct': round(100*len(hits)/len(results), 1) if results else None,
            'medianAbsErrorSessions': median([abs(e) for e in errors]) if errors else None,
            'early': sum(e < 0 for e in errors), 'late': sum(e > 0 for e in errors),
            'exact': sum(e == 0 for e in errors)}


def match(calls, turns):
    """Earliest-issued call claims the nearest unclaimed same-type turn."""
    results, used = [], set()
    for base, pos, observed_day in calls:
        kind = base['type']
        candidates = [t for t in turns if t['type'] == kind and t['date'] > observed_day
                      and abs(t['index']-pos) <= TOLERANCE and (t['date'], kind) not in used]
        if candidates:
            turn = min(candidates, key=lambda t: (abs(t['index']-pos), t['date']))
            used.add((turn['date'], kind))
            results.append(dict(base, status='hit', actualDate=turn['date'],
                                confirmedDate=turn['confirmedDate'], errorSessions=pos-turn['index']))
        else:
            results.append(dict(base, status='falseAlarm', actualDate=None,
                                confirmedDate=None, errorSessions=None))
    return results, used


def coverage(turns, from_exclusive, end_i):
    return [t for t in turns if from_exclusive and t['date'] > from_exclusive and t['index'] <= end_i]


def coverage_summary(scope, used, from_exclusive, dates, end_i):
    missed = sum((t['date'], t['type']) not in used for t in scope)
    return {'fromExclusive': from_exclusive,
            'through': dates[end_i] if end_i >= 0 else None,
            'turns': len(scope), 'missedTurns': missed, 'caughtTurns': len(scope)-missed}


def timing_review(data, snapshots, now):
    cutoff_day = eastern_day(now)
    # First means earliest timestamp, independent of file ordering. Never let a
    # later revision of the same date/type replace an ineligible original.
    originals = {}
    for row in sorted(snapshots, key=lambda r: (datetime.fromisoformat(r['recordedAt']), r['id'])):
        for pred in row['predictions']:
            originals.setdefault((row['ticker'], pred['isoDate'], pred['type']), (row, pred))
    report = {'version': VERSION, 'forwardStart': FORWARD_START, 'reviewedAt': now,
              'unit': 'trading sessions', 'tickers': {},
              'method': 'First logged future-date call per ticker/date/type; strict five-session daily-close high/low; ±2 sessions; two later closed bars confirm. One turn credits one call, earliest-issued first; historical-audit and forward cohorts are matched and covered independently (the combined summary uses one global matching). Error = called session minus actual session (negative = early).',
              'limitations': 'Daily-close turns are not intraday highs/lows or tradeable confirmation signals. Historical audit uses a rule chosen after those data; it is not unseen validation. Timing hits do not measure net trading profitability. Method tags describe blended calls, not standalone method performance.',
              'promotion': 'No weight changes. Require predeclared standalone/control comparisons on unseen sessions, adequate independent samples, and a separate cost/slippage/drawdown test.'}
    for ticker, d in data.items():
        generated_day = datetime.strptime(d['generated'][:19], '%Y-%m-%d %I:%M %p').date().isoformat()
        # Today's API daily bar may still be changing. Both build and review
        # must be on a later Eastern date before that bar can enter this audit.
        pairs = [(day, close) for day, close in zip(d['chart']['dates'], d['chart']['closes'])
                 if day < min(cutoff_day, generated_day)]
        dates = [p[0] for p in pairs]
        closes = [p[1] for p in pairs]
        positions = {day: i for i, day in enumerate(dates)}
        turns = confirmed_turns(dates, closes)
        calls, pending, excluded = [], 0, []
        first_logged = {}
        # Coverage ends early enough that even the latest acceptable prediction
        # for a turn has itself matured. Otherwise "missed" would be premature.
        coverage_end_i = len(dates)-1-FLANK-2*TOLERANCE
        for (symbol, target, kind), (row, pred) in originals.items():
            if symbol != ticker:
                continue
            logged_day = eastern_day(row['recordedAt'])
            cohort = 'forward' if datetime.fromisoformat(row['recordedAt']) >= datetime.fromisoformat(FORWARD_START) else 'historicalAudit'
            if logged_day < cutoff_day:
                for key in ('all', cohort):
                    first_logged[key] = min(first_logged.get(key, logged_day), logged_day)
            base = {'snapshotId': row['id'], 'targetDate': target, 'type': kind,
                    'recordedAt': row['recordedAt'], 'methods': pred.get('methods', []),
                    'cohort': cohort}
            observed_day = max(logged_day, row.get('lastBar', logged_day),
                               datetime.strptime(row['generated'][:19], '%Y-%m-%d %I:%M %p').date().isoformat())
            if kind not in ('high', 'low') or target <= observed_day:
                excluded.append(dict(base, reason='not a future-session original'))
                continue
            if not dates or target > dates[-1]:
                pending += 1
                continue
            if target not in positions:
                excluded.append(dict(base, reason='target session absent; no date shifting'))
                continue
            pos = positions[target]
            if pos < FLANK+TOLERANCE:
                excluded.append(dict(base, reason='insufficient earlier chart history'))
                continue
            if pos+TOLERANCE+FLANK >= len(dates):
                pending += 1
                continue
            calls.append((base, pos, observed_day))
        # Each cohort is matched on its own: a forward call must never become a
        # false alarm because an earlier historical call already claimed its
        # turn. Within any one scorecard a turn still credits at most one call.
        results, used = match(calls, turns)
        historical, historical_used = match([c for c in calls if c[0]['cohort'] == 'historicalAudit'], turns)
        forward, forward_used = match([c for c in calls if c[0]['cohort'] == 'forward'], turns)
        forward_day = eastern_day(FORWARD_START)
        historical_end_i = min(coverage_end_i, sum(day < forward_day for day in dates)-1)
        scope = coverage(turns, first_logged.get('all'), coverage_end_i)
        missed = [t for t in scope if (t['date'], t['type']) not in used]
        # Tags overlap because a call may combine several methods. No causal
        # attribution or ranking is inferred from these descriptive buckets.
        families = {'Gann': lambda s: 'gann' in s,
                    'Hurst / rhythm': lambda s: 'hurst' in s or 'rhythm' in s,
                    'Fibonacci': lambda s: 'fib' in s,
                    'Astro / vibration': lambda s: any(x in s for x in ('moon','vibe','astro','planet','sepharial')),
                    'Other cycles': lambda s: 'cycle' in s or 'goertzel' in s}
        tags = {family: summarize([r for r in results if any(test(m.lower()) for m in r['methods'])])
                for family, test in families.items()}
        report['tickers'][ticker] = {
            'summary': summarize(results), 'historicalAudit': summarize(historical),
            'forward': summarize(forward), 'pending': pending, 'excludedCount': len(excluded),
            'coverage': coverage_summary(scope, used, first_logged.get('all'), dates, coverage_end_i),
            # Historical coverage stops before the forward start; forward
            # coverage starts after the first forward original was logged.
            'historicalCoverage': coverage_summary(
                coverage(turns, first_logged.get('historicalAudit'), historical_end_i),
                historical_used, first_logged.get('historicalAudit'), dates, historical_end_i),
            'forwardCoverage': coverage_summary(
                coverage(turns, first_logged.get('forward'), coverage_end_i),
                forward_used, first_logged.get('forward'), dates, coverage_end_i),
            'results': historical + forward, 'excluded': excluded, 'missed': missed, 'methodTags': tags,
            'lastClosedSession': dates[-1] if dates else None}
    return report
