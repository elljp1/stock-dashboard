"""Validated publication, append-only forecast snapshots, and daily review.

No retrospective backfill is counted as a forecast. Existing engine calibration
continues; this independent ledger records what was actually available to users.
"""
import hashlib
import json
import math
from datetime import datetime, timezone
from pathlib import Path


def read_constants(path='data.js'):
    result = {}
    for line in Path(path).read_text().splitlines():
        if line.startswith('const '):
            name, value = line[6:].split(' = ', 1)
            result[name] = json.loads(value.rstrip(';'))
    return result


def validate(data):
    expected = {t.strip().upper() for t in Path('tickers.txt').read_text().splitlines() if t.strip()}
    if set(data) != expected:
        raise ValueError('Incomplete ticker set; refusing to replace last good publication')
    for ticker, item in data.items():
        chart = item['chart']
        assert item['generated'] and item['predictions'], ticker
        assert chart['dates'] and len(chart['dates']) == len(chart['closes']), ticker
        assert chart['dates'] == sorted(set(chart['dates'])), ticker
        values = chart['closes'] + [item['price']] + [p['price'] for p in item['predictions']]
        assert all(isinstance(v, (int, float)) and math.isfinite(v) and v > 0 for v in values), ticker


def atomic_json(path, value):
    p = Path(path)
    temp = p.with_suffix(p.suffix + '.tmp')
    temp.write_text(json.dumps(value, indent=2, allow_nan=False) + '\n')
    temp.replace(p)


def review(data, now=None):
    now = now or datetime.now(timezone.utc).isoformat()
    ledger_path = Path('forecast_ledger.json')
    ledger = json.loads(ledger_path.read_text()) if ledger_path.exists() else {'version': 1, 'snapshots': []}
    known = {r['id'] for r in ledger['snapshots']}
    for ticker, d in data.items():
        body = {'ticker': ticker, 'generated': d['generated'], 'predictions': d['predictions'],
                'price': d['price'], 'lastBar': d['chart']['dates'][-1]}
        key = hashlib.sha256(json.dumps(body, sort_keys=True).encode()).hexdigest()
        if key not in known:
            ledger['snapshots'].append(dict(body, id=key, recordedAt=now))
    atomic_json(ledger_path, ledger)
    # Score the first recorded call per ticker/target date/type. Revisions stay
    # visible in snapshots and cannot replace the original in this scorecard.
    original = {}
    for row in ledger['snapshots']:
        for pred in row['predictions']:
            key = (row['ticker'], pred['isoDate'], pred['type'])
            original.setdefault(key, (row, pred))
    results = []
    for (ticker, target, kind), (row, pred) in original.items():
        d = data[ticker]
        observed_day = datetime.fromisoformat(row['recordedAt']).date().isoformat()
        if target <= observed_day:
            continue  # timing cannot be evaluated prospectively on same-day daily bars
        dates, closes = d['chart']['dates'], d['chart']['closes']
        eligible = [i for i, day in enumerate(dates) if day >= target]
        if not eligible:
            continue
        i = eligible[0]
        actual = closes[i]
        results.append({'snapshotId': row['id'], 'ticker': ticker, 'targetDate': target,
                        'observedDate': dates[i], 'type': kind, 'predictedPrice': pred['price'],
                        'actualClose': actual, 'absolutePriceErrorPct': round(abs(actual / pred['price'] - 1) * 100, 2)})
    report = {'reviewedAt': now, 'snapshotCount': len(ledger['snapshots']),
              'scoredOriginals': len(results), 'results': results,
              'method': 'Original future-date targets versus first available daily close on/after target; price error only, not reversal accuracy or trading profit.',
              'learning': {t: {'bias': d.get('biasLearning'), 'trackRecord': d.get('trackRecord')}
                           for t, d in data.items()},
              'promotionPolicy': 'Daily scoring and existing bounded calibration run automatically. New strategies require unseen-data validation; no guaranteed improvement or return.'}
    atomic_json('daily_review.json', report)
    return report


def build():
    constants = read_constants()
    data = constants['DATA_ALL']
    validate(data)
    # Older analyzer builds omitted the plan from the update payload.
    if Path('week_plan.json').exists():
        constants['WEEKPLAN'] = json.loads(Path('week_plan.json').read_text())
    constants.setdefault('WEEKPLAN', {})
    report = review(data)
    for d in data.values():
        d['dailyReview'] = {'reviewedAt': report['reviewedAt'], 'snapshotCount': report['snapshotCount'],
                            'scoredOriginals': report['scoredOriginals']}
    script = '\n'.join('const ' + k + ' = ' + json.dumps(v, allow_nan=False).replace('</', '<\\/') + ';' for k, v in constants.items()) + '\n'
    Path('data.js').write_text(script)
    template = Path('dashboard.html').read_text()
    assert '<script src="data.js"></script>' in template
    html = template.replace('<script src="data.js"></script>', '<script>' + script + '</script>')
    for name in ('index.html', 'dashboard_single.html'):
        Path(name).write_text(html)
    print(f'Validated {len(data)} tickers; {report["snapshotCount"]} immutable snapshots; {report["scoredOriginals"]} prospective grades')


if __name__ == '__main__':
    build()
