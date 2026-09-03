"""Astro correlation lab: test EVERY astrological factor family against each
stock's own turn history, keep only what beats chance, and say so honestly.

Method: for each factor, collect its exact event dates over the price history,
ask how often a swing turn (high / low / either) landed within +-2 sessions,
and compare against the binomial chance of that many hits from random dates.
Benjamini-Hochberg FDR (q=0.10) per ticker+type controls the false-discovery
flood that testing ~770 factors otherwise guarantees. Survivors must also show
lift >= 1.30 with n >= 10 events.

Validated factors feed analyze.py's confluence scoring (weight ~ lift) and
their upcoming dates are published. Overrides: when a validated high-factor
and low-factor collide within 1 session, history decides which side wins.

Output: astro_lab.json. Recomputed at most every 7 days (CI stays fast).
"""
import json
import math
import os
import sys
from datetime import datetime, timedelta, date

import numpy as np
import pandas as pd
import ephem

OUT = "astro_lab.json"
MAX_AGE_DAYS = 7
WINDOW = 2          # sessions around an event that count as a hit
LIFT_BAR = 1.30
N_BAR = 10
FDR_Q = 0.10

# refresh only when stale, so hourly cloud runs don't pay the compute
if "--force" not in sys.argv and os.path.exists(OUT):
    try:
        with open(OUT, encoding="utf-8") as f:
            prev = json.load(f)
        age = (date.today() - datetime.strptime(prev["computed"], "%Y-%m-%d").date()).days
        if age < MAX_AGE_DAYS and prev.get("perTicker"):
            print(f"astro_lab.json is {age}d old (<{MAX_AGE_DAYS}) - keeping it")
            sys.exit(0)
    except Exception:
        pass

with open("tickers.txt") as f:
    TICKERS = [t.strip().upper() for t in f if t.strip()]
try:
    THRESH = {k: v["thresholdPct"] for k, v in
              json.load(open("backfill.json", encoding="utf-8"))["perTicker"].items()}
except Exception:
    THRESH = {}

FIRST_TRADE = {  # each stock's "natal" date (first public trading day)
    "TSLA": "2010-06-29", "HOOD": "2021-07-29", "QQQ": "1999-03-10",
    "JPM": "2001-01-02", "GOOGL": "2004-08-19", "NVDA": "1999-01-22",
    "AMZN": "1997-05-15", "SPY": "1993-01-29", "VOO": "2010-09-07"}

GEO = ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn",
       "Uranus", "Neptune", "Pluto"]
HELIO = ["Mercury", "Venus", "Mars", "Jupiter", "Saturn", "Uranus",
         "Neptune", "Pluto"]
ANGLES = [0, 30, 45, 60, 72, 90, 120, 135, 144, 150, 180]
SIGNS = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra",
         "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
OOB_DEC = 23.436

# ---------------------------------------------------------------- ephemeris
def build_ephemeris(d0, d1):
    days = pd.date_range(d0, d1, freq="D")
    lon = {b: np.empty(len(days)) for b in GEO}
    dec = {b: np.empty(len(days)) for b in GEO}
    hlon = {b: np.empty(len(days)) for b in HELIO}
    dist_moon = np.empty(len(days))
    for i, dt in enumerate(days):
        ds = dt.strftime("%Y/%m/%d")
        for b in GEO:
            body = getattr(ephem, b)()
            body.compute(ds)
            lon[b][i] = math.degrees(float(ephem.Ecliptic(body).lon))
            dec[b][i] = math.degrees(float(body.dec))
            if b == "Moon":
                dist_moon[i] = float(body.earth_distance)
            if b in HELIO:
                hlon[b][i] = math.degrees(float(body.hlon))
    return days, lon, dec, hlon, dist_moon


def wrap180(x):
    return (x + 180.0) % 360.0 - 180.0


def crossings(series, target):
    """dates (indices) where series crosses target between consecutive days"""
    f = series - target
    s = np.sign(f)
    idx = np.where((s[:-1] * s[1:]) < 0)[0]
    return idx + (np.abs(f[idx + 1]) < np.abs(f[idx]))  # nearer day


def local_extreme_idx(series, mode, width=3, gate=None):
    out = []
    for i in range(width, len(series) - width):
        w = series[i - width:i + width + 1]
        if mode == "min" and series[i] == w.min() and (gate is None or series[i] < gate):
            out.append(i)
        if mode == "max" and series[i] == w.max() and (gate is None or series[i] > gate):
            out.append(i)
    return np.array(out, dtype=int)


