"""Append-only helpers for honest day-ahead horizon grading."""


def record_horizon(entries, entry):
    """Append one original forecast per ticker/session without erasing history.

    A later run may advance to a later target session on the same calendar day,
    but a stale run may not move that day's target backward.
    """
    ticker, session, logged = entry["ticker"], entry["session"], entry["logged"]
    if any(e["ticker"] == ticker and e["session"] == session for e in entries):
        return False
    same_day = [e["session"] for e in entries
                if e["ticker"] == ticker and e["logged"] == logged]
    if same_day and session < max(same_day):
        return False
    entries.append(entry)
    return True


def original_horizons(entries, ticker):
    """Return the first logged forecast for each session, in session order."""
    selected = {}
    for position, entry in enumerate(entries):
        if entry["ticker"] != ticker:
            continue
        key = entry["session"]
        rank = (entry["logged"], position)
        if key not in selected or rank < selected[key][0]:
            selected[key] = (rank, entry)
    return [selected[key][1] for key in sorted(selected)]
