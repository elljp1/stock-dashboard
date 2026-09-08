"""Download price data for every ticker in tickers.txt from Yahoo's chart API."""
import urllib.request
import json
import time
import sys
from pathlib import Path
import pandas as pd
from zoneinfo import ZoneInfo

ET = ZoneInfo("America/New_York")
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

with open("tickers.txt") as f:
    TICKERS = [t.strip().upper() for t in f if t.strip()]


def fetch(ticker, rng, interval, tries=3):
    if rng == "max":
        # explicit epoch range forces true daily bars for full history
        span = f"period1=0&period2={int(time.time())}"
    else:
        span = f"range={rng}"
    url = (f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}"
           f"?{span}&interval={interval}&includePrePost=false&events=div|split")
    req = urllib.request.Request(url, headers=UA)
    d = None
    for k in range(tries):
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                d = json.load(r)
            break
        except Exception:
            if k == tries - 1:
                raise
            time.sleep(8)
    res = d["chart"]["result"][0]
    ts = res["timestamp"]
    q = res["indicators"]["quote"][0]
    df = pd.DataFrame({
        "Open": q["open"], "High": q["high"], "Low": q["low"],
        "Close": q["close"], "Volume": q["volume"],
    }, index=pd.to_datetime(ts, unit="s", utc=True).tz_convert(ET))
    df.index.name = "Datetime"
    df = df.dropna(subset=["Open", "High", "Low", "Close"])
    return df, res["meta"]


failures = []
for tkr in TICKERS:
    print(f"--- {tkr} ---")
    try:
        for rng, interval, name in [("max", "1d", "daily"),
                                    ("730d", "1h", "hourly"),
                                    ("60d", "15m", "15m")]:
            df, meta = fetch(tkr, rng, interval)
            if df.empty:
                raise ValueError("empty price response")
            target = Path(f"{tkr}_{name}.csv")
            temp = target.with_suffix(".csv.tmp")
            df.to_csv(temp)
            temp.replace(target)
            print(f"  {name}: {len(df)} rows, {df.index[0].date()} -> {df.index[-1].date()}")
            time.sleep(0.5)  # be polite to Yahoo
        print("  price:", meta["regularMarketPrice"])
    except Exception as e:
        print(f"  FAILED: {e}")
        failures.append(tkr)

# latest trade INCLUDING pre/post-market, so early-morning runs price reality
pm = {}
quotes = {}
for tkr in TICKERS:
    try:
        url = (f"https://query1.finance.yahoo.com/v8/finance/chart/{tkr}"
               f"?range=1d&interval=5m&includePrePost=true")
        req = urllib.request.Request(url, headers=UA)
        with urllib.request.urlopen(req, timeout=30) as r:
            res = json.load(r)["chart"]["result"][0]
        closes = res["indicators"]["quote"][0]["close"]
        trades = [(ts, close) for ts, close in zip(res.get("timestamp", []), closes)
                  if close is not None]
        if trades:
            quote_ts, quote_price = trades[-1]
            pm[tkr] = round(float(quote_price), 4)
            quotes[tkr] = {
                "price": pm[tkr],
                "quoteTime": pd.Timestamp(quote_ts, unit="s", tz="UTC").tz_convert(ET).isoformat(),
                "regularMarketTime": pd.Timestamp(
                    res["meta"]["regularMarketTime"], unit="s", tz="UTC"
                ).tz_convert(ET).isoformat(),
            }
    except Exception as e:
        print(f"  pre/post {tkr} failed: {e}")
with open("premarket.json", "w", encoding="utf-8") as f:
    json.dump({"asof": time.time(), "prices": pm, "quotes": quotes}, f)
print("pre/post prices:", pm)

if failures:
    sys.exit("Incomplete data download: " + ", ".join(failures))
