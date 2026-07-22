"""Download price data for every ticker in tickers.txt from Yahoo's chart API."""
import urllib.request
import json
import time
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


for tkr in TICKERS:
    print(f"--- {tkr} ---")
    try:
        for rng, interval, name in [("max", "1d", "daily"),
                                    ("730d", "1h", "hourly"),
                                    ("60d", "15m", "15m")]:
            df, meta = fetch(tkr, rng, interval)
            df.to_csv(f"{tkr}_{name}.csv")
            print(f"  {name}: {len(df)} rows, {df.index[0].date()} -> {df.index[-1].date()}")
            time.sleep(0.5)  # be polite to Yahoo
        print("  price:", meta["regularMarketPrice"])
    except Exception as e:
        print(f"  FAILED: {e}")
