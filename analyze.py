"""Analyze timing patterns for every ticker in tickers.txt.

For each stock: swing rhythm, intraday/weekday/monthly timing distributions,
strategy backtests, Gann/Hurst/astro/Fibonacci methods (each tested against
random controls), and a multi-method confluence forecast of the next 5
highs/lows. Writes data.js for the dashboard.
"""
import json
import time
import bisect
import math
import string
import pandas as pd
import numpy as np
import ephem
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

ET = ZoneInfo("America/New_York")
NOW = datetime.now(ET)

# rolling log of every prediction ever made, so each run can grade the old
# ones against what actually happened and re-weight the methods accordingly
LOG_FILE = "predictions_log.json"
try:
    with open(LOG_FILE, encoding="utf-8") as _f:
        PRED_LOG = json.load(_f)
except Exception:
    PRED_LOG = {"entries": []}

# permanent record of every day's high/low/close per ticker (committed to the
# repo, so accuracy analysis never depends on refetching history)
EXT_FILE = "daily_extremes.json"
try:
    with open(EXT_FILE, encoding="utf-8") as _f:
        EXTREMES = json.load(_f)
except Exception:
    EXTREMES = {}


def method_family(tag):
    t = tag.lower()
    if t.startswith("rhythm"):
        return "rhythm"
    if t.startswith("gann"):
        return "gann"
    if t.startswith("fib"):
        return "fib"
    if t.startswith("hurst"):
        return "hurst"
    if t.startswith("sepharial"):
        return "sepharial"
    if t.startswith("vibe") or t.startswith("numerology"):
        return "vibration"
    if "moon" in t:
        return "moon"
    return "other"

with open("tickers.txt") as f:
    TICKERS = [t.strip().upper() for t in f if t.strip()]

WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
GANN = [30, 45, 60, 90, 120, 144, 180, 270, 360]
GANN_CTRL = [37, 52, 68, 97, 127, 151, 187, 277, 367]
FIB = [8, 13, 21, 34, 55, 89, 144]
FIB_CTRL = [10, 16, 25, 40, 62, 97, 152]


def add_trading_days(start_date, n):
    d, step = start_date, 1 if n >= 0 else -1
    added = 0
    while added < abs(n):
        d += timedelta(days=step)
        if d.weekday() < 5:
            added += 1
    return d


def fmt_time(hhmm):
    # cross-platform 12-hour format (no %#I / %-I)
    return datetime.strptime(hhmm, "%H:%M").strftime("%I:%M %p").lstrip("0")


def dist(items):
    s = pd.Series(items).value_counts(normalize=True).sort_index()
    return {k: round(v * 100, 1) for k, v in s.items()}


def btstats(r):
    r = pd.Series(r).dropna()
    if r.empty:
        return None
    return {"avgPct": round(float(r.mean()) * 100, 3),
            "winRate": round(float((r > 0).mean()) * 100, 1),
            "totalPct": round((float((1 + r).prod()) - 1) * 100, 0),
            "n": int(len(r))}


def zigzag(df, threshold):
    closes = df["Close"].values
    dates = df.index
    pivots, direction, ext_i = [], 0, 0
    for i in range(1, len(closes)):
        c = closes[i]
        if direction >= 0:
            if c > closes[ext_i]:
                ext_i = i
            elif c < closes[ext_i] * (1 - threshold):
                pivots.append({"i": ext_i, "date": dates[ext_i], "type": "high",
                               "price": float(closes[ext_i])})
                direction, ext_i = -1, i
        if direction <= 0:
            if c < closes[ext_i]:
                ext_i = i
            elif c > closes[ext_i] * (1 + threshold):
                pivots.append({"i": ext_i, "date": dates[ext_i], "type": "low",
                               "price": float(closes[ext_i])})
                direction, ext_i = 1, i
    return pivots, direction, ext_i


# ---------------- astro series (computed once, shared by all tickers) ----------------
def moon_events(start, end):
    ev = []
    d = ephem.Date(start)
    while True:
        nm, fm = ephem.next_new_moon(d), ephem.next_full_moon(d)
        nxt, kind = (nm, "new") if nm < fm else (fm, "full")
        dt = ephem.to_timezone(nxt, ET)
        if dt.date() > end:
            break
        ev.append({"date": dt.date(), "time": dt.strftime("%I:%M %p ET").lstrip("0"), "kind": kind})
        d = ephem.Date(nxt + 1)
    return ev


MOONS_HIST = moon_events(datetime(2021, 7, 1), NOW.date())
MOONS_NEXT = moon_events(NOW, NOW.date() + timedelta(days=62))

_rdays, _rflags, _prev = [], [], None
_d = datetime(2021, 7, 1)
_end = datetime.now() + timedelta(days=62)
while _d <= _end:
    lon = float(ephem.Ecliptic(ephem.Mercury(ephem.Date(_d))).lon)
    if _prev is not None:
        diff = (lon - _prev + np.pi) % (2 * np.pi) - np.pi
        _rflags.append(diff < 0)
        _rdays.append(_d)
    _prev = lon
    _d += timedelta(days=1)
RETRO_SET = {d.date() for d, f in zip(_rdays, _rflags) if f}
RETRO_SHARE = len([d for d in _rdays if d.date() <= NOW.date() and d.date() in RETRO_SET]) / \
              len([d for d in _rdays if d.date() <= NOW.date()])
_upcoming = sorted({d for d in RETRO_SET if NOW.date() < d <= NOW.date() + timedelta(days=60)})
RETRO_RANGES = []
for d in _upcoming:
    if RETRO_RANGES and (d - RETRO_RANGES[-1][1]).days == 1:
        RETRO_RANGES[-1][1] = d
    else:
        RETRO_RANGES.append([d, d])

# ============================================================ VIBRATION LAB
# Daily geocentric longitudes for all 10 bodies, every planet-pair aspect
# series, and retrograde flags — mined per stock to find ITS OWN recurring
# astro signature at highs/lows, with an honest chance-calibration control.
BODY_FNS = [("Sun", ephem.Sun), ("Moon", ephem.Moon), ("Mercury", ephem.Mercury),
            ("Venus", ephem.Venus), ("Mars", ephem.Mars), ("Jupiter", ephem.Jupiter),
            ("Saturn", ephem.Saturn), ("Uranus", ephem.Uranus),
            ("Neptune", ephem.Neptune), ("Pluto", ephem.Pluto)]
VDAYS = []
_lon = {n: [] for n, _ in BODY_FNS}
_d = datetime(2021, 7, 1)
_vend = datetime.now() + timedelta(days=62)
while _d <= _vend:
    ed = ephem.Date(_d)
    for n, fn in BODY_FNS:
        _lon[n].append(math.degrees(float(ephem.Ecliptic(fn(ed)).lon)))
    VDAYS.append(_d.date())
    _d += timedelta(days=1)
LON = {n: np.array(v) for n, v in _lon.items()}
VIDX = {d: i for i, d in enumerate(VDAYS)}
HIST_END = VIDX.get(NOW.date(), len(VDAYS) - 63)

PRETRO = {}
for n, _ in BODY_FNS:
    if n in ("Sun", "Moon"):
        continue
    dl = (np.diff(LON[n]) + 180) % 360 - 180
    PRETRO[n] = np.concatenate([[False], dl < 0])

def _ang(a, b):
    return np.abs(((a - b + 180) % 360) - 180)


def _sm1(hit, k=1):
    sm = hit.copy()
    for s in range(1, k + 1):
        sm[s:] = sm[s:] | hit[:-s]
        sm[:-s] = sm[:-s] | hit[s:]
    return sm


