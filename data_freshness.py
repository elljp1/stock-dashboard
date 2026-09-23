"""Recover missing equity daily bars using recent daily data from the provider."""
from datetime import time
from datetime import datetime
import numpy as np
from zoneinfo import ZoneInfo
import pandas as pd

ET = ZoneInfo('America/New_York')


def cached_session(cache, ticker, session, now):
    """Reuse only a validated, exact-date completed bar; never a prior date."""
    if not cache or cache.get('version') != 1:
        return None
    row = cache.get('tickers', {}).get(ticker, {}).get(session.isoformat())
    if not row or row.get('source') not in ('yahoo_daily', 'recovered_15m_complete_session'):
        return None
    try:
        saved = datetime.fromisoformat(row['storedAt'])
        end = pd.Timestamp(session, tz=ET) + pd.Timedelta(hours=16, minutes=15)
        if saved.tzinfo is None or not (end <= pd.Timestamp(saved) <= pd.Timestamp(now)):
            return None
        cols = ['Open', 'High', 'Low', 'Close', 'Volume']
        values = np.array([row[k] for k in cols], dtype=float)
        if not np.isfinite(values).all() or (values[:4] <= 0).any() or values[4] < 0:
            return None
        o, h, lo, c, _ = values
        if h < max(o, c, lo) or lo > min(o, c, h):
            return None
        return pd.DataFrame([dict(zip(cols, values), Source='cached_validated_completed_session')],
                            index=pd.DatetimeIndex([end.normalize()+pd.Timedelta(hours=9, minutes=30)], name='Datetime'))
    except (KeyError, TypeError, ValueError):
        return None


def remember_completed(cache, ticker, daily, now):
    """Keep a small validated cache; incomplete same-day daily bars stay out.

    Cached entries keep their original source and stored timestamp. The caller
    commits this file only after the complete refresh and tests succeed.
    """
    if '=' in ticker:
        return
    cache.setdefault('version', 1)
    rows = cache.setdefault('tickers', {}).setdefault(ticker, {})
    for stamp, item in daily.tail(30).iterrows():
        session = stamp.tz_convert(ET).date()
        if session >= now.astimezone(ET).date():
            continue
        source = item.get('Source')
        if source == 'cached_validated_completed_session':
            continue
        source = 'recovered_15m_complete_session' if source == 'recovered_15m_complete_session' else 'yahoo_daily'
        try:
            row = {k: float(item[k]) for k in ['Open', 'High', 'Low', 'Close', 'Volume']}
        except (KeyError, TypeError, ValueError):
            continue
        row.update(source=source, storedAt=now.isoformat())
        probe = {'version': 1, 'tickers': {ticker: {session.isoformat(): row}}}
        if cached_session(probe, ticker, session, now) is not None:
            rows[session.isoformat()] = row
    cache['tickers'][ticker] = dict(sorted(rows.items())[-20:])


def recover_session(intraday, session, now):
    """Recover only a complete regular session with an explicit closing point.

    Require all 26 fifteen-minute intervals plus Yahoo's 16:00 observation.
    A missing interval, missing close, short session or bad OHLCV fails closed.
    Do not extrapolate partial sessions or substitute a last intraday trade.
    """
    if intraday is None or session.weekday() >= 5:
        return None
    start = pd.Timestamp(session, tz=ET) + pd.Timedelta(hours=9, minutes=30)
    end = start + pd.Timedelta(hours=6, minutes=30)
    if pd.Timestamp(now) < end + pd.Timedelta(minutes=15):
        return None
    required = pd.date_range(start, end, freq='15min')
    frame = intraday.copy()
    frame.index = frame.index.tz_convert(ET)
    frame = frame[(frame.index >= start) & (frame.index <= end)]
    if not frame.index.equals(required):
        return None
    cols = ['Open', 'High', 'Low', 'Close', 'Volume']
    if not set(cols).issubset(frame.columns):
        return None
    values = frame[cols].to_numpy(dtype=float)
    if not np.isfinite(values).all() or (values[:, :4] <= 0).any() or (values[:, 4] < 0).any():
        return None
    if ((frame.High < frame[['Open', 'Close', 'Low']].max(axis=1)).any()
            or (frame.Low > frame[['Open', 'Close', 'High']].min(axis=1)).any()):
        return None
    return pd.DataFrame([{
        'Open': frame.Open.iloc[0], 'High': frame.High.max(),
        'Low': frame.Low.min(), 'Close': frame.Close.iloc[-1],
        'Volume': frame.Volume.sum(), 'Source': 'recovered_15m_complete_session',
    }], index=pd.DatetimeIndex([start], name='Datetime'))


def reconcile_daily(daily, hourly, ticker, now, fetch_recent, intraday=None, cache=None):
    """Require the latest completed session observed in regular-hours data.

    Observed session dates avoid inventing bars for weekends/holidays. Same-day
    equity data is required only after 16:15 ET, including on early-close days.
    Futures/FX have different session labels and are not assigned equity hours.
    This cross-check cannot detect a provider returning stale data in both feeds.
    """
    if '=' in ticker:
        return daily
    now = now.astimezone(ET)
    observed = {stamp.date() for stamp in hourly.index.tz_convert(ET)
                if stamp.date() < now.date()
                or (stamp.date() == now.date() and now.time() >= time(16, 15))}
    if not observed:
        raise ValueError(f'{ticker}: no completed session found in hourly data')
    required = max(observed)
    if required in set(daily.index.tz_convert(ET).date):
        return daily
    recent = fetch_recent()
    if recent.empty:
        raise ValueError(f'{ticker}: recent daily recovery returned no bars')
    merged = pd.concat([daily, recent])
    # Daily endpoint timestamps can differ; deduplicate by exchange-local date.
    dates = pd.Index(merged.index.tz_convert(ET).date)
    merged = merged[~dates.duplicated(keep='last')].sort_index()
    if required not in set(merged.index.tz_convert(ET).date):
        recovered = recover_session(intraday, required, now)
        if recovered is None:
            recovered = cached_session(cache, ticker, required, now)
            if recovered is None:
                raise ValueError(f'{ticker}: missing daily bar for completed session {required}; refusing stale analysis')
            print(f'{ticker}: restored exact completed session {required} from validated cache')
        else:
            print(f'{ticker}: recovered {required} from 26 regular-hours 15-minute bars and explicit 16:00 close')
        merged = pd.concat([merged, recovered]).sort_index()
    print(f'{ticker}: recovered daily history through completed session {required}')
    return merged
