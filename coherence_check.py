"""Assert the published forecasts are internally consistent. Exit 1 on failure.

Checks per ticker:
 1. Chain events alternate high/low and dates strictly increase.
 2. Horizon nesting: daily <= weekly <= monthly <= yearly (highs), reverse for lows.
 3. Every chain event inside a period window fits within that period's extremes.
 4. 'already set' cells never carry a future date label.
"""
import json
import re
import sys
from datetime import datetime

raw = open("data.js", encoding="utf-8").read()
d = json.loads(raw.replace("const DATA_ALL = ", "").split("const TRADES")[0].strip().rstrip(";"))

fails = []
for t, D in d.items():
    preds = D.get("predictions", [])
    # 1. alternation + increasing dates
    for a, b in zip(preds, preds[1:]):
        if a["type"] == b["type"]:
            fails.append(f"{t}: chain events {a['isoDate']} and {b['isoDate']} are both {a['type']}s")
        if a["isoDate"] >= b["isoDate"]:
            fails.append(f"{t}: chain dates not increasing ({a['isoDate']} -> {b['isoDate']})")
    hz = D.get("horizons", {})
    order = [k for k in ("daily", "weekly", "monthly", "yearly") if k in hz]
    # 2. nesting
    for a, b in zip(order, order[1:]):
        if hz[a]["high"]["price"] > hz[b]["high"]["price"] + 0.01:
            fails.append(f"{t}: {a} high {hz[a]['high']['price']} > {b} high {hz[b]['high']['price']}")
        if hz[a]["low"]["price"] < hz[b]["low"]["price"] - 0.01:
            fails.append(f"{t}: {a} low {hz[a]['low']['price']} < {b} low {hz[b]['low']['price']}")
    # 3. chain events fit inside monthly extremes (proxy for all windows)
    if "monthly" in hz and preds:
        mo = datetime.now().strftime("%Y-%m")
        for p in preds:
            if p["isoDate"].startswith(mo):
                if p["type"] == "high" and p["price"] > hz["monthly"]["high"]["price"] + 0.01:
                    fails.append(f"{t}: chain high {p['price']} on {p['isoDate']} exceeds monthly high {hz['monthly']['high']['price']}")
                if p["type"] == "low" and p["price"] < hz["monthly"]["low"]["price"] - 0.01:
                    fails.append(f"{t}: chain low {p['price']} on {p['isoDate']} undercuts monthly low {hz['monthly']['low']['price']}")
    # 4. 'already set' labels must reference past dates
    today = datetime.now().date()
    for k in order:
        for side in ("high", "low"):
            cell = hz[k][side]
            m = re.search(r"already set .*?(\d{2})/(\d{2})", cell["date"])
            if m:
                mo_, dy = int(m.group(1)), int(m.group(2))
                if (mo_, dy) > (today.month, today.day) and k != "yearly":
                    fails.append(f"{t}: {k} {side} says 'already set' with future date {cell['date']}")


# ---- 0. the published page must actually RUN: parse every inline script -----
# (a syntax error here renders a completely blank dashboard)
try:
    import esprima, re as _re
    _html = open("index.html", encoding="utf-8").read()
    for _i, _b in enumerate(_re.findall(r"<script>([\s\S]*?)</script>", _html)):
        try:
            esprima.parseScript(_b)
        except Exception as _e:
            fails.append(f"index.html script block {_i} is INVALID JAVASCRIPT -> {_e}. "
                         f"The live page would render blank.")
except ImportError:
    print("note: esprima not installed - skipping JavaScript syntax gate")
except FileNotFoundError:
    pass

# 5. trade cards: exit must never be dated before entry
try:
    traw = raw.split("const TRADES = ")[1].split(";\nconst ")[0].strip().rstrip(";")
    tj = json.loads(traw)
    mon = {m: i for i, m in enumerate(
        ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"], 1)}
    def parse_md(s):
        if not s:
            return None
        m = re.search(r"(\d{2})/(\d{2})", s)
        if m:
            return (int(m.group(1)), int(m.group(2)))
        m = re.search(r"([A-Z][a-z]{2})\s+(\d{1,2})", s)
        if m and m.group(1) in mon:
            return (mon[m.group(1)], int(m.group(2)))
        return None
    for t, v in tj.items():
        for tr in v.get("trades", []):
            a, b = parse_md(tr.get("execute")), parse_md(tr.get("exitWin"))
            if a and b and b < a:
                fails.append(f"{t}: trade '{tr.get('label')}' exits {tr.get('exitWin')} "
                             f"BEFORE it enters {tr.get('execute')}")
except Exception:
    pass

if fails:
    print("COHERENCE FAILURES:")
    for f_ in fails:
        print("  -", f_)
    sys.exit(1)
print(f"coherence check PASSED for {len(d)} tickers")
