"""Prospective-only helpers for forecast grading."""


def nearest_prospective_pivot(pivots, kind, predicted_date, logged_date, td_pos):
    """Return the nearest matching pivot that was not knowable when logged.

    Daily forecasts are produced after the current data has been downloaded, so
    a pivot on or before the log date is retrospective and must never earn a hit.
    """
    candidates = [
        pivot for pivot in pivots
        if pivot["type"] == kind and pivot["date"].date() > logged_date
    ]
    if not candidates:
        return None
    return min(
        candidates,
        key=lambda pivot: abs(td_pos(pivot["date"].date()) - td_pos(predicted_date)),
    )
