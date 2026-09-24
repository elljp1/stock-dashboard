"""Vibration lab: find which Gann, planetary-degree and self-similar cycle tools
are "in play" for each stock, and when they next fire.

Each stock is tested on its own full daily history. Every tool is scored
walk-forward: a tool may only use swings that were already confirmed when it
issued its call, and only calls dated after the issue day count.

Tool families (each item below is a separately scored tool):
  time counts     calendar-day counts from confirmed major turns (Gann counts,
                  squares of numbers, Square-of-Nine spiral numbers)
  year circle     1/8 and 1/3 divisions of the year from a major turn;
                  anniversaries at 1, 10 and 20 years; seasonal Sun dates
  time = price    turn when elapsed days equal the anchor price (x scale)
  range squared   turn when elapsed days equal the prior swing's range / unit
  price = time    same-day call when points travelled / unit = days elapsed
  swing ratios    next turn at the prior swing's duration x ratio, and the
                  last MAJOR swing's duration scaled down (cycle in a cycle)
  planet degree   a planet reaches the anchor price's degree (price mod 360);
                  a planet returns to (or squares/opposes) its own position
                  at the anchor turn; price itself sits on a planet's degree
  analog scale    today's shape matched against history compressed 1x-8x
                  (a small cycle repeating a larger one); next turn projected
  price levels    1/8ths of the last major range, Square-of-Nine levels and
                  planetary longitude levels, scored on turn prices

Scoring: a call hits when a confirmed swing turn (the app's threshold) lands
within +-2 sessions. Chance is measured by shifting the tool's own calls in
time 300 times, which keeps their number and spacing. History is split: the
first 70% selects (Benjamini-Hochberg, q = 0.10, lift >= 1.2); a tool is IN
PLAY only if it also beats chance on the last 30% it was not selected on.
That later 30% was still visible on the dashboard before, so the prospective
record (calls logged from now on) is the only unseen test.

Output: gann_lab.json. Recomputed at most every 7 days unless --force.
Nothing here changes forecasts or weights.
"""
import json
import math
import os
import sys
from datetime import date, datetime, timedelta

import numpy as np
import pandas as pd

OUT = "gann_lab.json"
MAX_AGE_DAYS = 7
WINDOW = 2
SPLIT = 0.70
FDR_Q = 0.10
LIFT_BAR = 1.2
N_SEL = 15
N_HOLD = 8
HOLD_P = 0.20
DRAWS = 300
MAJOR_MULT = 2.5
PLANETS = ["Sun", "Mercury", "Venus", "Mars", "Jupiter", "Saturn"]

GANN_COUNTS = [30, 45, 60, 72, 90, 120, 135, 144, 150, 180, 210, 225, 240,
               270, 300, 315, 330, 360, 450, 540, 720]
SQUARES = [n * n for n in range(5, 28)]
# numbers on the 45-degree arms of the Square of Nine spiral
SQ9 = sorted({(2 * r + 1) ** 2 - k * r for r in range(1, 14) for k in range(0, 8, 1)
              if (2 * r + 1) ** 2 - k * r > 1})
UNITS = [0.1, 0.25, 0.5, 1, 2, 4, 8]
SWING_RATIOS = [0.5, 0.618, 1.0, 1.272, 1.618, 2.0]
MAJOR_FRACTIONS = [0.125, 0.25, 0.333, 0.5]
ANALOG_SCALES = [1, 2, 4, 8]
ANALOG_LEN = 60


# ------------------------------------------------------------------ swings
def zigzag(close, thresh_pct):
    """Swing turns (index, type, index at which the turn was confirmed)."""
    th = thresh_pct / 100.0
    piv, direction = [], 0
    hi_i = lo_i = ext_i = 0
    for i in range(1, len(close)):
        p = close[i]
        if direction == 0:
            hi_i = i if p > close[hi_i] else hi_i
            lo_i = i if p < close[lo_i] else lo_i
            if p < close[hi_i] * (1 - th):
                piv.append((hi_i, "high", i)); direction = -1
                ext_i = hi_i + int(np.argmin(close[hi_i:i + 1]))
            elif p > close[lo_i] * (1 + th):
                piv.append((lo_i, "low", i)); direction = 1
                ext_i = lo_i + int(np.argmax(close[lo_i:i + 1]))
        elif direction > 0:
            if p > close[ext_i]:
                ext_i = i
            elif p < close[ext_i] * (1 - th):
                piv.append((ext_i, "high", i)); direction = -1; ext_i = i
        else:
            if p < close[ext_i]:
                ext_i = i
            elif p > close[ext_i] * (1 + th):
                piv.append((ext_i, "low", i)); direction = 1; ext_i = i
    return piv


