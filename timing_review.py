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
              'method': 'First logged future-date call per ticker/date/type; strict five-session daily-close high/low; ±2 sessions; two later closed bars confirm. One turn credits one call, earliest-issued first. Error = called session minus actual session (negative = early).',
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
        results, pending, excluded = [], 0, []
        used = set()
        first_logged_day = None
        # Coverage ends early enough that even the latest acceptable prediction
        # for a turn has itself matured. Otherwise "missed" would be premature.
        coverage_end_i = len(dates)-1-FLANK-2*TOLERANCE
        for (symbol, target, kind), (row, pred) in originals.items():
            if symbol != ticker:
                continue
            logged_day = eastern_day(row['recordedAt'])
            if logged_day < cutoff_day:
                first_logged_day = min(first_logged_day or logged_day, logged_day)
            base = {'snapshotId': row['id'], 'targetDate': target, 'type': kind,
                    'recordedAt': row['recordedAt'], 'methods': pred.get('methods', []),
                    'cohort': 'forward' if datetime.fromisoformat(row['recordedAt']) >= datetime.fromisoformat(FORWARD_START) else 'historicalAudit'}
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
        scope = [t for t in turns if first_logged_day and t['date'] > first_logged_day
                 and t['index'] <= coverage_end_i]
        missed = [t for t in scope if (t['date'], t['type']) not in used]
        historical = [r for r in results if r['cohort'] == 'historicalAudit']
        forward = [r for r in results if r['cohort'] == 'forward']
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
            'coverage': {'fromExclusive': first_logged_day,
                         'through': dates[coverage_end_i] if coverage_end_i >= 0 else None,
                         'turns': len(scope), 'missedTurns': len(missed),
                         'caughtTurns': len(scope)-len(missed)},
            'results': results, 'excluded': excluded, 'missed': missed, 'methodTags': tags,
            'lastClosedSession': dates[-1] if dates else None}
    return report
