"""Build 3 option-trade candidates per ticker from live chains + model levels.

Importable: build_trades(dall) -> {ticker: {"asof":..., "spot":..., "trades":[...]}}
Run directly to print the current sheet.
"""
import urllib.request
import http.cookiejar
import json
from datetime import datetime, timezone


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


def _nearest(strikes, target, below=True):
    c = [s for s in strikes if (s <= target if below else s >= target)]
    return (max(c) if below else min(c)) if c else None


def build_trades(dall):
    op, crumb = _session()

    def chain(tkr, date_epoch=None):
        url = f"https://query2.finance.yahoo.com/v7/finance/options/{tkr}?crumb={crumb}"
        if date_epoch:
            url += f"&date={date_epoch}"
        return json.load(op.open(url, timeout=30))["optionChain"]["result"][0]

    today = datetime.now(timezone.utc)
    out = {}
    for tkr, D in dall.items():
        spot = D["price"]
        preds = D["predictions"]
        lows = [p for p in preds if p["type"] == "low"]
        highs = [p for p in preds if p["type"] == "high"]
        sup = D["levels"]["support"]
        trades = []
        try:
            base = chain(tkr)
            exps = base["expirationDates"]

            def pick_exp(min_days):
                for e in exps:
                    if (datetime.fromtimestamp(e, tz=timezone.utc) - today).days >= min_days:
                        return e
                return exps[-1]

            e1 = pick_exp(24)
            e1s = datetime.fromtimestamp(e1, tz=timezone.utc).strftime("%b %d")
            res1 = chain(tkr, e1)
            puts1 = {p["strike"]: p for p in res1["options"][0]["puts"]}
            pstrikes = sorted(puts1)

            # 0) MODEL conviction: sell the put AT the predicted low — max
            #    premium if the forecast is right; exit at the predicted high
            if lows:
                lp = lows[0]
                k0 = _nearest(pstrikes, lp["price"])
                if k0:
                    m0 = _mid(puts1[k0])
                    exit_note = (f"buy-to-close at the projected {highs[0]['date']} high"
                                 if highs else "close at 50% profit or ~1 week")
                    if m0 > 0:
                        trades.append({
                            "kind": "MODEL",
                            "label": f"Sell {e1s} ${k0:g} put AT the projected low",
                            "detail": f"≈${m0:.2f} (${m0*100:.0f}/contract) · "
                                      f"yield {m0/k0*100:.1f}% · breakeven ${k0-m0:.2f} · "
                                      f"collateral ${k0*100:,.0f}",
                            "thesis": f"full conviction play: enter at the projected "
                                      f"{lp['date']} low (~${lp['price']}), {exit_note}. "
                                      f"Highest premium — but assigned if the low overshoots "
                                      f"(crashes DO overshoot; size accordingly)",
                            "exp": e1s, "strikes": [k0], "premium": round(m0, 2)})

            deep = min([l["price"] for l in sup[1:2]] +
                       [p["price"] for p in lows[1:2]] + [spot * 0.9])
            k1 = _nearest(pstrikes, deep)
            if k1:
                m1 = _mid(puts1[k1])
                if m1 > 0:
                    trades.append({
                        "kind": "INCOME",
                        "label": f"Sell {e1s} ${k1:g} put (cash-secured)",
                        "detail": f"≈${m1:.2f} (${m1*100:.0f}/contract) · "
                                  f"yield {m1/k1*100:.1f}% · breakeven ${k1-m1:.2f} · "
                                  f"collateral ${k1*100:,.0f}",
                        "thesis": "strike below the deep/crash target — paid to wait",
                        "exp": e1s, "strikes": [k1], "premium": round(m1, 2)})

            tgt = lows[0]["price"] if lows else spot * 0.95
            ks = _nearest(pstrikes, tgt)
            kl = _nearest(pstrikes, ks * 0.96) if ks else None
            if ks and kl and kl < ks:
                cr = _mid(puts1[ks]) - _mid(puts1[kl])
                w = ks - kl
                if cr > 0 and w > cr:
                    trades.append({
                        "kind": "DEFINED",
                        "label": f"Sell {e1s} ${ks:g}/${kl:g} put spread",
                        "detail": f"credit ≈${cr:.2f} (${cr*100:.0f}) · "
                                  f"max loss ${(w-cr)*100:.0f} · "
                                  f"ROI {cr/(w-cr)*100:.0f}% if price holds ${ks:g}",
                        "thesis": "short strike at the projected low shelf, risk capped",
                        "exp": e1s, "strikes": [ks, kl], "premium": round(cr, 2)})

            if highs:
                hp = highs[0]
                dd = (datetime.strptime(hp["isoDate"], "%Y-%m-%d")
                      .replace(tzinfo=timezone.utc) - today).days
                e2 = pick_exp(max(7, dd + 4))
                e2s = datetime.fromtimestamp(e2, tz=timezone.utc).strftime("%b %d")
                res2 = chain(tkr, e2)
                calls2 = {c["strike"]: c for c in res2["options"][0]["calls"]}
                cstrikes = sorted(calls2)
                kb = _nearest(cstrikes, spot, below=False)
                kt = _nearest(cstrikes, hp["price"], below=False)
                if kb and kt and kt > kb:
                    deb = _mid(calls2[kb]) - _mid(calls2[kt])
                    w = kt - kb
                    if deb > 0:
                        trades.append({
                            "kind": "BOUNCE",
                            "label": f"Buy {e2s} ${kb:g}/${kt:g} call spread",
                            "detail": f"debit ≈${deb:.2f} (${deb*100:.0f}) · "
                                      f"max value ${w*100:.0f} · "
                                      f"ROI {max(0,(w-deb))/deb*100:.0f}% if "
                                      f"${hp['price']} prints by {hp['date']}",
                            "thesis": f"targets the projected {hp['date']} rebound high",
                            "exp": e2s, "strikes": [kb, kt], "premium": round(deb, 2)})
        except Exception as e:
            trades.append({"kind": "NOTE", "label": "No listed chain on this feed",
                           "detail": str(e)[:80], "thesis": "", "exp": "",
                           "strikes": [], "premium": 0})
        out[tkr] = {"asof": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "spot": round(spot, 2), "trades": trades}
    return out


if __name__ == "__main__":
    dall = json.loads(open("data.js", encoding="utf-8").read()
                      .replace("const DATA_ALL = ", "").rstrip().rstrip(";"))
    t = build_trades(dall)
    for tkr, v in t.items():
        print(f"\n===== {tkr}  spot {v['spot']} =====")
        for tr in v["trades"]:
            print(f" {tr['kind']:8} {tr['label']}  {tr['detail']}")
