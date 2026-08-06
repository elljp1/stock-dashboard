"""Build option-trade candidates per ticker from live chains + model levels.

Entry/exit are PAIRED events from the forecast chain: a trade entered at event
E exits at the next OPPOSITE event strictly AFTER E. Cards are tagged by how
soon they are actionable (TODAY / THIS WEEK / LATER) and sorted soonest-first,
so the top card is always the most actionable trade right now.

Importable: build_trades(dall) -> {ticker: {...}}
"""
import urllib.request
import http.cookiejar
import json
from datetime import datetime, timezone, date


def _session():
    jar = http.cookiejar.CookieJar()
    op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
    op.addheaders = [("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64)")]
    try:
        op.open("https://fc.yahoo.com", timeout=20)
    except Exception:
        pass
    crumb = op.open("https://query1.finance.yahoo.com/v1/test/getcrumb",
                    timeout=20).read().decode()
    return op, crumb


def _mid(o):
    b, a = o.get("bid", 0) or 0, o.get("ask", 0) or 0
    if b and a:
        return (b + a) / 2
    return o.get("lastPrice", 0) or 0


def _nearest(strikes, target, below=True, either=False):
    if either and strikes:
        return min(strikes, key=lambda s: abs(s - target))
    c = [s for s in strikes if (s <= target if below else s >= target)]
    if c:
        best = max(c) if below else min(c)
        # if the one-sided pick is far off but a closer strike exists, take it
        alt = min(strikes, key=lambda s: abs(s - target))
        if target and abs(best / target - 1) > 0.03 and abs(alt / target - 1) < abs(best / target - 1):
            return alt
        return best
    return min(strikes, key=lambda s: abs(s - target)) if strikes else None


def _when(ev):
    """Human 'date - time window' for a chain event."""
    return f"{ev['date']} - " + (ev.get("planetHour") or ev.get("time") or "")


def _bizdays(d0, d1):
    n, d = 0, d0
    while d < d1:
        d = date.fromordinal(d.toordinal() + 1)
        if d.weekday() < 5:
            n += 1
    return n


