"""Recover missing equity daily bars using recent daily data from the provider."""
from datetime import time
from zoneinfo import ZoneInfo
import pandas as pd

ET = ZoneInfo('America/New_York')


def reconcile_daily(daily, hourly, ticker, now, fetch_recent):
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
        raise ValueError(f'{ticker}: missing daily bar for completed session {required}; refusing stale analysis')
    print(f'{ticker}: recovered daily history through completed session {required}')
    return merged