# mean lunar node (Rahu; Ketu is the opposite point)
_j2000 = datetime(2000, 1, 1, 12)
_dsj = np.array([(datetime.combine(d, datetime.min.time()) - _j2000).days
                 for d in VDAYS], dtype=float)
LON["Node"] = (125.0445479 - 0.0529538083 * _dsj) % 360

# heliocentric longitudes (Sun-centred view — classic financial-astro variant)
HELIO_BODIES = ["Mercury", "Venus", "Mars", "Jupiter", "Saturn",
                "Uranus", "Neptune", "Pluto"]
_hlon = {n: [] for n in HELIO_BODIES}
_d = datetime(2021, 7, 1)
while _d <= _vend:
    ed = ephem.Date(_d)
    for n in HELIO_BODIES:
        b = getattr(ephem, n)(ed)
        _hlon[n].append(math.degrees(float(b.hlon)))
    _d += timedelta(days=1)
HLON = {n: np.array(v) for n, v in _hlon.items()}

MAJOR_ANGLES = [(0, "conjunct"), (60, "sextile"), (90, "square"),
                (120, "trine"), (180, "opposite")]
MINOR_ANGLES = [(30, "semi-sextile"), (45, "semi-square"), (72, "quintile"),
                (135, "sesquiquadrate"), (144, "biquintile"), (150, "quincunx")]

ASPECT_SERIES = []          # (label, smeared day-flag array)


def _add_series(label, hit, smear=1):
    sm = _sm1(hit, smear)
    base = sm[:HIST_END].mean()
    if 0.003 < base < 0.55:
        ASPECT_SERIES.append((label, sm))


def _pair_aspects(lon_map, names, angles, prefix="", orb_default=1.5,
                  orb_minor=1.0, moon_orb=3.0, moon_orb_minor=2.0):
    minor_set = {a for a, _ in MINOR_ANGLES}
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            a, b = names[i], names[j]
            diff = lon_map[a] - lon_map[b]
            for ang, albl in angles:
                if "Moon" in (a, b):
                    orb = moon_orb_minor if ang in minor_set else moon_orb
                else:
                    orb = orb_minor if ang in minor_set else orb_default
                hit = _ang(diff, ang) <= orb
                if ang not in (0, 180):
                    hit = hit | (_ang(diff, -ang) <= orb)
                _add_series(f"{prefix}{a} {albl} {b}", hit)


# geocentric: 11 points (10 bodies + Node), majors + minors
_geo_names = [n for n, _ in BODY_FNS] + ["Node"]
_pair_aspects(LON, _geo_names, MAJOR_ANGLES + MINOR_ANGLES)
# heliocentric: 8 planets, major aspects
_pair_aspects(HLON, HELIO_BODIES, MAJOR_ANGLES, prefix="Helio ")

# eclipse days: new/full moon while the Sun is near the lunar node
_newfull = (_ang(LON["Sun"] - LON["Moon"], 0) <= 7) | (_ang(LON["Sun"] - LON["Moon"], 180) <= 7)
_sun_node = (_ang(LON["Sun"], LON["Node"]) <= 15) | (_ang(LON["Sun"], (LON["Node"] + 180) % 360) <= 15)
_add_series("Eclipse (new/full moon near node)", _newfull & _sun_node)

# real-world calendar forces, mined with the same honesty machinery
_opex = np.zeros(len(VDAYS), dtype=bool)
_tom = np.zeros(len(VDAYS), dtype=bool)
_bym = {}
for _i2, _dv in enumerate(VDAYS):
    _bym.setdefault((_dv.year, _dv.month), []).append(_i2)
for _idx_list in _bym.values():
    fridays = [i for i in _idx_list if VDAYS[i].weekday() == 4]
    if len(fridays) >= 3:
        _opex[fridays[2]] = True
    wk = [i for i in _idx_list if VDAYS[i].weekday() < 5]
    for i in wk[-2:] + wk[:3]:
        _tom[i] = True
_add_series("Options expiration (3rd Friday)", _opex)
_add_series("Turn of month (last 2 + first 3 trading days)", _tom, smear=0)

_FOMC = ["2021-07-28", "2021-09-22", "2021-11-03", "2021-12-15",
         "2022-01-26", "2022-03-16", "2022-05-04", "2022-06-15", "2022-07-27",
         "2022-09-21", "2022-11-02", "2022-12-14",
         "2023-02-01", "2023-03-22", "2023-05-03", "2023-06-14", "2023-07-26",
         "2023-09-20", "2023-11-01", "2023-12-13",
         "2024-01-31", "2024-03-20", "2024-05-01", "2024-06-12", "2024-07-31",
         "2024-09-18", "2024-11-07", "2024-12-18",
         "2025-01-29", "2025-03-19", "2025-05-07", "2025-06-18", "2025-07-30",
         "2025-09-17", "2025-10-29", "2025-12-10",
         "2026-01-28", "2026-03-18", "2026-04-29", "2026-06-17", "2026-07-29",
         "2026-09-16", "2026-10-28", "2026-12-09"]
_fomc = np.zeros(len(VDAYS), dtype=bool)
for _ds in _FOMC:
    _fd = datetime.strptime(_ds, "%Y-%m-%d").date()
    if _fd in VIDX:
        _fomc[VIDX[_fd]] = True
_add_series("FOMC decision day", _fomc)

# Ebertin midpoints: planet C sitting on the A/B midpoint axis
# (8th-harmonic angles 0/45/90/135/180, tight 1° orb — Ebertin's method)
_bodies10 = [n for n, _ in BODY_FNS]
for _i in range(len(_bodies10)):
    for _j in range(_i + 1, len(_bodies10)):
        a, b = _bodies10[_i], _bodies10[_j]
        mid = (LON[a] + ((LON[b] - LON[a]) % 360) / 2) % 360
        for c in _bodies10:
            if c in (a, b):
                continue
            orb = 2.0 if "Moon" in (a, b, c) else 1.0
            hit = np.zeros(len(VDAYS), dtype=bool)
            for th in (0, 45, 90, 135, 180):
                hit |= _ang(LON[c] - mid, th) <= orb
            _add_series(f"{c} = {a}/{b} midpoint", hit)

# higher harmonics (7th/9th/11th/13th — Addey/Ebertin school)
for _H in (7, 9, 11, 13):
    for _i in range(len(_bodies10)):
        for _j in range(_i + 1, len(_bodies10)):
            a, b = _bodies10[_i], _bodies10[_j]
            orb = 2.0 if "Moon" in (a, b) else 1.0
            hit = _ang((LON[a] - LON[b]) * _H, 0) <= _H * orb
            _add_series(f"{a} {_H}th-harmonic {b}", hit)

SM_G = np.array([s for _, s in ASPECT_SERIES])
BASES_G = SM_G[:, :HIST_END].mean(axis=1)

PY_NUM = {c: (ord(c) - 65) % 9 + 1 for c in string.ascii_uppercase}

# ---------------- Sepharial module ----------------
# Chaldean name-numbers -> ruling planet (Sepharial's "Kabala of Numbers"),
# planetary station days (his prime signal days), Moon declination cycle.
CHALDEAN = {"A": 1, "B": 2, "C": 3, "D": 4, "E": 5, "F": 8, "G": 3, "H": 5,
            "I": 1, "J": 1, "K": 2, "L": 3, "M": 4, "N": 5, "O": 7, "P": 8,
            "Q": 1, "R": 2, "S": 3, "T": 4, "U": 6, "V": 6, "W": 6, "X": 5,
            "Y": 1, "Z": 7}
CH_PLANET = {1: "Sun", 2: "Moon", 3: "Jupiter", 4: "Uranus", 5: "Mercury",
             6: "Venus", 7: "Neptune", 8: "Saturn", 9: "Mars"}

