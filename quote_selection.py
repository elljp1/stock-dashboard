"""Keep a displayed quote's value, timestamp and provenance together."""
import math
from datetime import datetime


def select_quote(payload, ticker, daily_timestamp, now):
    """Return a usable intraday bar quote, otherwise leave the daily fallback.

    The provider response contains 5-minute bars, so its timestamp identifies
    a bar rather than a guaranteed individual trade. Never attach it to a
    different price just because the price change is small.
    """
    try:
        age = now.timestamp() - float(payload['asof'])
        quote = payload['quotes'][ticker]
        price = float(quote['price'])
        stamp = datetime.fromisoformat(quote['quoteTime'])
        if not 0 <= age < 6 * 3600 or not math.isfinite(price) or price <= 0:
            return None
        if stamp.tzinfo is None or not daily_timestamp <= stamp <= now:
            return None
        return {
            'price': price,
            'priceAsOf': stamp.isoformat(),
            'priceSource': 'latest available 5-minute bar, including extended hours',
        }
    except (KeyError, TypeError, ValueError, OverflowError):
        return None
