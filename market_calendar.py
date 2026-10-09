"""NYSE regular-session calendar (holidays and 1:00 PM early closes), 2024-2027.

Checked against the exchange_calendars XNYS calendar on 2026-10-09. Dates
outside the table's years are unknown: callers must treat them as unverified
rather than guess a session.
"""
from datetime import date, datetime, time, timedelta

from market_time import EASTERN

YEARS = range(2024, 2028)

HOLIDAYS = {
    '2024-01-01', '2024-01-15', '2024-02-19', '2024-03-29', '2024-05-27', '2024-06-19',
    '2024-07-04', '2024-09-02', '2024-11-28', '2024-12-25',
    '2025-01-01', '2025-01-09', '2025-01-20', '2025-02-17', '2025-04-18', '2025-05-26',
    '2025-06-19', '2025-07-04', '2025-09-01', '2025-11-27', '2025-12-25',
    '2026-01-01', '2026-01-19', '2026-02-16', '2026-04-03', '2026-05-25', '2026-06-19',
    '2026-07-03', '2026-09-07', '2026-11-26', '2026-12-25',
    '2027-01-01', '2027-01-18', '2027-02-15', '2027-03-26', '2027-05-31', '2027-06-18',
    '2027-07-05', '2027-09-06', '2027-11-25', '2027-12-24',
}

EARLY_CLOSES = {
    '2024-07-03', '2024-11-29', '2024-12-24',
    '2025-07-03', '2025-11-28', '2025-12-24',
    '2026-11-27', '2026-12-24',
    '2027-11-26',
}

OPEN = time(9, 30)
CLOSE = time(16, 0)
EARLY_CLOSE = time(13, 0)


def known(day):
    return day.year in YEARS


def is_session(day):
    if not known(day):
        raise ValueError(f'no verified NYSE calendar for {day.year}')
    return day.weekday() < 5 and day.isoformat() not in HOLIDAYS


def session_bounds(day):
    """(open, close) as aware Eastern datetimes, or None when the market is shut."""
    if not is_session(day):
        return None
    close = EARLY_CLOSE if day.isoformat() in EARLY_CLOSES else CLOSE
    return (datetime.combine(day, OPEN, EASTERN), datetime.combine(day, close, EASTERN))


def expected_bars(day, minutes=15):
    bounds = session_bounds(day)
    if bounds is None:
        return 0
    return int((bounds[1] - bounds[0]).total_seconds() // (minutes * 60))


def next_session(day):
    """First session on or after day."""
    d = day
    for _ in range(15):
        if is_session(d):
            return d
        d += timedelta(days=1)
    raise ValueError(f'no session found after {day}')


def previous_session(day):
    """Last session strictly before day."""
    d = day - timedelta(days=1)
    for _ in range(15):
        if is_session(d):
            return d
        d -= timedelta(days=1)
    raise ValueError(f'no session found before {day}')


def target_session(now):
    """Session a forecast issued at `now` is about, and whether it is premarket.

    Before today's open (or on a closed day) the target is the next session and
    the forecast is premarket. During regular hours it is today's session and
    an intraday revision. After the close it is the next session, premarket.
    """
    now = now.astimezone(EASTERN)
    today = now.date()
    bounds = session_bounds(today) if is_session(today) else None
    if bounds and bounds[0] <= now < bounds[1]:
        return today, 'intraday'
    if bounds and now < bounds[0]:
        return today, 'premarket'
    return next_session(today + timedelta(days=1)), 'premarket'


def as_date(text):
    return date.fromisoformat(text) if isinstance(text, str) else text
