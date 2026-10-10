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
  check(d.querySelectorAll("#gTicker option").length === Object.keys(ALL).length, "stock picker must list every stock");
  check(d.querySelectorAll("#gPeriod button").length === 4, "period picker must offer D W M Y");
  const order = ["gTop", "gChartWrap", "gRes", "gMeta"].map(id => d.getElementById(id));
  check(order.every((el, i) => i === 0 || !!(order[i - 1].compareDocumentPosition(el) & w.Node.DOCUMENT_POSITION_FOLLOWING)), "order must be top bar, chart, results, meta");
  const shownText = d.getElementById("glance").textContent.replace(/\s+/g, " ").replace(/<[^>]*>/g, "");
  const visible = shownText.length - d.getElementById("gTicker").textContent.length;   // picker options are collapsed
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
    check(v.fc.filter(p => p.src === "turn").every(p => p.date > v.S && p.date <= v.span[1]), per + ": turns outside the selected period");
    check(v.fc.filter(p => p.src === "turn").length <= 5, per + ": more than five turns");
    if (per === "D") check(v.fc.every(p => p.src === "day"), "day view must plot only the day forecast");
    if (per === "M") check(/so far/.test(res.textContent) && /123\.45/.test(res.textContent) && /proj\. pt/.test(res.textContent), "month view must show projected points and the separate so-far actual");
    if (per !== "D") check(/partial: day \+ \d+ turn/.test(d.getElementById("gAsOf").textContent), per + " must say the horizon is partial");
  }
  // Day, order resolved: each side gets its own time
  dom = load(hiloFor(true)); d = dom.window.document;
  d.querySelector('#gPeriod button[data-p="D"]').click();
  res = d.getElementById("gRes");
  const whens = [...res.querySelectorAll(".when")].map(e => e.textContent.trim());
  check(whens[0] === "9:30a" && whens[1] === "3:45p" && !/order \?/.test(res.textContent), "resolved order must time high and low: " + whens);
  if (fails.length) { console.error("UI LAYOUT TEST FAILED:\n - " + fails.join("\n - ")); process.exit(1); }
  console.log("ui layout test OK: chart + compact results only, D/W/M/Y share one source, actuals separate, honest timing");
  process.exit(0);
}, 400);
