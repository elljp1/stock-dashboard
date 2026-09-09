"""GitHub-only schedule selection and catch-up, using published analysis time."""
import json
import os
import urllib.request
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

EASTERN = ZoneInfo("America/New_York")
LIVE_REVIEW = "https://elljp1.github.io/stock-dashboard/daily_review.json"


def due_slot(now):
    now = now.astimezone(EASTERN)
    minute = now.hour * 60 + now.minute
    if not 360 <= minute <= 1140:
        return None
    slots = [1080]  # Daily 18:00 review, including weekends.
    if now.weekday() < 5:
        slots += [360, 420, 480, 540, 555, 560, 565, 570, 575, 585]
        slots += list(range(600, 1021, 30))
    due = [m for m in slots if m <= minute]
    if not due:
        return None
    m = max(due)
    return now.replace(hour=m // 60, minute=m % 60, second=0, microsecond=0)


def decision(now, reviewed_at=None, event="schedule"):
    if event != "schedule":
        return True, "Code push or manual refresh"
    due = due_slot(now)
    if due is None:
        return False, "Outside requested refresh/recovery hours"
    try:
        reviewed = datetime.fromisoformat(reviewed_at)
        if reviewed.tzinfo is None or reviewed > now + timedelta(minutes=1):
            raise ValueError("Invalid timestamp")
    except (TypeError, ValueError):
        return True, "Published freshness unavailable; rebuilding"
    if reviewed >= due:
        return False, "Latest requested slot is already published"
    return True, f"Refresh due {due:%Y-%m-%d %H:%M %Z}; last publication {reviewed.astimezone(EASTERN):%H:%M:%S %Z}"


def main():
    now = datetime.now(EASTERN)
    event = os.environ.get("EVENT_NAME", "schedule")
    reviewed = None
    if event == "schedule" and due_slot(now):
        try:
            request = urllib.request.Request(
                LIVE_REVIEW + "?check=" + str(int(now.timestamp())),
                headers={"Cache-Control": "no-cache"},
            )
            with urllib.request.urlopen(request, timeout=20) as response:
                reviewed = json.load(response)["reviewedAt"]
        except Exception:
            pass  # A failed check must not suppress recovery.
    should_run, reason = decision(now, reviewed, event)
    with open(os.environ["GITHUB_OUTPUT"], "a", encoding="utf-8") as output:
        output.write("should_run=" + str(should_run).lower() + "\n")
    message = f"Checked {now:%Y-%m-%d %H:%M:%S %Z}: {reason}. Refresh={should_run}"
    print(message)
    if os.environ.get("GITHUB_STEP_SUMMARY"):
        with open(os.environ["GITHUB_STEP_SUMMARY"], "a", encoding="utf-8") as summary:
            summary.write(message + "\n")


if __name__ == "__main__":
    main()