def build_trades(dall):
    op, crumb = _session()

    def chain(tkr, date_epoch=None):
        url = f"https://query2.finance.yahoo.com/v7/finance/options/{tkr}?crumb={crumb}"
        if date_epoch:
            url += f"&date={date_epoch}"
        return json.load(op.open(url, timeout=30))["optionChain"]["result"][0]

    now = datetime.now(timezone.utc)
    today = date.today()
    out = {}
    for tkr, D in dall.items():
        spot = D["price"]
        preds = sorted(D["predictions"], key=lambda p: p["isoDate"])
        sup = D["levels"]["support"]
        res = D["levels"]["resistance"]
        trades = []

        def ev_date(e):
            return datetime.strptime(e["isoDate"], "%Y-%m-%d").date()

        # pair each event with the next OPPOSITE event after it
        pairs = []
        for i, e in enumerate(preds):
            nxt = next((f for f in preds[i + 1:] if f["type"] != e["type"]), None)
            if nxt:
                pairs.append((e, nxt))
        first_low = next((p for p in pairs if p[0]["type"] == "low"), None)
        first_high = next((p for p in pairs if p[0]["type"] == "high"), None)

        def horizon(d):
            n = _bizdays(today, d)
            if n <= 0:
                return "TODAY"
            if n <= 5:
                return "THIS WEEK"
            return f"IN {n} SESSIONS"

        try:
            base = chain(tkr)
            exps = base["expirationDates"]

            def pick_exp(min_days):
                for e in exps:
                    if (datetime.fromtimestamp(e, tz=timezone.utc) - now).days >= min_days:
                        return e
                return exps[-1]

            # ---- A) trades anchored on the next LOW (sell puts into weakness)
            if first_low:
                entry, exit_ev = first_low
                ed, xd = ev_date(entry), ev_date(exit_ev)
                hz = horizon(ed)
                # expiry must outlive the exit event
                e1 = pick_exp(max(10, (xd - today).days + 10))
                e1s = datetime.fromtimestamp(e1, tz=timezone.utc).strftime("%b %d")
                res1 = chain(tkr, e1)
                puts1 = {p["strike"]: p for p in res1["options"][0]["puts"]}
                ps = sorted(puts1)

                k0 = _nearest(ps, entry["price"])
                if k0 and _mid(puts1[k0]) > 0:
                    m0 = _mid(puts1[k0])
                    trades.append({
                        "kind": "MODEL", "hz": hz, "sortd": ed.isoformat(),
                        "label": f"Sell {e1s} ${k0:g} put AT the projected low",
                        "detail": f"~${m0:.2f} (${m0*100:.0f}/contract) - yield {m0/k0*100:.1f}% - "
                                  f"breakeven ${k0-m0:.2f} - collateral ${k0*100:,.0f}",
                        "thesis": f"enter at the projected {entry['date']} low (~${entry['price']}), "
                                  f"buy-to-close into the {exit_ev['date']} high (~${exit_ev['price']}). "
                                  f"Highest premium - assigned if the low overshoots; size accordingly",
                        "exp": e1s, "strikes": [k0], "premium": round(m0, 2),
                        "execute": _when(entry), "exitWin": _when(exit_ev)})

                deep = min([l["price"] for l in sup[1:2]] + [spot * 0.9])
                k1 = _nearest(ps, deep)
                if k1 and _mid(puts1[k1]) > 0:
                    m1 = _mid(puts1[k1])
                    trades.append({
                        "kind": "INCOME", "hz": hz, "sortd": ed.isoformat(),
                        "label": f"Sell {e1s} ${k1:g} put (cash-secured)",
                        "detail": f"~${m1:.2f} (${m1*100:.0f}/contract) - yield {m1/k1*100:.1f}% - "
                                  f"breakeven ${k1-m1:.2f} - collateral ${k1*100:,.0f}",
                        "thesis": "strike below the deep/crash target - paid to wait",
                        "exp": e1s, "strikes": [k1], "premium": round(m1, 2),
                        "execute": _when(entry), "exitWin": "50% profit or ~1 week"})

                ks = _nearest(ps, entry["price"])
                kl = _nearest(ps, ks * 0.96) if ks else None
                if ks and kl and kl < ks:
                    cr = _mid(puts1[ks]) - _mid(puts1[kl])
                    w = ks - kl
                    if cr > 0 and w > cr:
                        trades.append({
                            "kind": "DEFINED", "hz": hz, "sortd": ed.isoformat(),
                            "label": f"Sell {e1s} ${ks:g}/${kl:g} put spread",
                            "detail": f"credit ~${cr:.2f} (${cr*100:.0f}) - max loss ${(w-cr)*100:.0f} - "
                                      f"ROI {cr/(w-cr)*100:.0f}% if price holds ${ks:g}",
                            "thesis": "short strike at the projected low shelf, risk capped",
                            "exp": e1s, "strikes": [ks, kl], "premium": round(cr, 2),
                            "execute": _when(entry), "exitWin": "50% profit or ~1 week"})

                # bounce play off that low, targeting the paired high
                e2 = pick_exp(max(7, (xd - today).days + 5))
                e2s = datetime.fromtimestamp(e2, tz=timezone.utc).strftime("%b %d")
                calls2 = {c["strike"]: c for c in chain(tkr, e2)["options"][0]["calls"]}
                cs = sorted(calls2)
                kb = _nearest(cs, entry["price"], below=False)
                kt = _nearest(cs, exit_ev["price"], below=False)
                if kb and kt and kt > kb:
                    deb = _mid(calls2[kb]) - _mid(calls2[kt])
                    w = kt - kb
                    if deb > 0:
                        trades.append({
                            "kind": "BOUNCE", "hz": hz, "sortd": ed.isoformat(),
                            "label": f"Buy {e2s} ${kb:g}/${kt:g} call spread",
                            "detail": f"debit ~${deb:.2f} (${deb*100:.0f}) - max value ${w*100:.0f} - "
                                      f"ROI {max(0,(w-deb))/deb*100:.0f}% if ${exit_ev['price']} prints by {exit_ev['date']}",
                            "thesis": f"targets the {exit_ev['date']} rebound. DO NOT enter on the date alone - "
                                      f"wait for the low to CONFIRM (price back +3% off the low). "
                                      f"Bounce bets in a falling tape are lottery tickets (graded lesson 7/23-24)",
                            "exp": e2s, "strikes": [kb, kt], "premium": round(deb, 2),
                            "execute": _when(entry) + " - AFTER +3% reversal confirms",
                            "exitWin": _when(exit_ev)})

            # ---- B) if a HIGH comes first (price rising into it), trade THAT
            if first_high and (not first_low or ev_date(first_high[0]) < ev_date(first_low[0])):
                hi_ev, after_low = first_high
                hd = ev_date(hi_ev)
                hz = horizon(hd)
                e3 = pick_exp(max(7, (hd - today).days + 5))
                e3s = datetime.fromtimestamp(e3, tz=timezone.utc).strftime("%b %d")
                res3 = chain(tkr, e3)
                calls3 = {c["strike"]: c for c in res3["options"][0]["calls"]}
                puts3 = {p["strike"]: p for p in res3["options"][0]["puts"]}
                cs3, ps3 = sorted(calls3), sorted(puts3)
                kb = _nearest(cs3, spot, below=False)
                kt = _nearest(cs3, hi_ev["price"], below=False)
                if kb and kt and kt > kb:
                    deb = _mid(calls3[kb]) - _mid(calls3[kt])
                    w = kt - kb
                    if deb > 0:
                        trades.append({
                            "kind": "RIDE", "hz": "TODAY", "sortd": today.isoformat(),
                            "label": f"Buy {e3s} ${kb:g}/${kt:g} call spread (ride to the projected high)",
                            "detail": f"debit ~${deb:.2f} (${deb*100:.0f}) - max value ${w*100:.0f} - "
                                      f"ROI {max(0,(w-deb))/deb*100:.0f}% if ${hi_ev['price']} prints by {hi_ev['date']}",
                            "thesis": f"price is projected to rise into the {hi_ev['date']} high - "
                                      f"this is the actionable trade NOW, not the far-off put entry",
                            "exp": e3s, "strikes": [kb, kt], "premium": round(deb, 2),
                            "execute": f"now / today - {hi_ev.get('planetHour') or hi_ev.get('time','')}",
                            "exitWin": _when(hi_ev)})
                ksup = _nearest(ps3, sup[0]["price"] if sup else spot * 0.97)
                if ksup and _mid(puts3[ksup]) > 0:
                    mp = _mid(puts3[ksup])
                    trades.append({
                        "kind": "INCOME NOW", "hz": "TODAY", "sortd": today.isoformat(),
                        "label": f"Sell {e3s} ${ksup:g} put at nearest support",
                        "detail": f"~${mp:.2f} (${mp*100:.0f}/contract) - yield {mp/ksup*100:.1f}% - "
                                  f"breakeven ${ksup-mp:.2f} - collateral ${ksup*100:,.0f}",
                        "thesis": f"collect premium while price is projected to rise into {hi_ev['date']}; "
                                  f"strike sits on the nearest tested support",
                        "exp": e3s, "strikes": [ksup], "premium": round(mp, 2),
                        "execute": "now / today",
                        "exitWin": _when(hi_ev) + " (or 50% profit)"})
        except Exception as e:
            trades.append({"kind": "NOTE", "hz": "", "sortd": "9999",
                           "label": "No listed chain on this feed",
                           "detail": str(e)[:80], "thesis": "", "exp": "",
                           "strikes": [], "premium": 0, "execute": None, "exitWin": None})

        rank = {"TODAY": 0, "THIS WEEK": 1}
        trades.sort(key=lambda t: (t.get("sortd", "9999"), rank.get(t.get("hz"), 2)))
        out[tkr] = {"asof": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "spot": round(spot, 2), "trades": trades,
                    "bestToday": next((t["label"] for t in trades if t.get("hz") == "TODAY"), None),
                    "bestWeek": next((t["label"] for t in trades
                                      if t.get("hz") in ("TODAY", "THIS WEEK")), None)}
    return out


if __name__ == "__main__":
    dall = json.loads(open("data.js", encoding="utf-8").read()
                      .replace("const DATA_ALL = ", "").split("const TRADES")[0]
                      .strip().rstrip(";"))
    t = build_trades(dall)
    for tkr, v in t.items():
        print(f"\n===== {tkr}  spot {v['spot']} =====")
        for tr in v["trades"]:
            print(f" [{tr.get('hz','')}] {tr['kind']:10} {tr['label']}")
            print(f"      in: {tr.get('execute')}   out: {tr.get('exitWin')}")