# ------------------------------------------------------------------ calendar
class Calendar:
    def __init__(self, sessions):
        self.s = sessions
        self.first, self.last = sessions[0], sessions[-1]
        self.idx = {d: i for i, d in enumerate(sessions)}

    def session(self, d):
        """Next trading session on/after a calendar date (None past history)."""
        for k in range(5):
            i = self.idx.get(d + timedelta(days=k))
            if i is not None:
                return i
        return None


def future_sessions(last_day, n):
    out, d = [], last_day
    while len(out) < n:
        d += timedelta(days=1)
        if d.weekday() < 5:
            out.append(d)
    return out


# ------------------------------------------------------------------ ephemeris
def ephemeris(d0, d1, bodies):
    import ephem
    days = pd.date_range(d0, d1, freq="D").date
    lon = {b: np.empty(len(days)) for b in bodies}
    for i, dt in enumerate(days):
        ds = dt.strftime("%Y/%m/%d")
        for b in bodies:
            body = getattr(ephem, b)()
            body.compute(ds)
            lon[b][i] = math.degrees(float(ephem.Ecliptic(body).lon))
    return days, lon


def wrap180(x):
    return (x + 180.0) % 360.0 - 180.0


# ------------------------------------------------------------------ scoring
def binom_sf(k, n, p):
    """P(X >= k), X ~ Binomial(n, p)."""
    if k <= 0:
        return 1.0
    p = min(max(p, 1e-9), 1 - 1e-9)
    return min(1.0, sum(math.exp(math.lgamma(n + 1) - math.lgamma(x + 1) - math.lgamma(n - x + 1)
                                 + x * math.log(p) + (n - x) * math.log(1 - p))
                        for x in range(k, n + 1)))


def result(hits, n, ctrl):
    """Chance = the tool's own calls moved in time. p = binomial tail at that
    chance rate (fine-grained enough for FDR); pPerm = the shifted copies."""
    c = float(ctrl.mean())
    rate = min(max(c / n, 1e-6), 1 - 1e-6)
    return {"n": n, "hits": int(hits), "hitPct": round(100 * hits / n, 1),
            "chancePct": round(100 * c / n, 1),
            "lift": round(hits / c, 2) if c > 0 else None,
            "p": float(f"{binom_sf(int(hits), n, rate):.3g}"),
            "pPerm": round(float((1 + (ctrl >= hits).sum()) / (1 + len(ctrl))), 4)}


def score(targets, near, rng, lo, hi):
    """Hits among distinct target sessions in [lo, hi) vs time-shifted copies."""
    t = np.array(sorted({x for x in targets if lo <= x < hi}), dtype=int)
    n = len(t)
    if n == 0:
        return {"n": 0}
    hits = int(near[t].sum())
    span = hi - lo
    shifts = rng.integers(10, 251, DRAWS) * rng.choice([-1, 1], DRAWS)
    ctrl = np.empty(DRAWS)
    for k, sh in enumerate(shifts):
        ctrl[k] = near[lo + ((t - lo + sh) % span)].sum()
    return result(hits, n, ctrl)