def factor_events(days, lon, dec, hlon, dist_moon):
    """{factor_name: [date, ...]} across every family we can compute."""
    ev = {}
    dl = days.date

    def add(name, idxs):
        if len(idxs):
            ev.setdefault(name, []).extend(dl[i] for i in np.asarray(idxs, dtype=int))

    # A/B. aspects, geocentric and heliocentric
    def aspects(lons, names, prefix, angles):
        for i in range(len(names)):
            for j in range(i + 1, len(names)):
                sep = np.abs(wrap180(lons[names[i]] - lons[names[j]]))
                for A in angles:
                    nm = f"{prefix} {names[i]}-{names[j]} {A}"
                    if A == 0:
                        add(nm, local_extreme_idx(sep, "min", 2, gate=3.0))
                    elif A == 180:
                        add(nm, local_extreme_idx(sep, "max", 2, gate=177.0))
                    else:
                        add(nm, crossings(sep, float(A)))
    aspects(lon, GEO, "geo", ANGLES)
    aspects(hlon, HELIO, "helio", [0, 60, 72, 90, 120, 144, 180])

    # C. stations: geocentric longitude reverses direction
    for b in ["Mercury", "Venus", "Mars", "Jupiter", "Saturn"]:
        v = wrap180(np.diff(lon[b]))
        s = np.sign(v)
        add(f"{b} station", np.where(s[:-1] * s[1:] < 0)[0] + 1)

    # D. solar ingresses (equinoxes/solstices included at 0/90/180/270)
    for k, sign in enumerate(SIGNS):
        f = wrap180(lon["Sun"] - k * 30.0)
        add(f"Sun ingress {sign}", crossings(f, 0.0))

    # E. lunar apogee / perigee
    add("Moon apogee", local_extreme_idx(dist_moon, "max", 5))
    add("Moon perigee", local_extreme_idx(dist_moon, "min", 5))

    # F. lunar declination extremes and zero-crossings
    add("Moon max declination", local_extreme_idx(dec["Moon"], "max", 5))
    add("Moon min declination", local_extreme_idx(dec["Moon"], "min", 5))
    add("Moon declination zero", crossings(dec["Moon"], 0.0))

    # G. out-of-bounds entries (|declination| exceeds the solar maximum)
    for b in ["Moon", "Mercury", "Venus", "Mars"]:
        a = np.abs(dec[b])
        s = np.sign(a - OOB_DEC)
        add(f"{b} out-of-bounds", np.where((s[:-1] < 0) & (s[1:] > 0))[0] + 1)

    # H. declination parallels / contraparallels (personal + social planets)
    P6 = ["Sun", "Mercury", "Venus", "Mars", "Jupiter", "Saturn"]
    for i in range(len(P6)):
        for j in range(i + 1, len(P6)):
            add(f"decl parallel {P6[i]}-{P6[j]}",
                crossings(dec[P6[i]] - dec[P6[j]], 0.0))
            add(f"decl contraparallel {P6[i]}-{P6[j]}",
                crossings(dec[P6[i]] + dec[P6[j]], 0.0))

    # I. Bradley siderograph turning dates
    MID = ["Sun", "Venus", "Mars", "Jupiter", "Saturn", "Uranus", "Neptune", "Pluto"]
    VAL = {0: 1.0, 60: 1.0, 120: 1.0, 90: -1.0, 180: -1.0}
    idx_b = np.zeros(len(days))
    for i in range(len(MID)):
        for j in range(i + 1, len(MID)):
            sep = np.abs(wrap180(lon[MID[i]] - lon[MID[j]]))
            for A, v in VAL.items():
                d = np.abs(sep - A)
                idx_b += v * np.clip(1.0 - d / 6.0, 0.0, 1.0)
    k = np.ones(5) / 5
    smooth = np.convolve(idx_b, k, mode="same")
    add("Bradley turn", np.concatenate([local_extreme_idx(smooth, "max", 5),
                                        local_extreme_idx(smooth, "min", 5)]))
    return ev


# ------------------------------------------------------------------ turns
def zigzag_turns(close, thresh_pct):
    th = thresh_pct / 100.0
    piv = []
    last_i, last_p, direction = 0, close[0], 0
    ext_i, ext_p = 0, close[0]
    for i in range(1, len(close)):
        p = close[i]
        if direction >= 0:
            if p > ext_p:
                ext_i, ext_p = i, p
            if p < ext_p * (1 - th):
                piv.append((ext_i, "high")); direction = -1; ext_i, ext_p = i, p
        if direction <= 0:
            if p < ext_p:
                ext_i, ext_p = i, p
            if p > ext_p * (1 + th):
                piv.append((ext_i, "low")); direction = 1; ext_i, ext_p = i, p
    return piv