def _smear(flags, k):
    sm = flags.copy()
    for s in range(1, k + 1):
        sm[s:] = sm[s:] | flags[:-s]
        sm[:-s] = sm[:-s] | flags[s:]
    return sm

# station days: the flip between direct and retrograde motion, +/-2 days
STATION = {}
for _n, _arr in PRETRO.items():
    fl = np.zeros(len(_arr), dtype=bool)
    fl[1:] = _arr[1:] != _arr[:-1]
    STATION[_n] = _smear(fl, 2)
STATION_ANY = np.zeros(len(VDAYS), dtype=bool)
for _s in STATION.values():
    STATION_ANY |= _s

# Moon declination series -> extremes (max N / max S) and equator crossings
_mdec = []
_d = datetime(2021, 7, 1)
while _d <= _vend:
    _mdec.append(math.degrees(float(ephem.Moon(ephem.Date(_d)).dec)))
    _d += timedelta(days=1)
MOON_DEC = np.array(_mdec)
_dd = np.diff(MOON_DEC)
_ext = np.zeros(len(MOON_DEC), dtype=bool)
_ext[1:-1] = (_dd[:-1] > 0) & (_dd[1:] <= 0) | (_dd[:-1] < 0) & (_dd[1:] >= 0)
MOON_DEC_EXT = _smear(_ext, 1)
_zc = np.zeros(len(MOON_DEC), dtype=bool)
_zc[1:] = np.sign(MOON_DEC[1:]) != np.sign(MOON_DEC[:-1])
MOON_DEC_ZERO = _smear(_zc, 1)


def sepharial_scan(tkr, pivots):
    """Sepharial's techniques tested against this stock's actual pivots."""
    all_idx = [VIDX[p["date"].date()] for p in pivots if p["date"].date() in VIDX]
    res = {"tests": []}
    bumps = []
    if not all_idx:
        return res, bumps
    ch = digital_root(sum(CHALDEAN.get(c, 0) for c in tkr if c.isalpha()))
    ruler = CH_PLANET[ch]
    res["chaldeanNumber"] = ch
    res["rulingPlanet"] = ruler

    def test(name, mask, which="B", w=0.3):
        base = mask[:HIST_END].mean()
        if base <= 0 or base > 0.7:
            return
        rate = float(mask[all_idx].mean())
        hits = int(mask[all_idx].sum())
        lift = rate / base
        res["tests"].append({"name": name, "lift": round(lift, 2), "hits": hits,
                             "n": len(all_idx), "basePct": round(base * 100, 1)})
        if lift >= 1.3 and hits >= 4:
            bumps.append(("Sepharial: " + name, mask, which, w))

    # 1) days the ruling planet makes any exact aspect
    ruler_mask = np.zeros(len(VDAYS), dtype=bool)
    for lbl, sm in ASPECT_SERIES:
        parts = lbl.split()
        if parts[0] == ruler or parts[-1] == ruler:
            ruler_mask |= sm
    test(f"ruling planet {ruler} in exact aspect", ruler_mask)
    # 2) ruling planet station days (Sun/Moon never station)
    if ruler in STATION:
        test(f"{ruler} station (turning retro/direct)", STATION[ruler], w=0.4)
    # 3) any planet stationing
    test("any planet station day", STATION_ANY)
    # 4) Moon at declination extreme (max north/south)
    test("Moon declination extreme", MOON_DEC_EXT)
    # 5) Moon crossing the equator (0 declination)
    test("Moon crossing equator", MOON_DEC_ZERO)
    return res, bumps


def digital_root(x):
    return 1 + (x - 1) % 9 if x > 0 else 0


# ---------------- planetary hours (classical, computed for New York) ----------------
PH_ORDER = ["Saturn", "Jupiter", "Mars", "Sun", "Venus", "Mercury", "Moon"]
PH_DAYRULER = {0: "Moon", 1: "Mars", 2: "Mercury", 3: "Jupiter",
               4: "Venus", 5: "Saturn", 6: "Sun"}          # Monday=0
_ph_cache = {}


def planetary_hours(d):
    """24 unequal planetary hours (day + night) for date d, ET datetimes."""
    if d in _ph_cache:
        return _ph_cache[d]
    obs = ephem.Observer()
    obs.lat, obs.lon = "40.7128", "-74.0060"
    start = ephem.Date(datetime(d.year, d.month, d.day, 8, 0))   # ~3-4 AM ET in UTC
    sun = ephem.Sun()
    sr = obs.next_rising(sun, start=start)
    ss = obs.next_setting(sun, start=sr)
    sr2 = obs.next_rising(sun, start=ss)
    i0 = PH_ORDER.index(PH_DAYRULER[d.weekday()])
    hours = []
    dl, nl = (ss - sr) / 12, (sr2 - ss) / 12
    for k in range(12):
        hours.append((ephem.to_timezone(ephem.Date(sr + k * dl), ET),
                      ephem.to_timezone(ephem.Date(sr + (k + 1) * dl), ET),
                      PH_ORDER[(i0 + k) % 7]))
    for k in range(12):
        hours.append((ephem.to_timezone(ephem.Date(ss + k * nl), ET),
                      ephem.to_timezone(ephem.Date(ss + (k + 1) * nl), ET),
                      PH_ORDER[(i0 + 12 + k) % 7]))
    _ph_cache[d] = hours
    return hours


def ruler_at(hours, ts):
    for s, e, r in hours:
        if s <= ts < e:
            return r
    return None


def vibration_scan(tkr, pivots):
    """Mine this stock's pivots for its own astro/numerology signature."""
    out_v = {"high": [], "low": [], "retro": [], "numerology": {}, "chanceLift": None}
    upcoming_bumps = []      # (label, sm, which, weight)
    rng = np.random.default_rng(7)
    idx_by_type = {}
    for ptype in ("high", "low"):
        idx_by_type[ptype] = [VIDX[p["date"].date()] for p in pivots
                              if p["type"] == ptype and p["date"].date() in VIDX]
    # chance calibration: what max lift do random date-sets of this size show?
    n_ref = max(len(idx_by_type["high"]), len(idx_by_type["low"]), 5)
    maxlifts = []
    for _ in range(120):
        ridx = rng.choice(HIST_END, size=n_ref, replace=False)
        rates = SM_G[:, ridx].mean(axis=1)
        with np.errstate(divide="ignore", invalid="ignore"):
            lifts = np.where(BASES_G > 0, rates / BASES_G, 0)
        maxlifts.append(float(np.max(lifts)))
    out_v["chanceLift"] = round(float(np.median(maxlifts)), 2)

    for ptype in ("high", "low"):
        pidx = idx_by_type[ptype]
        if len(pidx) < 5:
            continue
        rows = []
        for k, (lbl, sm) in enumerate(ASPECT_SERIES):
            hits = int(sm[pidx].sum())
            if hits < 4:
                continue
            lift = (hits / len(pidx)) / BASES_G[k] if BASES_G[k] > 0 else 0
            if lift >= 1.5:
                rows.append({"aspect": lbl, "lift": round(float(lift), 2),
                             "hits": hits, "n": len(pidx),
                             "basePct": round(float(BASES_G[k]) * 100, 1), "k": k})
        rows.sort(key=lambda r: -(r["lift"] * math.log(r["hits"] + 1)))
        out_v[ptype] = [{kk: r[kk] for kk in ("aspect", "lift", "hits", "n", "basePct")}
                        for r in rows[:5]]
        for r in rows[:3]:
            w = min(0.6, 0.2 + 0.15 * (r["lift"] - 1.5))
            upcoming_bumps.append((r["aspect"], ASPECT_SERIES[r["k"]][1],
                                   "H" if ptype == "high" else "L", w))

    all_idx = idx_by_type["high"] + idx_by_type["low"]
    if all_idx:
        for n, arr in PRETRO.items():
            base = arr[:HIST_END].mean()
            if base < 0.02:
                continue
            rate = float(arr[all_idx].mean())
            lift = rate / base
            hits = int(arr[all_idx].sum())
            if lift >= 1.4 and hits >= 4:
                out_v["retro"].append({"planet": n, "lift": round(lift, 2),
                                       "hits": hits, "n": len(all_idx)})

    # numerology: ticker's Pythagorean root vs pivot-date roots
    troot = digital_root(sum(PY_NUM[ch] for ch in tkr if ch.isalpha()))
    droots = np.array([digital_root(sum(int(c) for c in d.strftime("%m%d%Y")))
                       for d in VDAYS])
    match = droots == troot
    base = match[:HIST_END].mean()
    rate = float(match[all_idx].mean()) if all_idx else 0
    nlift = rate / base if base > 0 else 0
    nhits = int(match[all_idx].sum()) if all_idx else 0
    out_v["numerology"] = {"tickerNumber": troot, "lift": round(nlift, 2),
                           "hits": nhits, "n": len(all_idx),
                           "basePct": round(base * 100, 1)}
    if nlift >= 1.3 and nhits >= 4:
        upcoming_bumps.append((f"Numerology day {troot}", match, "B", 0.25))
    return out_v, upcoming_bumps


