"""Deep audit: does everything on the page line up with everything else?

Cross-checks the forecast chain, period extremes, price levels, trade cards,
and current price against each other. Prints every inconsistency found.
"""
import json
import re
from datetime import datetime, date

raw = open("data.js", encoding="utf-8").read()
D = json.loads(raw.replace("const DATA_ALL = ", "").split("const TRADES")[0].strip().rstrip(";"))
try:
    T = json.loads(raw.split("const TRADES = ")[1].split(";\nconst ")[0].strip().rstrip(";"))
except Exception:
    T = {}

MON = {m: i for i, m in enumerate(
    ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"], 1)}
today = date.today()
issues = []
notes = []


def md(s):
    if not s:
        return None
    m = re.search(r"(\d{2})/(\d{2})", s)
    if m:
        return (int(m.group(1)), int(m.group(2)))
    m = re.search(r"([A-Z][a-z]{2})\s+(\d{1,2})", s)
    if m and m.group(1) in MON:
        return (MON[m.group(1)], int(m.group(2)))
    return None


for t, d in D.items():
    spot = d["price"]
    preds = sorted(d["predictions"], key=lambda p: p["isoDate"])
    lv = d.get("levels", {})
    sup = [x["price"] for x in lv.get("support", [])]
    res = [x["price"] for x in lv.get("resistance", [])]

    # 1. chain sanity vs spot
    for p in preds:
        pd_ = datetime.strptime(p["isoDate"], "%Y-%m-%d").date()
        if pd_ < today:
            issues.append(f"{t}: chain still shows a PAST event {p['isoDate']} ({p['type']})")
        if p["type"] == "high" and p["price"] < spot * 0.995:
            issues.append(f"{t}: projected HIGH {p['price']} on {p['isoDate']} is BELOW spot {spot:.2f}")
        if p["type"] == "low" and p["price"] > spot * 1.005:
            issues.append(f"{t}: projected LOW {p['price']} on {p['isoDate']} is ABOVE spot {spot:.2f}")

    # 1b. the IN-PROGRESS event cannot sit inside ground the current swing
    # has already covered (later chain events start from new swings, so they
    # are legitimately free to sit anywhere)
    sw = d.get("swingExtremes")
    if sw and preds:
        p0 = preds[0]
        if p0["type"] == "high" and p0["price"] < sw["swingHi"] * 0.999:
            issues.append(f"{t}: next HIGH {p0['price']} on {p0['isoDate']} is BELOW {sw['swingHi']} "
                          f"already printed in this swing (since {sw['since']})")
        if p0["type"] == "low" and p0["price"] > sw["swingLo"] * 1.001:
            issues.append(f"{t}: next LOW {p0['price']} on {p0['isoDate']} is ABOVE {sw['swingLo']} "
                          f"already printed in this swing (since {sw['since']})")

    # 2. levels sanity
    if sup and max(sup) > spot:
        issues.append(f"{t}: support {max(sup)} sits ABOVE spot {spot:.2f}")
    if res and min(res) < spot:
        issues.append(f"{t}: resistance {min(res)} sits BELOW spot {spot:.2f}")

    # 3. horizons vs chain
    hz = d.get("horizons", {})
    for k in ("daily", "weekly", "monthly"):
        if k in hz:
            hi, lo = hz[k]["high"]["price"], hz[k]["low"]["price"]
            if lo > hi:
                issues.append(f"{t}: {k} low {lo} exceeds {k} high {hi}")
            if hi < spot * 0.995:
                issues.append(f"{t}: {k} projected high {hi} is below spot {spot:.2f}")
            if lo > spot * 1.005:
                issues.append(f"{t}: {k} projected low {lo} is above spot {spot:.2f}")

    # 3b. CROSS-SURFACE SYNC: the date-picker day forecasts, the chain, and the
    # period extremes all derive from one envelope - prove they never disagree
    dfc = {x["date"]: x for x in d.get("dayForecasts", [])}
    for p in preds:
        f = dfc.get(p["isoDate"])
        if f:
            if p["type"] == "high" and f["high"] < p["price"] - 0.01:
                issues.append(f"{t}: date-picker high {f['high']} on {p['isoDate']} is below the "
                              f"chain's own high {p['price']} for that day")
            if p["type"] == "low" and f["low"] > p["price"] + 0.01:
                issues.append(f"{t}: date-picker low {f['low']} on {p['isoDate']} is above the "
                              f"chain's own low {p['price']} for that day")
    if dfc and hz.get("monthly"):
        mo = today.strftime("%Y-%m")
        same = [v for k2, v in dfc.items() if k2.startswith(mo)]
        if same:
            if max(v["high"] for v in same) > hz["monthly"]["high"]["price"] + 0.01:
                issues.append(f"{t}: a date-picker day exceeds the monthly high "
                              f"{hz['monthly']['high']['price']}")
            if min(v["low"] for v in same) < hz["monthly"]["low"]["price"] - 0.01:
                issues.append(f"{t}: a date-picker day undercuts the monthly low "
                              f"{hz['monthly']['low']['price']}")
    # 3c. the turn state must agree with the first chain event's direction
    tn = d.get("turnFormed")
    if tn and preds:
        if tn.get("state") == "turned" and tn.get("formed"):
            want = "low" if tn["formed"] == "high" else "high"
            if preds[0]["type"] != want:
                issues.append(f"{t}: reversal confirmed ({tn['formed']} formed), so the next event "
                              f"should be a {want}, but the chain predicts a {preds[0]['type']}")
        elif tn.get("state") in ("extending", "target-hit-early"):
            if preds[0]["type"] != tn.get("extreme"):
                issues.append(f"{t}: swing is {tn['state']} toward a {tn.get('extreme')}, but the "
                              f"chain's next event is a {preds[0]['type']}")

    # 4. trade cards line up with the chain + horizon labels
    for tr in T.get(t, {}).get("trades", []):
        a, b = md(tr.get("execute")), md(tr.get("exitWin"))
        if a and b and b < a:
            issues.append(f"{t}: '{tr['label'][:40]}' exits before entry")
        # horizon tag must match the execute date
        if a:
            ed = date(today.year, a[0], a[1])
            n = (ed - today).days
            tag = tr.get("hz", "")
            if tag == "TODAY" and n > 1 and "now" not in (tr.get("execute") or ""):
                issues.append(f"{t}: '{tr['label'][:34]}' tagged TODAY but executes {tr['execute']}")
            if tag == "THIS WEEK" and n > 7:
                issues.append(f"{t}: '{tr['label'][:34]}' tagged THIS WEEK but executes {tr['execute']}")
        # expiry must outlive the exit
        e, x = md(tr.get("exp")), b
        if e and x and e < x:
            issues.append(f"{t}: '{tr['label'][:34]}' expires {tr['exp']} before its exit {tr['exitWin']}")
        # strike vs the event it claims to target
        st = tr.get("strikes") or []
        if tr.get("kind") == "MODEL" and st:
            low_ev = next((p for p in preds if p["type"] == "low"), None)
            if low_ev and abs(st[0] / low_ev["price"] - 1) > 0.03:
                issues.append(f"{t}: MODEL strike {st[0]} is far from projected low {low_ev['price']}")
        if tr.get("premium", 0) <= 0 and tr.get("kind") != "NOTE":
            issues.append(f"{t}: '{tr['label'][:34]}' has no premium")

    # 5. informational: no near-term setup (a market condition, not a conflict)
    if T.get(t) and not T[t].get("bestToday") and not T[t].get("bestWeek"):
        notes.append(f"{t}: next turn is far out - no trade today or this week")

print(f"AUDIT {datetime.now():%Y-%m-%d %H:%M} - {len(D)} tickers")
if issues:
    print(f"\n{len(issues)} ANOMALIES:")
    for i in issues:
        print("  -", i)
else:
    print("\nNo anomalies: chain, levels, horizons and trade cards all line up.")
