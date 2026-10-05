"""Shared market-clock helpers for Eastern-date business rules."""

from datetime import datetime, timezone
from zoneinfo import ZoneInfo


EASTERN = ZoneInfo("America/New_York")


def eastern_now(now=None):
    """Return an aware Eastern datetime, optionally converting a supplied instant."""
    current = now if now is not None else datetime.now(timezone.utc)
    if current.tzinfo is None:
        raise ValueError("now must be timezone-aware")
    return current.astimezone(EASTERN)


def eastern_date(now=None):
    """Return the New York calendar date for an instant."""
    return eastern_now(now).date()