# ================================================================ per-ticker
def analyze(tkr):
    daily = pd.read_csv(f"{tkr}_daily.csv", parse_dates=["Datetime"], index_col="Datetime")
    hourly = pd.read_csv(f"{tkr}_hourly.csv", parse_dates=["Datetime"], index_col="Datetime")
    m15 = pd.read_csv(f"{tkr}_15m.csv", parse_dates=["Datetime"], index_col="Datetime")
    for df in (daily, hourly, m15):
        df.index = pd.to_datetime(df.index, utc=True).tz_convert(ET)

    daily["date"] = daily.index.date
    last_close = float(daily["Close"].iloc[-1])
    last_bar_date = daily.index[-1].date()

    # use the latest pre/post-market trade as current price when fresher than
    # the last completed bar (early-morning runs must price overnight gaps)
    is_pm = False
    try:
        with open("premarket.json", encoding="utf-8") as f:
            _pm = json.load(f)
        if time.time() - _pm.get("asof", 0) < 6 * 3600 and tkr in _pm.get("prices", {}):
            _pmp = float(_pm["prices"][tkr])
            if _pmp > 0 and abs(_pmp / last_close - 1) > 0.001:
                last_close = _pmp
                is_pm = True
    except Exception:
        pass

    # append recent daily highs/lows to the permanent record (keep ~400 days)
    ex = EXTREMES.setdefault(tkr, {})
    for ts, row in daily.tail(90).iterrows():
        ex[ts.strftime("%Y-%m-%d")] = [round(float(row["High"]), 2),
                                       round(float(row["Low"]), 2),
                                       round(float(row["Close"]), 2)]
    for k in sorted(ex)[:-400]:
        del ex[k]
    out = {"ticker": tkr,
           "generated": NOW.strftime("%Y-%m-%d %I:%M %p ET") + (" · incl. pre/post-market" if is_pm else ""),
           "price": last_close, "monthName": NOW.strftime("%B")}

    # ------- ranges -------
    def rng(sl):
        if sl.empty:
            return None
        return {"low": round(float(sl["Low"].min()), 2),
                "high": round(float(sl["High"].max()), 2)}
    week_start = (NOW - timedelta(days=NOW.weekday())).replace(hour=0, minute=0)
    out["ranges"] = {
        "daily": rng(daily[daily["date"] == last_bar_date]),
        "weekly": rng(daily[daily.index >= week_start]),
        "monthly": rng(daily[(daily.index.year == NOW.year) & (daily.index.month == NOW.month)]),
        "yearly": rng(daily[daily.index >= NOW - timedelta(days=365)])}

    # ------- intraday timing -------
    m15d = m15.copy()
    m15d["date"] = m15d.index.date
    hi_t, lo_t = [], []
    ph_hi, ph_lo, ph_bars = [], [], []
    for dte, g in m15d.groupby("date"):
        if len(g) < 10:
            continue
        hi_t.append(g["High"].idxmax().strftime("%H:%M"))
        lo_t.append(g["Low"].idxmin().strftime("%H:%M"))
        hrs = planetary_hours(dte)
        ph_hi.append(ruler_at(hrs, g["High"].idxmax()))
        ph_lo.append(ruler_at(hrs, g["Low"].idxmin()))
        ph_bars.extend(ruler_at(hrs, t) for t in g.index)
    out["intraday15m"] = {"days": len(hi_t), "high": dist(hi_t), "low": dist(lo_t)}

    # which planetary hour-ruler owns the day's extreme, vs time-share baseline
    ph_base = pd.Series([r for r in ph_bars if r]).value_counts(normalize=True)

    def ph_stats(events):
        ev = [r for r in events if r]
        rows = []
        if not ev:
            return rows
        for r, c in pd.Series(ev).value_counts().items():
            b = float(ph_base.get(r, 0))
            if b > 0 and c >= 5:
                rows.append({"ruler": r, "lift": round((c / len(ev)) / b, 2),
                             "hits": int(c), "n": len(ev),
                             "basePct": round(b * 100, 1)})
        rows.sort(key=lambda x: -x["lift"])
        return rows

    ph_high, ph_low = ph_stats(ph_hi), ph_stats(ph_lo)
    hot_hi = [r["ruler"] for r in ph_high if r["lift"] >= 1.3][:2]
    hot_lo = [r["ruler"] for r in ph_low if r["lift"] >= 1.3][:2]
    out["planetHours"] = {"high": ph_high[:4], "low": ph_low[:4],
                          "hotHigh": hot_hi, "hotLow": hot_lo, "days": len(ph_hi)}

    hd = hourly.copy()
    hd["date"] = hd.index.date
    hi_h = [g["High"].idxmax().strftime("%H:%M") for _, g in hd.groupby("date") if len(g) >= 5]
    out["intradayHourly"] = {"days": len(hi_h), "high": dist(hi_h), "low": {}}

    # ------- weekday of weekly high/low -------
    d5 = daily[daily.index >= NOW - timedelta(days=365 * 5)].copy()
    d5["iso"] = d5.index.strftime("%G-%V")
    wk_hi, wk_lo = [], []
    for _, g in d5.groupby("iso"):
        if len(g) < 4:
            continue
        wk_hi.append(g["High"].idxmax().strftime("%A"))
        wk_lo.append(g["Low"].idxmin().strftime("%A"))
    def dist_ord(items):
        s = pd.Series(items).value_counts(normalize=True)
        return {d: round(float(s.get(d, 0)) * 100, 1) for d in WEEKDAYS}
    out["weekday"] = {"weeks": len(wk_hi), "high": dist_ord(wk_hi), "low": dist_ord(wk_lo)}

    # ------- day of month + seasonality -------
    d5["ym"] = d5.index.strftime("%Y-%m")
    mo_hi = [int(g["High"].idxmax().day) for _, g in d5.groupby("ym") if len(g) >= 15]
    mo_lo = [int(g["Low"].idxmin().day) for _, g in d5.groupby("ym") if len(g) >= 15]
    def bucket3(days_list):
        s = pd.Series(days_list)
        return {"early (1st-10th)": round(float((s <= 10).mean()) * 100, 1),
                "mid (11th-20th)": round(float(((s > 10) & (s <= 20)).mean()) * 100, 1),
                "late (21st-31st)": round(float((s > 20).mean()) * 100, 1)}
    out["dayOfMonth"] = {"months": len(mo_hi), "high": bucket3(mo_hi), "low": bucket3(mo_lo)}

    mret = daily["Close"].resample("ME").last().pct_change().dropna()
    seas = mret.groupby(mret.index.month).agg(["mean", lambda x: (x > 0).mean(), "count"])
    seas.columns = ["mean", "winrate", "n"]
    out["seasonality"] = {
        datetime(2000, m, 1).strftime("%b"): {
            "avgRet": round(float(seas.loc[m, "mean"]) * 100, 2),
            "winRate": round(float(seas.loc[m, "winrate"]) * 100, 0),
            "n": int(seas.loc[m, "n"])}
        for m in range(1, 13) if m in seas.index}
    out["seasonalityYears"] = int(mret.index.year.nunique())

    # ------- swing engine -------
    zz_df = daily[daily.index >= NOW - timedelta(days=365 * 5)]
    # volatility-scaled threshold: ~2.5x median 20d range, clamped 4..10%
    dvol = float((np.log(zz_df["Close"]).diff().rolling(20).std().median()) * np.sqrt(20))
    THRESH = min(0.10, max(0.04, round(dvol * 1.3, 3)))
    pivots, cur_dir, ext_i = zigzag(zz_df, THRESH)
    if len(pivots) < 8:
        THRESH = max(0.03, THRESH / 2)
        pivots, cur_dir, ext_i = zigzag(zz_df, THRESH)
    if len(pivots) < 4:
        raise ValueError(f"not enough swing pivots for {tkr}")

    spacings = [pivots[k]["i"] - pivots[k - 1]["i"] for k in range(1, len(pivots))]
    amps = [abs(pivots[k]["price"] / pivots[k - 1]["price"] - 1) for k in range(1, len(pivots))]
    up_amps = [pivots[k]["price"] / pivots[k - 1]["price"] - 1
               for k in range(1, len(pivots)) if pivots[k]["type"] == "high"]
    dn_amps = [1 - pivots[k]["price"] / pivots[k - 1]["price"]
               for k in range(1, len(pivots)) if pivots[k]["type"] == "low"]
    med_spacing = max(2, int(np.median(spacings)))
    med_amp = float(np.median(amps))
    med_up = float(np.median(up_amps)) if up_amps else med_amp
    med_dn = float(np.median(dn_amps)) if dn_amps else med_amp

    hits2 = hits3 = tested = 0
    for k in range(6, len(pivots)):
        pred = pivots[k - 1]["i"] + int(np.median(spacings[: k - 1]))
        err = abs(pivots[k]["i"] - pred)
        tested += 1
        hits2 += err <= 2
        hits3 += err <= 3
    out["swing"] = {
        "thresholdPct": round(THRESH * 100, 1), "pivotCount": len(pivots),
        "medianSpacingTradingDays": med_spacing,
        "medianAmplitudePct": round(med_amp * 100, 1),
        "hitRate2d": round(hits2 / tested * 100, 0) if tested else None,
        "hitRate3d": round(hits3 / tested * 100, 0) if tested else None,
        "tested": tested,
        "recentPivots": [{"date": p["date"].strftime("%Y-%m-%d"), "type": p["type"],
                          "price": round(p["price"], 2)} for p in pivots[-8:]]}

    # ------- support / resistance from clustered fine-grained pivots (2y) -------
    zz2 = daily[daily.index >= NOW - timedelta(days=365 * 2)]
    fpiv, _, _ = zigzag(zz2, max(0.02, THRESH / 2))
    lvl_prices = sorted(p["price"] for p in fpiv)
    clusters = []
    for pr in lvl_prices:
        # merge nearby pivots, but cap a cluster's total span at ~4% so dense
        # zones don't daisy-chain into one giant blob
        if clusters and pr <= clusters[-1][-1] * 1.015 and pr <= clusters[-1][0] * 1.04:
            clusters[-1].append(pr)
        else:
            clusters.append([pr])
    levels = [{"price": float(np.mean(c)), "touches": len(c)} for c in clusters]
    sup = sorted((l for l in levels if l["price"] < last_close * 0.995),
                 key=lambda l: -l["price"])
    resi = sorted((l for l in levels if l["price"] > last_close * 1.005),
                  key=lambda l: l["price"])
    yr = out["ranges"]["yearly"]
    if yr and len(resi) < 2 and yr["high"] > last_close * 1.005:
        resi.append({"price": yr["high"], "touches": 1})
        resi.sort(key=lambda l: l["price"])
    if yr and len(sup) < 2 and yr["low"] < last_close * 0.995:
        sup.append({"price": yr["low"], "touches": 1})
        sup.sort(key=lambda l: -l["price"])
    def fmtl(l):
        return {"price": round(l["price"], 2), "touches": l["touches"],
                "distPct": round((l["price"] / last_close - 1) * 100, 1)}
    out["levels"] = {"support": [fmtl(l) for l in sup[:3]],
                     "resistance": [fmtl(l) for l in resi[:3]]}

    # ------- strategy backtests -------
    bt = {}
    d5b = daily[daily.index >= NOW - timedelta(days=365 * 5)].copy()
    bt["overnight"] = btstats(d5b["Open"] / d5b["Close"].shift(1) - 1)
    bt["intraday"] = btstats(d5b["Close"] / d5b["Open"] - 1)
    s2, s2b = [], []
    for _, g in hd.groupby("date"):
        g = g.sort_index()
        if len(g) < 6:
            continue
        b = g[g.index.strftime("%H:%M") == "10:30"]
        if not b.empty:
            s2.append(float(g["Close"].iloc[-1] / b["Open"].iloc[0] - 1))
        s2b.append(float(g["Close"].iloc[-1] / g["Open"].iloc[0] - 1))
    bt["buy1030SellClose"] = btstats(s2)
    bt["openToClose2y"] = btstats(s2b)
    out["backtests"] = bt

    # ------- Gann / Fib counts vs controls -------
    cal_dates = [p["date"].date() for p in pivots]
    piv_idx = [p["i"] for p in pivots]

    def count_hits(counts, gaps, tol):
        hits = pairs = 0
        for j in range(1, len(gaps)):
            for i in range(j):
                gap = gaps[j] - gaps[i] if isinstance(gaps[0], int) else (gaps[j] - gaps[i]).days
                if gap > (370 if tol == 2 else 150):
                    continue
                pairs += 1
                if any(abs(gap - g) <= tol for g in counts):
                    hits += 1
        return round(hits / pairs * 100, 1) if pairs else 0

    gann_rate = count_hits(GANN, cal_dates, 2)
    gann_ctrl = count_hits(GANN_CTRL, cal_dates, 2)
    fib_rate = count_hits(FIB, piv_idx, 1)
    fib_ctrl = count_hits(FIB_CTRL, piv_idx, 1)

    gann_up = []
    for p in pivots[-3:]:
        for g in GANN:
            d = p["date"].date() + timedelta(days=g)
            if NOW.date() < d <= NOW.date() + timedelta(days=60):
                gann_up.append({"date": d.strftime("%Y-%m-%d"),
                                "rule": f"{g} days from {p['type']} {p['date'].strftime('%m/%d')}"})
    gann_up.sort(key=lambda x: x["date"])

    anniv_hits = 0
    for j, dj in enumerate(cal_dates):
        for i in range(j):
            di = cal_dates[i]
            if dj.year > di.year:
                try:
                    same = di.replace(year=dj.year)
                except ValueError:
                    continue
                if abs((dj - same).days) <= 3:
                    anniv_hits += 1
                    break

    fib_up = []
    n_total = len(zz_df)
    for p in pivots[-3:]:
        for g in FIB:
            ahead = p["i"] + g - (n_total - 1)
            if 0 < ahead <= 42:
                d = add_trading_days(last_bar_date, ahead)
                fib_up.append({"date": d.strftime("%Y-%m-%d"),
                               "rule": f"Fib {g} bars from {p['type']} {p['date'].strftime('%m/%d')}"})
    fib_up.sort(key=lambda x: x["date"])

    # ------- Hurst cycles -------
    logc = np.log(zz_df["Close"].values)
    hurst, hurst_events = {}, []
    lows_n = [p["i"] for p in pivots if p["type"] == "low"]
    for P in [10, 20, 40, 80]:
        seg = logc[-3 * P:]
        n = np.arange(len(seg))
        seg_d = seg - np.polyval(np.polyfit(n, seg, 1), n)
        a = 2 / len(seg) * np.sum(seg_d * np.cos(2 * np.pi * n / P))
        b = 2 / len(seg) * np.sum(seg_d * np.sin(2 * np.pi * n / P))
        theta, amp = np.arctan2(b, a), np.hypot(a, b)
        last_n = len(seg) - 1
        def next_at(phase_target):
            n0 = P * ((theta + phase_target) % (2 * np.pi)) / (2 * np.pi)
            k = n0
            while k <= last_n:
                k += P
            return int(round(k - last_n))
        t_ahead, c_ahead = next_at(np.pi), next_at(0.0)
        tol_bars = max(1, int(round(0.15 * P)))
        n_end = len(logc) - 1
        n_tr = P * ((theta + np.pi) % (2 * np.pi)) / (2 * np.pi)
        def phase_dist(i):
            ni = i - (n_end - last_n)
            return min(abs((ni - n_tr) % P), P - abs((ni - n_tr) % P))
        obs = round(sum(1 for i in lows_n if phase_dist(i) <= tol_bars) / len(lows_n) * 100, 0) if lows_n else 0
        hurst[str(P)] = {"nextTroughDays": t_ahead, "nextCrestDays": c_ahead,
                         "ampPct": round(amp * 100, 2), "lowsAlignedPct": obs,
                         "chancePct": round((2 * tol_bars + 1) / P * 100, 0)}
        for ahead, kind in [(t_ahead, "trough"), (c_ahead, "crest")]:
            d = add_trading_days(last_bar_date, ahead)
            if d <= NOW.date() + timedelta(days=60):
                hurst_events.append({"date": d.strftime("%Y-%m-%d"),
                                     "cycle": f"{P}-day", "kind": kind})
    hurst_events.sort(key=lambda x: x["date"])

    # ------- lunar/retro alignment for this ticker's pivots -------
    def moon_align(ptype):
        ds = [p["date"].date() for p in pivots if p["type"] == ptype]
        md = [m["date"] for m in MOONS_HIST]
        if not ds:
            return 0
        hits = sum(1 for d in ds if min(abs((d - m).days) for m in md) <= 1)
        return round(hits / len(ds) * 100, 0)
    moon_low, moon_high = moon_align("low"), moon_align("high")
    moon_chance = round(3 / 14.77 * 100, 0)
    retro_piv = round(sum(1 for d in cal_dates if d in RETRO_SET) / len(cal_dates) * 100, 0)

    out["methods"] = {
        "gann": {"rate": gann_rate, "control": gann_ctrl, "counts": GANN,
                 "annivHits": anniv_hits, "pivots": len(cal_dates), "upcoming": gann_up[:10]},
        "fib": {"rate": fib_rate, "control": fib_ctrl, "counts": FIB, "upcoming": fib_up[:10]},
        "hurst": {"cycles": hurst, "upcoming": hurst_events},
        "astro": {"moonLowPct": moon_low, "moonHighPct": moon_high, "moonChance": moon_chance,
                  "retroPivPct": retro_piv, "retroChance": round(RETRO_SHARE * 100, 0),
                  "moonsNext": [{"date": m["date"].strftime("%Y-%m-%d"), "time": m["time"],
                                 "kind": m["kind"]} for m in MOONS_NEXT],
                  "retroRanges": [[a.strftime("%Y-%m-%d"), b.strftime("%Y-%m-%d")]
                                  for a, b in RETRO_RANGES]}}

    # ------- per-stock vibration signature (astro + numerology) -------
    vib, vib_bumps = vibration_scan(tkr, pivots)
    vib_upcoming = []
    for lbl, sm, which, w in vib_bumps:
        for fd in [NOW.date() + timedelta(days=k) for k in range(1, 61)]:
            i = VIDX.get(fd)
            if i is not None and sm[i] and fd.weekday() < 5:
                vib_upcoming.append({"date": fd.strftime("%Y-%m-%d"),
                                     "rule": lbl + (" (highs)" if which == "H" else
                                                    " (lows)" if which == "L" else "")})
    # Sepharial techniques (Chaldean ruler, stations, Moon declination)
    sep, sep_bumps = sepharial_scan(tkr, pivots)
    vib_bumps = vib_bumps + sep_bumps
    for lbl, sm, which, w in sep_bumps:
        for fd in [NOW.date() + timedelta(days=k) for k in range(1, 61)]:
            i = VIDX.get(fd)
            if i is not None and sm[i] and fd.weekday() < 5:
                vib_upcoming.append({"date": fd.strftime("%Y-%m-%d"), "rule": lbl})
    vib["sepharial"] = sep
    seen_v = set()
    vib_upcoming.sort(key=lambda v: v["date"])
    vib["upcoming"] = [v for v in vib_upcoming
                       if not (v["date"] + v["rule"] in seen_v or seen_v.add(v["date"] + v["rule"]))][:18]
    out["vibration"] = vib

    # ------- grade past predictions & learn method weights -------
    trading_dates = [d.date() for d in zz_df.index]

    def td_pos(d):
        return bisect.bisect_left(trading_dates, d)

    resolved = []
    fam_stats = {}
    for e in PRED_LOG["entries"]:
        if e["ticker"] != tkr:
            continue
        for p in e["preds"]:
            pdate = datetime.strptime(p["isoDate"], "%Y-%m-%d").date()
            # only grade once enough data exists past the predicted date for a
            # swing to be confirmed (8 trading days)
            if td_pos(pdate) > len(trading_dates) - 8:
                continue
            cands = [v for v in pivots if v["type"] == p["type"]]
            if not cands:
                continue
            best = min(cands, key=lambda v: abs(td_pos(v["date"].date()) - td_pos(pdate)))
            err = td_pos(best["date"].date()) - td_pos(pdate)
            found = abs(err) <= 10
            rec = {"logged": e["logged"], "predDate": p["isoDate"], "type": p["type"],
                   "predPrice": p["price"],
                   "actualDate": best["date"].strftime("%Y-%m-%d") if found else None,
                   "actualPrice": round(best["price"], 2) if found else None,
                   "errDays": err if found else None,
                   "hit2": bool(found and abs(err) <= 2),
                   "hit3": bool(found and abs(err) <= 3),
                   "methods": p.get("methods", [])}
            resolved.append(rec)
            for tag in rec["methods"]:
                fam = method_family(tag)
                st = fam_stats.setdefault(fam, {"n": 0, "hits": 0})
                st["n"] += 1
                st["hits"] += rec["hit2"]

    # dedupe (same prediction re-logged on consecutive days)
    seen = set()
    resolved_u = []
    for r in resolved:
        key = (r["predDate"], r["type"])
        if key not in seen:
            seen.add(key)
            resolved_u.append(r)
    resolved_u.sort(key=lambda r: r["predDate"])

    n_res = len(resolved_u)
    hit2s = sum(r["hit2"] for r in resolved_u)
    hit3s = sum(r["hit3"] for r in resolved_u)
    base_rate = (hit2s + 1) / (n_res + 2)  # smoothed

    # price-accuracy grading + learned calibration of future targets:
    # if predicted prices systematically over/undershoot, scale targets
    perrs = [abs(r["actualPrice"] / r["predPrice"] - 1) for r in resolved_u
             if r["actualPrice"] and r["predPrice"]]
    price_med_err = round(float(np.median(perrs)) * 100, 1) if perrs else None
    cal_hi = cal_lo = 1.0
    hi_ratios = [r["actualPrice"] / r["predPrice"] for r in resolved_u
                 if r["type"] == "high" and r["actualPrice"]]
    lo_ratios = [r["actualPrice"] / r["predPrice"] for r in resolved_u
                 if r["type"] == "low" and r["actualPrice"]]
    if len(hi_ratios) >= 4:
        cal_hi = float(np.clip(np.median(hi_ratios), 0.85, 1.15))
    if len(lo_ratios) >= 4:
        cal_lo = float(np.clip(np.median(lo_ratios), 0.85, 1.15))
    # learned multiplier per method family: >1 = earning trust, <1 = losing it
    MF = {}
    for fam, st in fam_stats.items():
        if st["n"] >= 3:
            MF[fam] = round(min(2.0, max(0.5, ((st["hits"] + 1) / (st["n"] + 2)) / base_rate)), 2)
    out["trackRecord"] = {
        "since": min((e["logged"] for e in PRED_LOG["entries"] if e["ticker"] == tkr),
                     default=NOW.strftime("%Y-%m-%d")),
        "resolved": resolved_u[-30:], "n": n_res,
        "hit2Rate": round(hit2s / n_res * 100, 0) if n_res else None,
        "hit3Rate": round(hit3s / n_res * 100, 0) if n_res else None,
        "priceMedErrPct": price_med_err,
        "priceCalibHigh": round(cal_hi, 3), "priceCalibLow": round(cal_lo, 3),
        "methodFactors": MF,
        "famStats": {f: s for f, s in fam_stats.items()}}

    # ------- confluence forecast -------
    def modal(distribution, window=None):
        items = distribution.items()
        if window:
            f = {k: v for k, v in distribution.items() if window[0] <= k <= window[1]}
            if f:
                items = f.items()
        return max(items, key=lambda kv: kv[1]) if distribution else ("09:30", 0)

    hi_mode, lo_mode = modal(out["intraday15m"]["high"]), modal(out["intraday15m"]["low"])
    hi_pm = modal(out["intraday15m"]["high"], ("12:00", "16:00"))
    lo_pm = modal(out["intraday15m"]["low"], ("12:00", "16:00"))

    last_piv = pivots[-1]
    prov_type = "high" if cur_dir >= 0 else "low"
    # the in-progress swing's running extreme — a more current price anchor
    # than the last confirmed pivot (learned from grading the 07/09 forecasts);
    # extended by the live pre/post-market price when it runs beyond the bars
    prov_price = float(zz_df["Close"].iloc[ext_i])
    if cur_dir >= 0:
        prov_price = max(prov_price, last_close)
    else:
        prov_price = min(prov_price, last_close)

    def edge_weight(obs, chance):
        return max(0.15, min(1.5, obs / chance)) if chance > 0 else 0.3
    w_gann = edge_weight(gann_rate, gann_ctrl) * MF.get("gann", 1.0)
    w_fib = edge_weight(fib_rate, fib_ctrl) * MF.get("fib", 1.0)
    w_moon = edge_weight(max(moon_low, moon_high), moon_chance) * MF.get("moon", 1.0)
    w_rhythm_f = MF.get("rhythm", 1.0)
    w_hurst_f = MF.get("hurst", 1.0)

    future = [add_trading_days(last_bar_date, k) for k in range(1, 46)]
    scoreL = {d: 0.0 for d in future}
    scoreH = {d: 0.0 for d in future}
    tags = {d: [] for d in future}

    def bump(d, pts, tag, which):
        if d in scoreL:
            if which in ("L", "B"):
                scoreL[d] += pts
            if which in ("H", "B"):
                scoreH[d] += pts
            if tag and tag not in tags[d]:
                tags[d].append(tag)

    t = prov_type
    d = add_trading_days(last_piv["date"].date(), med_spacing)
    if d <= NOW.date():
        d = add_trading_days(NOW.date(), 1)
    for _ in range(8):
        if d > future[-1]:
            break
        for off in range(-2, 3):
            dd = add_trading_days(d, off) if off else d
            pts = (1.0 if off == 0 else (0.7 if abs(off) == 1 else 0.4)) * w_rhythm_f
            bump(dd, pts, f"Rhythm {med_spacing}-bar" if off == 0 else None,
                 "L" if t == "low" else "H")
        t = "low" if t == "high" else "high"
        d = add_trading_days(d, med_spacing)

    for g in gann_up:
        gd = datetime.strptime(g["date"], "%Y-%m-%d").date()
        for off in (-1, 0, 1):
            dd = gd + timedelta(days=off)
            while dd.weekday() >= 5:
                dd += timedelta(days=1)
            bump(dd, w_gann * (1.0 if off == 0 else 0.6),
                 f"Gann {g['rule']}" if off == 0 else None, "B")
    for g in fib_up:
        bump(datetime.strptime(g["date"], "%Y-%m-%d").date(), w_fib, g["rule"], "B")
    for ev in hurst_events:
        ed = datetime.strptime(ev["date"], "%Y-%m-%d").date()
        P = int(ev["cycle"].split("-")[0])
        st = hurst[str(P)]
        w = edge_weight(st["lowsAlignedPct"], st["chancePct"]) * (0.5 + P / 80) * w_hurst_f
        for off in range(-2, 3):
            dd = add_trading_days(ed, off) if off else ed
            pts = w * (1.0 if off == 0 else (0.7 if abs(off) == 1 else 0.4))
            bump(dd, pts, f"Hurst {ev['cycle']} {ev['kind']}" if off == 0 else None,
                 "L" if ev["kind"] == "trough" else "H")
    for m in MOONS_NEXT:
        md = m["date"]
        while md.weekday() >= 5:
            md += timedelta(days=1)
        which = "L" if moon_low >= moon_high else "H"
        bump(md, 0.5 * w_moon, f"{m['kind']} moon {m['time']}",
             which if max(moon_low, moon_high) > moon_chance else "B")

    # 6) this stock's own mined vibration + Sepharial signals
    #    (each family's weight is earned/lost via the track record)
    for lbl, sm, which, w in vib_bumps:
        tag = lbl if lbl.startswith("Sepharial") else "Vibe: " + lbl
        fam_f = MF.get(method_family(tag), 1.0)
        for fd in future:
            i = VIDX.get(fd)
            if i is not None and i < len(sm) and sm[i]:
                bump(fd, w * fam_f, tag, which)

    combined = [(d, max(scoreL[d], scoreH[d]), "low" if scoreL[d] >= scoreH[d] else "high")
                for d in future]
    combined.sort(key=lambda x: -x[1])
    chosen = []
    for d, s, ty in combined:
        if len(chosen) == 5:
            break
        if all(abs((d - c[0]).days) >= 4 for c in chosen):
            chosen.append((d, s, ty))
    chosen.sort(key=lambda x: x[0])

    # prediction #1 is ALWAYS the completion of the swing in progress — where
    # the CURRENT move is heading and when — before any turn the other way.
    # (a trader must never see "HIGH on date X" while price is still falling)
    first_d = add_trading_days(last_piv["date"].date(), med_spacing)
    if first_d <= NOW.date():
        first_d = add_trading_days(NOW.date(), 1)
    seq = [(first_d, max(scoreL.get(first_d, 0), scoreH.get(first_d, 0), 0.5), prov_type)]
    for d, s, ty in chosen:
        if len(seq) == 5:
            break
        if d > first_d and (d - seq[-1][0]).days >= 3:
            seq.append((d, s, ty))
    chosen = seq

    preds = []
    # price targets measure a full swing from the previous OPPOSITE extreme:
    # event #1 completes the in-progress swing, so it projects from the last
    # confirmed pivot; later events chain from each projected extreme.
    # prev_type starts at the last CONFIRMED pivot so the forced first event
    # (same type as the provisional swing) is not flipped by alternation.
    prev_price, prev_type = last_piv["price"], last_piv["type"]
    first_base_confirmed = last_piv["price"]
    smax = max((s for _, s, _ in combined), default=1) or 1
    for k, (d, s, ty) in enumerate(chosen):
        if ty == prev_type:
            ty = "low" if prev_type == "high" else "high"
        base = prev_price
        if k == 0 and ty == prov_type:
            base = first_base_confirmed
        # cap the target by what volatility allows in the time available:
        # a 1-day-out extreme is a small move, a 3-week-out one can be a full
        # swing (learned from grading 07/09-07/14 forecasts: dates hit, prices
        # overshot badly on short horizons)
        ahead = future.index(d) + 1
        cap = 1.25 * (dvol / np.sqrt(20)) * np.sqrt(ahead)
        # crash regime: when already deep below the 20d high, moves run further
        # than calm-market vol implies — widen the cap with the drawdown
        dd20 = 1 - last_close / float(daily["Close"].tail(20).max())
        cap *= 1 + min(1.0, 2 * max(0.0, dd20))
        # a projected high can't sit below today's price (nor a low above it);
        # graded price errors feed back in as a learned calibration factor
        if ty == "high":
            price = max(min(base * (1 + med_up) * cal_hi, last_close * (1 + cap)), last_close)
        else:
            price = min(max(base * (1 - med_dn) * cal_lo, last_close * (1 - cap)), last_close)
        # snap to a real support/resistance level when one sits within 3% —
        # markets turn at levels, not at abstract percentages
        lv_c = out["levels"]["resistance"] if ty == "high" else out["levels"]["support"]
        near = [c["price"] for c in lv_c if abs(c["price"] / price - 1) < 0.03]
        if near:
            price = min(near, key=lambda v: abs(v - price))
        tmode = hi_mode if ty == "high" else lo_mode
        alt = hi_pm if ty == "high" else lo_pm
        moon_today = next((m for m in MOONS_NEXT if m["date"] == d), None)
        # this stock's hot hour-rulers, mapped to actual clock hours on that date
        hot = hot_hi if ty == "high" else hot_lo
        ph_str = None
        if hot:
            ses_s = datetime(d.year, d.month, d.day, 9, 30, tzinfo=ET)
            ses_e = datetime(d.year, d.month, d.day, 16, 0, tzinfo=ET)
            spans = []
            for s0, e0, r in planetary_hours(d):
                if r not in hot:
                    continue
                s2, e2 = max(s0, ses_s), min(e0, ses_e)
                if s2 < e2:
                    spans.append(f"{r} {s2.strftime('%I:%M').lstrip('0')}–"
                                 f"{e2.strftime('%I:%M %p').lstrip('0')}")
            ph_str = "; ".join(spans[:3]) or None
        preds.append({
            "n": k + 1, "type": ty,
            "date": d.strftime("%a %m/%d"), "isoDate": d.strftime("%Y-%m-%d"),
            "time": fmt_time(tmode[0]) + " ET", "timePct": tmode[1],
            "altTime": fmt_time(alt[0]) + " ET", "altTimePct": alt[1],
            "astroTime": moon_today["time"] if moon_today else None,
            "planetHour": ph_str,
            "price": round(price, 2),
            "dateWindow": f"{add_trading_days(d, -2).strftime('%m/%d')}–{add_trading_days(d, 2).strftime('%m/%d')}",
            "score": round(s, 2), "scoreMax": round(smax, 2),
            "methods": tags[d][:4]})
        prev_price, prev_type = price, ty
    out["predictions"] = preds

    # log today's predictions for future grading (re-running the same day
    # replaces that day's entry, so the latest forecast is what gets graded)
    today_str = NOW.strftime("%Y-%m-%d")
    PRED_LOG["entries"] = [e for e in PRED_LOG["entries"]
                           if not (e["ticker"] == tkr and e["logged"] == today_str)]
    PRED_LOG["entries"].append({
        "ticker": tkr, "logged": today_str,
        "preds": [{"isoDate": p["isoDate"], "type": p["type"], "price": p["price"],
                   "methods": p["methods"]} for p in preds]})

    out["predictionBasis"] = {
        "lastPivot": {"date": last_piv["date"].strftime("%Y-%m-%d"), "type": last_piv["type"],
                      "price": round(last_piv["price"], 2)},
        "medianSpacing": med_spacing, "medianAmpPct": round(med_amp * 100, 1),
        "medianUpPct": round(med_up * 100, 1), "medianDownPct": round(med_dn * 100, 1),
        "hitRate2d": out["swing"]["hitRate2d"], "hitRate3d": out["swing"]["hitRate3d"]}

    # ------- chart -------
    chart_df = daily[daily.index >= NOW - timedelta(days=280)]
    out["chart"] = {
        "dates": [d.strftime("%Y-%m-%d") for d in chart_df.index],
        "closes": [round(float(c), 2) for c in chart_df["Close"]],
        "pivots": [{"date": p["date"].strftime("%Y-%m-%d"), "type": p["type"],
                    "price": round(p["price"], 2)} for p in pivots
                   if p["date"] >= NOW - timedelta(days=280)]}
    return out


