"""Recover missing equity daily bars using recent daily data from the provider."""
from datetime import time
import numpy as np
from zoneinfo import ZoneInfo
import pandas as pd

ET = ZoneInfo('America/New_York')


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


def reconcile_daily(daily, hourly, ticker, now, fetch_recent, intraday=None):
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
            raise ValueError(f'{ticker}: missing daily bar for completed session {required}; refusing stale analysis')
        merged = pd.concat([merged, recovered]).sort_index()
        print(f'{ticker}: recovered {required} from 26 regular-hours 15-minute bars and explicit 16:00 close')
    print(f'{ticker}: recovered daily history through completed session {required}')
    return merged
