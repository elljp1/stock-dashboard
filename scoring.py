"""Prospective-only helpers for forecast grading."""

from datetime import date, datetime, timedelta


def monthly_chain_failures(ticker, data):
    """Check the resolver's remaining-session window, not expired chart calls.

    Original chart calls remain intact for historical comparison. After close,
    the resolver advances to the next session and no longer includes today's
    missed target. Legacy builds derive the same window from their build time,
    never from the checker machine's current date.
    """
    if "monthly" not in data.get("horizons", {}):
        return []
    if data.get("horizonSession"):
        session = date.fromisoformat(data["horizonSession"])
    else:
        built = datetime.strptime(data["generated"][:19], "%Y-%m-%d %I:%M %p")
        last = date.fromisoformat(data["chart"]["dates"][-1])
        session = last
        if built.date() != last or built.hour >= 16:
            session += timedelta(days=1)
            while session.weekday() >= 5:
                session += timedelta(days=1)
    errors = []
    month = data["horizons"]["monthly"]
    for pred in data.get("predictions", []):
        target = date.fromisoformat(pred["isoDate"])
        if target < session or (target.year, target.month) != (session.year, session.month):
            continue
        side = pred["type"]
        limit = month[side]["price"]
        if (pred["price"] > limit + .01 if side == "high" else pred["price"] < limit - .01):
            errors.append(f"{ticker}: active chain {side} {pred['price']} on {target} "
                          f"outside monthly {side} {limit}")
    return errors


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