all_out = {}
for tkr in TICKERS:
    try:
        all_out[tkr] = analyze(tkr)
        p = all_out[tkr]
        print(f"{tkr}: OK — price {p['price']}, {p['swing']['pivotCount']} pivots "
              f"(threshold {p['swing']['thresholdPct']}%), spacing {p['swing']['medianSpacingTradingDays']}d, "
              f"first pred {p['predictions'][0]['date']} {p['predictions'][0]['type']}")
    except Exception as e:
        print(f"{tkr}: FAILED — {e}")

with open(LOG_FILE, "w", encoding="utf-8") as f:
    json.dump(PRED_LOG, f, indent=1)

with open(EXT_FILE, "w", encoding="utf-8") as f:
    json.dump(EXTREMES, f)

with open("data.js", "w", encoding="utf-8") as f:
    f.write("const DATA_ALL = " + json.dumps(all_out) + ";\n")

# single self-contained file (data inlined) — works on phones via OneDrive,
# email, or a simple web upload, with no companion data.js needed
try:
    with open("dashboard.html", encoding="utf-8") as f:
        html = f.read()
    inline = "<script>const DATA_ALL = " + json.dumps(all_out) + ";</script>"
    html = html.replace('<script src="data.js"></script>', inline)
    with open("dashboard_single.html", "w", encoding="utf-8") as f:
        f.write(html)
    # same file under the name GitHub Pages expects, ready to drag-and-drop
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("dashboard_single.html + index.html written (self-contained)")
except Exception as e:
    print("single-file build failed:", e)

print(f"data.js written with {len(all_out)} tickers; "
      f"prediction log has {len(PRED_LOG['entries'])} daily entries")
