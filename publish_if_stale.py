"""Publish from this laptop ONLY when the cloud copy is stale.

GitHub's scheduled workflows are unreliable (today they fired 3 times instead
of 8). This makes the laptop a safety net without causing the deploy
collisions that come from two publishers pushing on every run.
"""
import json
import re
import subprocess
import urllib.request
from datetime import datetime
from zoneinfo import ZoneInfo

ET = ZoneInfo("America/New_York")
STALE_MINUTES = 75
RAW = "https://raw.githubusercontent.com/elljp1/stock-dashboard/main/data.js"


def stamp_of(text):
    m = re.search(r'"generated": "(\d{4})-(\d{2})-(\d{2}) (\d{2}):(\d{2}) (AM|PM)', text)
    if not m:
        return None
    hr = int(m.group(4)) % 12 + (12 if m.group(6) == "PM" else 0)
    return datetime(int(m.group(1)), int(m.group(2)), int(m.group(3)),
                    hr, int(m.group(5)), tzinfo=ET)


try:
    remote = urllib.request.urlopen(RAW + "?t=" + str(datetime.now().timestamp()),
                                    timeout=30).read().decode("utf-8", "ignore")
    r_time = stamp_of(remote)
except Exception as e:
    print("could not read the published copy:", e)
    r_time = None

local = open("data.js", encoding="utf-8").read()
l_time = stamp_of(local)
now = datetime.now(ET)

if not l_time:
    print("local data has no timestamp - skipping")
elif r_time and (now - r_time).total_seconds() / 60 < STALE_MINUTES:
    print(f"published copy is fresh ({r_time:%I:%M %p ET}) - laptop stays out of the way")
elif r_time and l_time <= r_time:
    print("local copy is not newer than published - nothing to publish")
else:
    print(f"published copy stale ({r_time:%I:%M %p ET} vs local {l_time:%I:%M %p ET}) - publishing")
    for f in ["index.html", "dashboard_single.html", "data.js", "predictions_log.json",
              "daily_extremes.json", "trades.json", "trades_log.json",
              "horizons_log.json", "benchmark.json", "backfill.json"]:
        try:
            subprocess.run(["cp", f, f"site/{f}"], check=False)
        except Exception:
            pass
    subprocess.run(["git", "-C", "site", "pull", "--rebase", "origin", "main"], check=False)
    subprocess.run(["git", "-C", "site", "add", "-A"], check=False)
    subprocess.run(["git", "-C", "site", "commit", "-m", "backup publish (cloud schedule missed)"],
                   check=False)
    subprocess.run(["git", "-C", "site", "push", "origin", "main"], check=False)
    print("published from laptop")