def score_levels(pivot_prices, level_sets, tol, rng):
    """Turn prices within tol of the tool's levels vs randomly nudged prices."""
    if not pivot_prices:
        return {"n": 0}
    pp = np.array(pivot_prices, float)

    def count(prices):
        return sum(bool(len(L)) and np.min(np.abs(np.array(L) - x)) <= tol * x
                   for x, L in zip(prices, level_sets))
    hits = count(pp)
    ctrl = np.empty(DRAWS // 3)
    for k in range(len(ctrl)):
        eps = rng.uniform(0.02, 0.10, len(pp)) * rng.choice([-1, 1], len(pp))
        ctrl[k] = count(pp * (1 + eps))
    return result(hits, len(pp), ctrl)


def bh_pass(rows, q):
    ps = sorted((r["sel"]["p"], i) for i, r in enumerate(rows) if r["sel"].get("n"))
    m, cut = len(ps), -1
    for k, (p, _) in enumerate(ps, 1):
        if p <= q * k / m:
            cut = k
    return {i for _, i in ps[:cut]} if cut > 0 else set()


# ------------------------------------------------------------------ tools
def time_tools(cal, close, majors, minors, lon_days, lon):
    """{tool: (family, [(issue_idx, target_date), ...])} for time tools."""
    tools = {}

    def add(name, fam, issue, d):
        tools.setdefault(name, (fam, []))[1].append((issue, d))

    s = cal.s
    lon_pos = {d: k for k, d in enumerate(lon_days)} if lon_days is not None else {}
    for (i, ty, c) in majors:
        d0, p0 = s[i], close[i]
        for n in GANN_COUNTS:
            add(f"{n} calendar days from a major turn", "time counts", c, d0 + timedelta(days=n))
        for n in SQUARES:
            add("squares of numbers (25..729 days)", "time counts", c, d0 + timedelta(days=n))
        for n in SQ9:
            if n <= 800:
                add("Square of Nine spiral numbers (days)", "time counts", c, d0 + timedelta(days=n))
        for k in range(1, 17):
            add("1/8 divisions of the year", "year circle", c, d0 + timedelta(days=round(365.25 * k / 8)))
        for k in range(1, 7):
            add("1/3 divisions of the year", "year circle", c, d0 + timedelta(days=round(365.25 * k / 3)))
        for yrs, label in ((range(1, 8), "1-year anniversaries"),
                           ((10,), "10-year anniversaries"), ((20,), "20-year anniversaries")):
            for y in yrs:
                try:
                    add(f"{label} of major turns", "year circle", c, d0.replace(year=d0.year + y))
                except ValueError:
                    add(f"{label} of major turns", "year circle", c, d0.replace(year=d0.year + y, day=28))
        for m in (0.1, 1, 10):
            n = round(p0 * m)
            if 5 <= n <= 1500:
                add(f"time = price x{m:g} (days = anchor price)", "time = price", c, d0 + timedelta(days=n))
        # planets from the anchor: degree of the anchor price, and returns
        if lon_days is not None:
            base = lon_pos.get(d0)
            if base is not None:
                deg = p0 % 360
                for b in PLANETS:
                    seg = lon[b][base + 1: base + 1 + 900]
                    for A, lab in ((0, "reaches"), (90, "squares"), (180, "opposes")):
                        sep = wrap180(seg - (deg + A))
                        cross = np.where(np.sign(sep[:-1]) * np.sign(sep[1:]) < 0)[0]
                        for j in cross[:6]:
                            if abs(sep[j]) < 20:
                                add(f"{b} {lab} the anchor price's degree", "planet degree", c,
                                    lon_days[base + 1 + j])
                    if b != "Sun":
                        natal = lon[b][base]
                        for A, lab in ((0, "returns to"), (90, "squares"), (180, "opposes")):
                            sep = wrap180(seg - (natal + A))
                            cross = np.where(np.sign(sep[:-1]) * np.sign(sep[1:]) < 0)[0]
                            for j in cross[:6]:
                                if abs(sep[j]) < 20:
                                    add(f"{b} {lab} its place at the anchor turn", "planet degree", c,
                                        lon_days[base + 1 + j])

    # swings: range squared, duration ratios, cycle within a cycle
    for a, b in zip(minors, minors[1:]):
        ia, ib, cb = a[0], b[0], b[2]
        rng_pts = abs(close[ib] - close[ia])
        dur = ib - ia
        for u in UNITS:
            n = round(rng_pts / u)
            if 3 <= n <= 900:
                add(f"range squared in time, {u:g} pt/day", "range squared", cb, s[ib] + timedelta(days=n))
        for r in SWING_RATIOS:
            j = ib + round(dur * r)
            if j < len(s):
                add(f"prior swing duration x{r:g}", "swing ratios", cb, s[j])
            else:
                add(f"prior swing duration x{r:g}", "swing ratios", cb, None)
    for a, b in zip(majors, majors[1:]):
        dur, cb = b[0] - a[0], b[2]
        for f in MAJOR_FRACTIONS:
            step = max(3, round(dur * f))
            for k in range(1, int(1 / f) + 1):
                j = b[0] + step * k
                add(f"major cycle / {round(1 / f)} repeating", "swing ratios", cb,
                    s[j] if j < len(s) else None)

    # seasonal: Sun on the cardinal and cross-quarter points (every year)
    if lon_days is not None:
        sun = lon["Sun"]
        for A in range(0, 360, 45):
            sep = wrap180(sun - A)
            cross = np.where(np.sign(sep[:-1]) * np.sign(sep[1:]) < 0)[0]
            for j in cross:
                if abs(sep[j]) < 20:
                    d = lon_days[j + 1]
                    ci = cal.session(d)
                    issue = 0 if ci is None else max(0, ci - 30)
                    add("seasonal dates (Sun at each 45 degrees)", "year circle", issue, d)
    return tools


def same_day_tools(cal, close, majors, lon_days, lon):
    """Calls issued the day a condition is met (price meets time / a degree)."""
    tools = {}
    s = cal.s
    anchors = sorted(majors, key=lambda m: m[2])
    for u in UNITS:
        hits = []
        for k, (i, ty, c) in enumerate(anchors):
            end = anchors[k + 1][2] if k + 1 < len(anchors) else len(s)
            elapsed = np.array([(s[j] - s[i]).days for j in range(c, end)])
            if not len(elapsed):
                continue
            moved = np.abs(close[c:end] - close[i]) / u
            gap = moved - elapsed
            cross = np.where(np.sign(gap[:-1]) * np.sign(gap[1:]) < 0)[0] + 1
            hits += [c + j for j in cross]
        tools[f"price squares time, {u:g} pt/day"] = ("price = time", hits)
    if lon_days is not None:
        pos = {d: i for i, d in enumerate(lon_days)}
        for b in PLANETS:
            hits = []
            for j, d in enumerate(s):
                q = pos.get(d)
                if q is not None and abs(wrap180(close[j] % 360 - lon[b][q])) <= 1.0:
                    hits.append(j)
            # one call per contact, not one per day of it
            hits = [h for n, h in enumerate(hits) if n == 0 or h - hits[n - 1] > 3]
            tools[f"price on {b}'s degree (price mod 360)"] = ("planet degree", hits)
    return tools


def analog_tools(close, minors, step=5):
    """Match today's shape against history compressed by each scale."""
    lc = np.log(close)
    n = len(lc)
    tools = {}
    piv_idx = np.array([m[0] for m in minors])
    piv_conf = np.array([m[2] for m in minors])
    for sc in ANALOG_SCALES:
        series = lc[::sc] if sc > 1 else lc
        W = ANALOG_LEN
        if len(series) < W * 3:
            continue
        win = np.lib.stride_tricks.sliding_window_view(series, W)
        z = (win - win.mean(1, keepdims=True)) / (win.std(1, keepdims=True) + 1e-12)
        calls = []
        for t in range(W * sc * 3, n - 1, step):
            q = lc[t - W + 1: t + 1]
            q = (q - q.mean()) / (q.std() + 1e-12)
            # candidate windows must end well before today in real time
            last_end = (t - W * 2) // sc - (W - 1)
            if last_end < 1:
                continue
            corr = z[:last_end] @ q / W
            j = int(np.argmax(corr))
            end_real = (j + W - 1) * sc
            known = piv_idx[(piv_conf <= t) & (piv_idx > end_real)]
            if not len(known):
                continue
            ahead = int(known[0] - end_real)
            calls.append((t, t + max(1, round(ahead / sc) if sc > 1 else ahead)))
        tools[f"history analog at {sc}x time scale"] = ("analog scale", calls)
    return tools


def level_tools(close, majors, minors, lon_days, lon, cal):
    """{tool: (family, pivot prices, level sets)} for price-level tools."""
    out = {}
    pos = {d: i for i, d in enumerate(lon_days)} if lon_days is not None else {}
    for (i, ty, c) in minors:
        prior = [m for m in majors if m[2] <= i]
        if len(prior) < 2:
            continue
        a, b = prior[-2], prior[-1]
        hi, lo = max(close[a[0]], close[b[0]]), min(close[a[0]], close[b[0]])
        eighths = [lo + (hi - lo) * k / 8 for k in range(0, 9)]
        eighths += [lo + (hi - lo) * k / 3 for k in (1, 2)]
        root = math.sqrt(close[b[0]])
        sq9 = [(root + k * 0.25) ** 2 for k in range(-8, 9) if root + k * 0.25 > 0]
        for name, L in (("1/8ths and 1/3rds of the last major range", eighths),
                        ("Square of Nine levels from the last major turn", sq9)):
            fam, pp, ls = out.setdefault(name, ("price levels", [], []))
            pp.append(close[i]); ls.append(L)
        q = pos.get(cal.s[i])
        if q is not None:
            for bdy in PLANETS:
                L = [lon[bdy][q] + 360 * k for k in range(0, int(close[i] / 360) + 3)]
                fam, pp, ls = out.setdefault(f"{bdy}'s longitude as a price", ("price levels", [], []))
                pp.append(close[i]); ls.append(L)
    return out


# ------------------------------------------------------------------ per ticker
def analyze_ticker(df, thresh, today, eph=None, seed=7, null=False):
    rng = np.random.default_rng(seed)
    sessions = [d.date() for d in df.index]
    cal = Calendar(sessions)
    close = df["Close"].to_numpy(float)
    n = len(close)
    minors = zigzag(close, thresh)
    majors = zigzag(close, thresh * MAJOR_MULT)
    near = np.zeros(n + 1, bool)
    for i, _, _ in minors:
        near[max(0, i - WINDOW): i + WINDOW + 1] = True
    # the last sessions cannot be graded: a turn there is not yet confirmable
    graded_end = max((c for _, _, c in minors), default=0)
    split = int(graded_end * SPLIT)
    lon_days, lon = (eph if eph else (None, None))
    if lon_days is not None:
        lon_days = list(lon_days)

    rows = []
    tt = time_tools(cal, close, majors, minors, lon_days, lon)
    for name, (fam, calls) in tt.items():
        targets = []
        for issue, d in calls:
            if d is None:
                continue
            j = cal.session(d)
            if j is not None and j > issue:
                targets.append(j)
        rows.append({"tool": name, "family": fam,
                     "sel": score(targets, near, rng, 0, split),
                     "hold": score(targets, near, rng, split, graded_end)})
    for name, (fam, idxs) in {**same_day_tools(cal, close, majors, lon_days, lon),
                              **{k: (v[0], [t for _, t in v[1]])
                                 for k, v in analog_tools(close, minors).items()}}.items():
        rows.append({"tool": name, "family": fam,
                     "sel": score(idxs, near, rng, 0, split),
                     "hold": score(idxs, near, rng, split, graded_end)})

    lv = level_tools(close, majors, minors, lon_days, lon, cal)
    piv_i = [m[0] for m in minors if m[2] <= graded_end]
    for name, (fam, pp, ls) in lv.items():
        # level sets align with minors that had 2 prior majors; split by order
        k = int(len(pp) * SPLIT)
        rows.append({"tool": name, "family": fam, "tol": "1% of price",
                     "sel": score_levels(pp[:k], ls[:k], 0.01, rng),
                     "hold": score_levels(pp[k:], ls[k:], 0.01, rng)})

    selected = bh_pass(rows, FDR_Q)
    for i, r in enumerate(rows):
        s, h = r["sel"], r["hold"]
        passed = (i in selected and s.get("n", 0) >= N_SEL and (s.get("lift") or 0) >= LIFT_BAR
                  and s.get("pPerm", 1) <= 0.05)
        held = (h.get("n", 0) >= N_HOLD and (h.get("lift") or 0) > 1.0 and h.get("p", 1) <= HOLD_P)
        r["verdict"] = ("IN PLAY" if passed and held else
                        "FAILED HOLDOUT" if passed else
                        "NOT ABOVE CHANCE" if s.get("n", 0) >= N_SEL else "TOO FEW CALLS")

    upcoming = project(cal, close, majors, minors, lon_days, lon, rows, today) if not null else []
    in_play = [r for r in rows if r["verdict"] == "IN PLAY"]
    tested = sum(1 for r in rows if r["sel"].get("n", 0) >= N_SEL)
    return {
        "history": {"from": str(sessions[0]), "to": str(sessions[-1]), "sessions": n},
        "swingThresholdPct": thresh, "majorThresholdPct": round(thresh * MAJOR_MULT, 1),
        "turns": len(minors), "majorTurns": len(majors),
        "split": str(sessions[split]) if split < n else None,
        "tested": tested, "inPlay": len(in_play),
        "tools": sorted(rows, key=lambda r: (r["verdict"] != "IN PLAY",
                                             -(r["sel"].get("lift") or 0))),
        "upcoming": upcoming}


def project(cal, close, majors, minors, lon_days, lon, rows, today):
    """Next dates from IN PLAY time tools, from the latest confirmed swings."""
    live = {r["tool"] for r in rows if r["verdict"] == "IN PLAY"}
    if not live:
        return []
    horizon = future_sessions(cal.last, 45)
    hset = set(horizon)
    fut = {}
    ext = list(cal.s) + horizon
    ext_cal = Calendar(ext)
    tt = time_tools(ext_cal, np.concatenate([close, np.full(len(horizon), close[-1])]),
                    majors[-8:], minors[-3:], lon_days, lon)
    for name, (fam, calls) in tt.items():
        if name not in live:
            continue
        for issue, d in calls:
            if d is None:
                continue
            j = ext_cal.session(d)
            if j is not None and j >= len(cal.s) and ext[j] in hset:
                fut.setdefault(str(ext[j]), set()).add(name)
    return [{"date": d, "tools": sorted(t), "count": len(t)}
            for d, t in sorted(fut.items())]


def shuffled(df, seed, block=20):
    """Same dates and volatility, daily moves reshuffled in blocks."""
    rng = np.random.default_rng(seed)
    r = np.diff(np.log(df["Close"].to_numpy(float)))
    blocks = [r[i:i + block] for i in range(0, len(r), block)]
    order = rng.permutation(len(blocks))
    rr = np.concatenate([blocks[k] for k in order])
    close = df["Close"].iloc[0] * np.exp(np.concatenate([[0], np.cumsum(rr)]))
    out = df.copy()
    out["Close"] = close
    return out


# ------------------------------------------------------------------ main
def main():
    today = date.today()
    if "--force" not in sys.argv and os.path.exists(OUT):
        try:
            prev = json.load(open(OUT, encoding="utf-8"))
            age = (today - datetime.strptime(prev["computed"], "%Y-%m-%d").date()).days
            if age < MAX_AGE_DAYS and prev.get("tickers"):
                print(f"{OUT} is {age}d old (<{MAX_AGE_DAYS}) - keeping it")
                return
        except Exception:
            pass
    tickers = [t.strip().upper() for t in open("tickers.txt") if t.strip()]
    try:
        thresh = {k: v["thresholdPct"] for k, v in
                  json.load(open("backfill.json", encoding="utf-8"))["perTicker"].items()}
    except Exception:
        thresh = {}
    frames = {}
    for t in tickers:
        fn = f"{t}_daily.csv"
        if os.path.exists(fn):
            df = pd.read_csv(fn, index_col=0)
            df.index = pd.to_datetime(df.index, utc=True, format="mixed").tz_convert("America/New_York")
            df = df[~df.index.normalize().duplicated(keep="last")]
            if len(df) >= 500:
                frames[t] = df
    if not frames:
        print("no daily history available; keeping previous lab")
        return
    start = min(df.index[0].date() for df in frames.values()) - timedelta(days=5)
    end = today + timedelta(days=1000)
    print(f"ephemeris {start} .. {end}")
    eph = ephemeris(start, end, PLANETS)
    result = {"computed": today.strftime("%Y-%m-%d"), "window": WINDOW, "split": SPLIT,
              "fdrQ": FDR_Q, "liftBar": LIFT_BAR, "draws": DRAWS,
              "method": __doc__.strip().split("\n\n")[0], "tickers": {}}
    for t, df in frames.items():
        th = thresh.get(t, 6.0)
        res = analyze_ticker(df, th, today, eph)
        # luck baseline: the identical pipeline on this stock's own daily
        # moves reshuffled in 20-day blocks (same volatility, no real cycles)
        nulls = [analyze_ticker(shuffled(df, seed), th, today, eph, seed=seed, null=True)["inPlay"]
                 for seed in (11, 12, 13)]
        res["nullInPlay"] = nulls
        result["tickers"][t] = res
        print(f"{t}: {res['history']['from']}..{res['history']['to']} tested {res['tested']}, "
              f"in play {res['inPlay']} (reshuffled history: {nulls})")
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=1, default=str)
    print(f"{OUT} written")


if __name__ == "__main__":
    main()
