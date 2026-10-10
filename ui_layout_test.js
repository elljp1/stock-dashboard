/* Main screen: chart + compact high/low results only, one shared source per period.
 * Synthetic forecast, real page data. */
const fs = require("fs");
const { JSDOM } = require("jsdom");

const data = fs.readFileSync("data.js", "utf8").split("\n").filter(l => !l.startsWith("const HILO = ")).join("\n");
const ALL = new Function(data + ";return DATA_ALL;")();
const T = Object.keys(ALL)[0];
const side = (price, time) => ({ price, lo: price - 2, hi: price + 2, time, pBar: 0.3, window: { centre: "10:30", p60: 0.6 } });
function hiloFor(resolved) {
  return { generatedAt: new Date().toISOString(), model: "hilo-2", targetSession: "2026-10-12",
    latest: { [T]: { premarket: { kind: "premarket", session: "2026-10-12", model: "hilo-2", lastBar: "2026-10-09 15:45",
      issuedAt: new Date().toISOString(), dataCutoff: "2026-10-09T16:00:00-04:00",
      high: side(110, resolved ? "09:30" : "09:30"), low: side(100, resolved ? "15:45" : "09:30"),
      timing: { early: { time: "09:30", pBar: 0.6, p60: 0.8 }, late: { time: "15:45", pBar: 0.2, p60: 0.4 },
                pHighFirst: resolved ? 0.7 : 0.5, resolved } } } },
    periods: { [T]: { W: { start: "2026-10-12", end: "2026-10-16", high: null, low: null },
                      M: { start: "2026-10-01", end: "2026-10-31", high: { price: 123.45, date: "2026-10-06" }, low: { price: 90.5, date: "2026-10-01" } },
                      Y: { start: "2026-01-01", end: "2026-12-31", high: { price: 150, date: "2026-03-02" }, low: { price: 60, date: "2026-07-29" } } } },
    ledger: { ok: true, records: 1 }, history: [] };
}
const ctx = () => new Proxy({}, { get(_t, k) { return k === "measureText" ? () => ({ width: 10 }) : () => {}; }, set() { return true; } });
function load(hilo) {
  const html = fs.readFileSync("dashboard.html", "utf8")
    .replace('<script src="data.js"></script>', "<script>" + data + "\nconst HILO = " + JSON.stringify(hilo) + ";</script>");
  return new JSDOM(html, { runScripts: "dangerously", pretendToBeVisual: true, url: "https://example.test/",
    beforeParse(w) { w.HTMLCanvasElement.prototype.getContext = () => ctx(); w.fetch = () => new Promise(() => {}); } });
}
const fails = [], check = (c, m) => { if (!c) fails.push(m); };
setTimeout(() => {
  let dom = load(hiloFor(false)), w = dom.window, d = w.document;
  for (const id of ["detailsAll", "predTable", "timingPanel", "weekPanel", "sectionTabs", "hiloCards", "legacy"])
    check(!d.getElementById(id), "superseded element still present: " + id);
  // every followed stock and its price visible at once as one-click buttons; no selector to open
  check(!d.querySelector("select"), "stocks must not sit behind a selector/dropdown");
  const chips = [...d.querySelectorAll("#gTk button[data-t]")];
  check(chips.length === Object.keys(ALL).length, "every stock needs its own button: " + chips.length);
  check(chips.every(b => /\$[\d,]+\.\d\d/.test(b.textContent) && b.textContent.includes(b.dataset.t === "GC=F" ? "GOLD" : b.dataset.t)), "each button shows its stock and price");
  check(chips.filter(b => b.classList.contains("on")).length === 1, "exactly one stock is selected");
  check(d.querySelectorAll("#gPeriod button").length === 4, "period picker must offer D W M Y");
  const order = ["gTk", "gTop", "gChartWrap", "gRes", "gMeta"].map(id => d.getElementById(id));
  check(order.every((el, i) => i === 0 || !!(order[i - 1].compareDocumentPosition(el) & w.Node.DOCUMENT_POSITION_FOLLOWING)), "order must be stocks, controls, chart, results, meta");
  const shownText = d.getElementById("glance").textContent.replace(/\s+/g, " ").replace(/<[^>]*>/g, "");
  const visible = shownText.length - d.getElementById("gTk").textContent.length;   // the stock list is a glanceable grid
  check(visible < 260, "main screen text too long: " + visible);
  // Day, order unresolved: no time attached to high or low; the early/late pair is shown on its own
  let res = d.getElementById("gRes");
  check([...res.querySelectorAll(".when")].slice(0, 2).every(e => e.textContent.trim() === ""), "unresolved order must not put times on high/low");
  check(/1st ≈9:30a · 2nd ≈3:45p/.test(res.textContent) && /order \?/.test(res.textContent), "early/late pair not shown: " + res.textContent);
  // every period: results equal the plotted points; actuals labelled "so far" and never used as the forecast
  for (const per of ["D", "W", "M", "Y"]) {
    d.querySelector(`#gPeriod button[data-p="${per}"]`).click();
    const v = w.__gView;
    for (const s of ["high", "low"]) {
      check(Number(res.querySelector(`[data-side="${s}"]`).dataset.price) === v[s].price, per + " " + s + " result differs from the plotted point");
      check(v.fc.includes(v[s]) && v[s].src !== "set", per + " " + s + " result must be a plotted forecast point");
    }
    const turns = v.fc.filter(p => p.src === "turn"), supported = ALL[T].predictions.filter(p => p.isoDate > v.lastClose).slice(0, 5);
    check(turns.every(p => p.date > v.lastClose && (per === "D" || p.date <= v.span[1])), per + ": turns outside the selected period");
    check(turns.every(p => supported.some(q => q.isoDate === p.date && q.price === p.price && q.type === p.type)), per + ": every turn must be a supported prediction");
    check(v.fc.filter(p => p.src === "turn").length <= 5, per + ": more than five turns");
    if (per === "D") {
      check(turns.length === supported.length, "day view must plot every supported future turn: " + turns.length + " of " + supported.length);
      check(v.high.src === "day" && v.low.src === "day", "day results must stay the day forecast, not a multi-day turn");
    }
    // the chart itself carries every prediction: same price as the summary, plus a time (D) or date (W/M/Y)
    const labs = w.__gLabels || [];
    check(labs.length === v.fc.length && v.fc.every(p => labs.some(l => l.point === p)), per + ": every plotted prediction needs a chart label");
    for (const l of labs) {
      check(l.text.startsWith("$" + l.point.price.toFixed(2)), per + ": label price differs from the point: " + l.text);
      if (per === "D" && l.point.src === "day") check(/ 9:30a\/3:45p\?$/.test(l.text), "unresolved day label must show the two-bar window with ?, not one exact time: " + l.text);
      else check(l.text.endsWith(" " + Number(l.point.date.slice(5, 7)) + "/" + Number(l.point.date.slice(8, 10))), per + ": label must carry its date: " + l.text);
    }
    check(labs.filter(l => l.main).length === 2, per + ": the two summary numbers must be the emphasised labels");
    if (per === "M") check(/so far/.test(res.textContent) && /123\.45/.test(res.textContent) && /proj\. pt/.test(res.textContent), "month view must show projected points and the separate so-far actual");
    if (per !== "D") check(/partial: day \+ \d+ turn/.test(d.getElementById("gAsOf").textContent), per + " must say the horizon is partial");
  }
  // Day, order resolved: each side gets its own time
  dom = load(hiloFor(true)); d = dom.window.document;
  d.querySelector('#gPeriod button[data-p="D"]').click();
  res = d.getElementById("gRes");
  const whens = [...res.querySelectorAll(".when")].map(e => e.textContent.trim());
  check(whens[0] === "9:30a" && whens[1] === "3:45p" && !/order \?/.test(res.textContent), "resolved order must time high and low: " + whens);
  const rl = Object.fromEntries((dom.window.__gLabels || []).filter(l => l.point.src === "day").map(l => [l.point.type, l.text]));
  check(rl.high === "$110.00 9:30a" && rl.low === "$100.00 3:45p", "resolved day labels must carry each side's time: " + JSON.stringify(rl));
  // one click on a stock button switches chart and results to it, every period
  {
    const all = Object.keys(ALL), other = all.find(t => t !== T);
    const dm = load(hiloFor(false)), dd = dm.window.document;
    for (const per of ["D", "W", "M", "Y"]) {
      dd.querySelector(`#gPeriod button[data-p="${per}"]`).click();
      for (const t of [other, T]) {
        dd.querySelector(`#gTk button[data-t="${t}"]`).click();
        check(dm.window.eval("CUR") === t, per + ": one click must select " + t);
        const on = [...dd.querySelectorAll("#gTk button.on")].map(b => b.dataset.t);
        check(on.length === 1 && on[0] === t, per + ": selected button must follow the click");
        check(dd.querySelectorAll("#gTk button[data-t]").length === all.length, per + ": buttons must stay after switching");
        const res = dd.getElementById("gRes").textContent;
        check(t === T ? /High/.test(res) : /No forecast yet/.test(res), per + " " + t + ": results did not switch: " + res);
      }
    }
  }
  if (fails.length) { console.error("UI LAYOUT TEST FAILED:\n - " + fails.join("\n - ")); process.exit(1); }
  console.log("ui layout test OK: chart + compact results only, D/W/M/Y share one source, predictions labelled on the chart, actuals separate, honest timing");
  process.exit(0);
}, 400);
