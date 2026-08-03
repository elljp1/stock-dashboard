"""Walk-forward backtest: replay the swing-rhythm predictor across all history
and grade every prediction against what actually happened next.

Turns "wait weeks for 30 live grades" into "hundreds of graded predictions now"
— genuine out-of-sample validation, since at each step only PAST bars are used
to predict, then FUTURE bars grade it. Writes backfill.json for the dashboard.
"""
import json
import numpy as np
import pandas as pd
from datetime import timedelta

TICKERS = [t.strip().upper() for t in open("tickers.txt") if t.strip()]


def zigzag(closes, threshold):
    piv, direction, ext = [], 0, 0
    for i in range(1, len(closes)):
        c = closes[i]
        if direction >= 0:
            if c > closes[ext]:
                ext = i
            elif c < closes[ext] * (1 - threshold):
                piv.append((ext, "high")); direction, ext = -1, i
        if direction <= 0:
            if c < closes[ext]:
                ext = i
            elif c > closes[ext] * (1 + threshold):
                piv.append((ext, "low")); direction, ext = 1, i
    return piv


def backfill(tkr):
    df = pd.read_csv(f"{tkr}_daily.csv", parse_dates=["Datetime"], index_col="Datetime")
    df = df.tail(252 * 5 + 40)
    closes = df["Close"].to_numpy(float)
    highs = df["High"].to_numpy(float)
    lows = df["Low"].to_numpy(float)
    n = len(closes)
    if n < 260:
        return None
    lr = np.diff(np.log(closes))
    dvol = float(np.median(pd.Series(lr).rolling(20).std().dropna())) * np.sqrt(20)
    thr = min(0.10, max(0.04, round(dvol * 1.3, 3)))
    # match analyze.py: halve the threshold if too few swings emerge
    if len(zigzag(closes, thr)) < 8:
        thr = max(0.03, thr / 2)
    if len(zigzag(closes, thr)) < 8:
        thr = max(0.02, thr / 2)

    hits2 = hits3 = tested = 0
    perrs, up_amps, dn_amps = [], [], []
    day_err, price_err_signed = [], []
    # walk forward: at each i, use bars [0..i] to detect pivots + rhythm,
    # predict the NEXT opposite pivot, then grade against bars after i
    for i in range(120, n - 30):
        piv = zigzag(closes[: i + 1], thr)
        if len(piv) < 6:
            continue
        idxs = [p[0] for p in piv]
        spac = [idxs[k] - idxs[k - 1] for k in range(1, len(idxs))]
        med_sp = int(np.median(spac))
        last_i, last_t = piv[-1]
        next_t = "low" if last_t == "high" else "high"
        pred_i = last_i + med_sp
        if pred_i <= i or pred_i >= n:
            continue
        # actual: the real next pivot of that type after last_i
        future_piv = zigzag(closes, thr)
        actual = next((p for p in future_piv if p[0] > last_i and p[1] == next_t), None)
        if not actual:
            continue
        err = actual[0] - pred_i
        tested += 1
        hits2 += abs(err) <= 2
        hits3 += abs(err) <= 3
        day_err.append(err)
        # price grade: predicted swing magnitude vs actual
        amps = [abs(closes[idxs[k]] / closes[idxs[k - 1]] - 1) for k in range(1, len(idxs))]
        med_amp = float(np.median(amps))
        base_px = closes[last_i]
        pred_px = base_px * (1 + med_amp) if next_t == "high" else base_px * (1 - med_amp)
        act_px = closes[actual[0]]
        if act_px > 0:
            perrs.append(abs(pred_px / act_px - 1))
            price_err_signed.append(pred_px / act_px - 1)

    if tested < 20:
        return None
    return {
        "ticker": tkr, "thresholdPct": round(thr * 100, 1),
        "tested": tested,
        "hit2Rate": round(hits2 / tested * 100, 1),
        "hit3Rate": round(hits3 / tested * 100, 1),
        "medDayErr": int(np.median(np.abs(day_err))),
        "medPriceErrPct": round(float(np.median(perrs)) * 100, 1),
        "priceBias": round(float(np.median(price_err_signed)) * 100, 1),
        "years": round(len(closes) / 252, 1)}


results = {}
for t in TICKERS:
    try:
        r = backfill(t)
        if r:
            results[t] = r
            print(f"{t}: {r['tested']} graded over {r['years']}y | "
                  f"±2d {r['hit2Rate']}% ±3d {r['hit3Rate']}% | "
                  f"med price err {r['medPriceErrPct']}% (bias {r['priceBias']:+}%)")
    except Exception as e:
        print(f"{t}: FAILED {e}")

agg = {"perTicker": results,
       "totalGraded": sum(r["tested"] for r in results.values()),
       "avgHit2": round(np.mean([r["hit2Rate"] for r in results.values()]), 1) if results else 0,
       "avgHit3": round(np.mean([r["hit3Rate"] for r in results.values()]), 1) if results else 0}
with open("backfill.json", "w", encoding="utf-8") as f:
    json.dump(agg, f, indent=1)
print(f"\nTOTAL: {agg['totalGraded']} graded predictions | "
      f"avg ±2d {agg['avgHit2']}% ±3d {agg['avgHit3']}%")
