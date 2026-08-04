"""Buy-and-hold benchmark: what would simply HOLDING have returned?

Trailing total return + CAGR over 1/3/5/10/20 years for every ticker plus SPY
(the index everyone secretly loses to). Writes benchmark.json. Any active
system must beat these numbers to justify existing.
"""
import json
import time
import urllib.request
import numpy as np
import pandas as pd

TICKERS = [t.strip().upper() for t in open("tickers.txt") if t.strip()]
SPANS = [1, 3, 5, 10, 20]
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}


def spy_closes():
    url = (f"https://query1.finance.yahoo.com/v8/finance/chart/SPY"
           f"?period1=0&period2={int(time.time())}&interval=1d&includePrePost=false")
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=30) as r:
        res = json.load(r)["chart"]["result"][0]
    c = res["indicators"]["quote"][0]["close"]
    ts = res["timestamp"]
    s = pd.Series(c, index=pd.to_datetime(ts, unit="s")).dropna()
    return s


def spans_for(closes):
    out = {}
    last = float(closes.iloc[-1])
    for yrs in SPANS:
        n = yrs * 252
        if len(closes) <= n:
            continue
        start = float(closes.iloc[-n - 1])
        if start <= 0:
            continue
        total = last / start - 1
        cagr = (last / start) ** (1 / yrs) - 1
        out[str(yrs)] = {"totalPct": round(total * 100, 1),
                         "cagrPct": round(cagr * 100, 1)}
    return out


bench = {}
for t in TICKERS:
    try:
        df = pd.read_csv(f"{t}_daily.csv", parse_dates=["Datetime"], index_col="Datetime")
        bench[t] = spans_for(df["Close"].dropna())
    except Exception as e:
        print(f"{t}: {e}")
try:
    bench["SPY"] = spans_for(spy_closes())
except Exception as e:
    print("SPY fetch failed:", e)

with open("benchmark.json", "w", encoding="utf-8") as f:
    json.dump(bench, f, indent=1)

for t, v in bench.items():
    row = " | ".join(f"{y}y: {d['cagrPct']:+.1f}%/yr" for y, d in sorted(v.items(), key=lambda kv: int(kv[0])))
    print(f"{t:6} {row}")