def binom_sf(k, n, p):
    """P(X >= k) for X~Bin(n,p) via log terms (no scipy in CI)."""
    if k <= 0:
        return 1.0
    total = 0.0
    for x in range(k, n + 1):
        lg = (math.lgamma(n + 1) - math.lgamma(x + 1) - math.lgamma(n - x + 1)
              + x * math.log(max(p, 1e-12)) + (n - x) * math.log(max(1 - p, 1e-12)))
        total += math.exp(lg)
    return min(1.0, total)


# --------------------------------------------------------------------- main
today = date.today()
print("building ephemeris (5y history + 70d forward)...")
E_START = today - timedelta(days=5 * 365 + 30)
E_END = today + timedelta(days=70)
days, lon, dec, hlon, dist_moon = build_ephemeris(E_START, E_END)
base_events = factor_events(days, lon, dec, hlon, dist_moon)
print(f"  {len(base_events)} factors, "
      f"{sum(len(v) for v in base_events.values())} raw event dates")

result = {"computed": today.strftime("%Y-%m-%d"), "window": WINDOW,
          "liftBar": LIFT_BAR, "nBar": N_BAR, "fdrQ": FDR_Q, "perTicker": {}}

for tkr in TICKERS:
    fn = f"{tkr}_daily.csv"
    if not os.path.exists(fn):
        continue
    df = pd.read_csv(fn, index_col=0)
    df.index = pd.to_datetime(df.index, utc=True, format="mixed")
    df = df[df.index >= pd.Timestamp(E_START, tz="UTC")]
    if len(df) < 300:
        continue
    sessions = [d.date() for d in df.index]
    sidx = {d: i for i, d in enumerate(sessions)}
    close = df["Close"].to_numpy(float)

    piv = zigzag_turns(close, THRESH.get(tkr, 6.0))
    near = {"high": np.zeros(len(sessions), bool),
            "low": np.zeros(len(sessions), bool)}
    for i, ty in piv:
        near[ty][max(0, i - WINDOW):i + WINDOW + 1] = True
    near["any"] = near["high"] | near["low"]

    # per-ticker extras: natal transits + pivot anniversaries
    ev = {k: list(v) for k, v in base_events.items()}
    natal = FIRST_TRADE.get(tkr)
    if natal:
        b = ephem.Sun(); b.compute(natal.replace("-", "/"))
        natal_sun = math.degrees(float(ephem.Ecliptic(b).lon))
        for tb in ["Sun", "Mars", "Jupiter", "Saturn", "Uranus", "Pluto"]:
            sep = np.abs(wrap180(lon[tb] - natal_sun))
            for A in (0, 90, 180):
                nm = f"natal {tb} {A} first-trade Sun"
                if A == 0:
                    ii = local_extreme_idx(sep, "min", 2, gate=3.0)
                elif A == 180:
                    ii = local_extreme_idx(sep, "max", 2, gate=177.0)
                else:
                    ii = crossings(sep, float(A))
                if len(ii):
                    ev.setdefault(nm, []).extend(days.date[i] for i in ii)
    prom = sorted(piv, key=lambda x: -abs(close[x[0]] / np.mean(close) - 1))[:6]
    for i, ty in prom:
        md = sessions[i]
        nm = f"anniversary {ty} {md.strftime('%m/%d')}"
        ev.setdefault(nm, []).extend(
            date(y, md.month, min(md.day, 28)) for y in
            range(sessions[0].year, today.year + 2) if date(y, md.month, min(md.day, 28)) != md)

    def to_session(d0):
        for k in range(4):
            d2 = d0 + timedelta(days=k)
            if d2 in sidx:
                return sidx[d2]
        return None

    split = int(len(sessions) * 0.6)   # train on the first 60%, replicate on the rest
    rows = []
    for name, dates in ev.items():
        hist = sorted(set(d for d in dates if sessions[0] <= d <= sessions[-1]))
        mapped = [to_session(d) for d in hist]
        mapped = [m for m in mapped if m is not None]
        if len(mapped) < N_BAR:
            continue
        for ty in ("high", "low", "any"):
            p0 = float(near[ty].mean())
            hits = int(sum(near[ty][m] for m in mapped))
            n = len(mapped)
            lift = (hits / n) / p0 if p0 > 0 else 0
            pv = binom_sf(hits, n, p0)
            # split-sample replication: the same factor judged independently
            # on data it was not mined from
            tr = [m for m in mapped if m < split]
            te = [m for m in mapped if m >= split]
            rep = None
            if len(tr) >= 6 and len(te) >= 4:
                p_tr = float(near[ty][:split].mean())
                p_te = float(near[ty][split:].mean())
                h_tr = int(sum(near[ty][m] for m in tr))
                h_te = int(sum(near[ty][m] for m in te))
                rep = {"trainP": round(binom_sf(h_tr, len(tr), p_tr), 4),
                       "testP": round(binom_sf(h_te, len(te), p_te), 4),
                       "trainLift": round((h_tr / len(tr)) / p_tr, 2) if p_tr else 0,
                       "testLift": round((h_te / len(te)) / p_te, 2) if p_te else 0,
                       "trainN": len(tr), "testN": len(te)}
            rows.append({"factor": name, "type": ty, "n": n, "hits": hits,
                         "hitPct": round(100 * hits / n, 1),
                         "chancePct": round(100 * p0, 1),
                         "lift": round(lift, 2), "p": round(pv, 5), "rep": rep})

    # Benjamini-Hochberg per type, then the practical bars
    validated = []
    for ty in ("high", "low", "any"):
        sub = sorted([r for r in rows if r["type"] == ty], key=lambda r: r["p"])
        m = len(sub)
        cut = 0
        for i, r in enumerate(sub, 1):
            if r["p"] <= FDR_Q * i / m:
                cut = i
        for r in sub[:cut]:
            if r["lift"] >= LIFT_BAR and r["n"] >= N_BAR:
                r2 = dict(r); r2["verdict"] = "VALIDATED"
                validated.append(r2)
    # REPLICATED tier: significant on the train half AND independently on the
    # test half it never saw. P(both by luck) ~ 0.02x0.10 = 0.002 per test -
    # expected false replications are reported, never hidden.
    for r in rows:
        rp = r.get("rep")
        if (rp and rp["trainP"] <= 0.02 and rp["testP"] <= 0.10
                and rp["trainLift"] >= LIFT_BAR and rp["testLift"] >= LIFT_BAR
                and not any(v["factor"] == r["factor"] and v["type"] == r["type"]
                            for v in validated)):
            r2 = dict(r); r2["verdict"] = "REPLICATED"
            validated.append(r2)

    # an 'any'-validated factor whose high/low split also validated is a dup;
    # prefer the directional finding
    dirn = {(r["factor"], r["type"]) for r in validated if r["type"] != "any"}
    dir_factors = {f for f, _ in dirn}
    validated = [r for r in validated if not (r["type"] == "any" and r["factor"] in dir_factors)]

    # overrides: validated high-factor vs low-factor within 1 session - who won?
    overrides = []
    vh = [r for r in validated if r["type"] == "high"]
    vl = [r for r in validated if r["type"] == "low"]
    for rh in vh:
        for rl in vl:
            hh = {to_session(d) for d in ev[rh["factor"]]
                  if sessions[0] <= d <= sessions[-1]} - {None}
            ll = {to_session(d) for d in ev[rl["factor"]]
                  if sessions[0] <= d <= sessions[-1]} - {None}
            clash = [a for a in hh for b in ll if abs(a - b) <= 1]
            if len(clash) >= 5:
                wins_h = sum(near["high"][c] for c in clash)
                wins_l = sum(near["low"][c] for c in clash)
                overrides.append({
                    "highFactor": rh["factor"], "lowFactor": rl["factor"],
                    "n": len(clash), "highWon": int(wins_h), "lowWon": int(wins_l),
                    "winner": ("high" if wins_h > wins_l else
                               "low" if wins_l > wins_h else "tie")})

    # upcoming events for validated factors (next 60 days)
    upcoming = []
    for r in validated:
        for d0 in ev[r["factor"]]:
            if today < d0 <= today + timedelta(days=60):
                upcoming.append({"date": d0.strftime("%Y-%m-%d"),
                                 "factor": r["factor"], "type": r["type"],
                                 "lift": r["lift"], "hitPct": r["hitPct"],
                                 "chancePct": r["chancePct"]})
    upcoming.sort(key=lambda x: x["date"])

    tested = len(rows)
    # near-misses: the strongest raw signals even when nothing survives FDR -
    # shown so "0 validated" is visibly a verdict, not a silence
    cands = sorted(rows, key=lambda r: r["p"])[:10]
    result["perTicker"][tkr] = {
        "tested": tested, "turns": len(piv),
        "expectedFalse": round(0.002 * tested / 3, 1),  # per replication tier
        "validated": sorted(validated, key=lambda r: -r["lift"])[:40],
        "candidates": cands,
        "overrides": overrides[:20], "upcoming": upcoming[:40]}
    print(f"{tkr}: tested {tested} factor-type combos, "
          f"{len(validated)} validated, {len(upcoming)} upcoming events")

with open(OUT, "w", encoding="utf-8") as f:
    json.dump(result, f, indent=1)
print("astro_lab.json written")
