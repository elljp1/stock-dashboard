/* Layout test for the simplified main view.
 *
 * Main view: chart + daily high/low cards, from the same forecast record.
 * Everything else (next five, week ahead, date picker, timing scorecard, trades,
 * accuracy, research) sits inside the collapsed Details section. Synthetic forecast.
 */
const fs = require("fs");
const { JSDOM } = require("jsdom");

const data = fs.readFileSync("data.js", "utf8").split("\n").filter(l => !l.startsWith("const HILO = ")).join("\n");
const side = (price, time) => ({ price, lo: price - 2, hi: price + 2, time, pBar: 0.3,
  topBins: [{ time, p: 0.3 }], window: { centre: "10:30", p60: 0.6, p30: 0.3 } });
const firstTicker = Object.keys(new Function(data + ";return DATA_ALL;")())[0];
const hilo = { generatedAt: new Date().toISOString(), model: "hilo-1", targetSession: "2026-10-12", kind: "premarket",
  latest: { [firstTicker]: { premarket: { kind: "premarket", session: "2026-10-12", model: "hilo-1",
    lastBar: "2026-10-09 15:45", issuedAt: new Date().toISOString(), dataCutoff: new Date().toISOString(),
    high: side(110, "09:30"), low: side(100, "15:45") } } }, status: {}, ledger: { ok: true, records: 1 },
  history: [], forwardByModel: {}, method: "test" };
const html = fs.readFileSync("dashboard.html", "utf8")
  .replace('<script src="data.js"></script>', "<script>" + data + "\nconst HILO = " + JSON.stringify(hilo) + ";</script>");
const ctx = () => new Proxy({}, { get(_t, k) {
  if (k === "measureText") return () => ({ width: 10 });
  if (k === "canvas") return { width: 300, height: 150 };
  return () => ({ addColorStop() {} });
}, set() { return true; } });
const dom = new JSDOM(html, { runScripts: "dangerously", pretendToBeVisual: true, url: "https://example.test/",
  beforeParse(w) { w.HTMLCanvasElement.prototype.getContext = () => ctx(); w.fetch = () => new Promise(() => {}); } });

setTimeout(() => {
  const d = dom.window.document, fails = [];
  const check = (c, m) => { if (!c) fails.push(m); };
  const details = d.getElementById("detailsAll");
  const inDetails = el => !!el && details.contains(el);
  check(details && !details.open, "Details section missing or open by default");
  check(!inDetails(d.getElementById("hiloCards")), "high/low cards are not in the main view");
  check(!inDetails(d.getElementById("chart")), "chart is not in the main view");
  check(d.getElementById("hiloCards").children.length === 4, "expected 4 high/low cards");
  for (const id of ["predTable", "dpInput", "timingPanel", "weekPanel", "sectionTabs"])
    check(inDetails(d.getElementById(id)), id + " should be inside Details");
  check([...d.querySelectorAll("[data-tab]")].every(inDetails), "a data-tab panel is outside Details");
  check(d.getElementById("sectionTabs").children.length > 0, "Details tabs did not build");
  const head = d.getElementById("hiloHead").textContent, tag = d.getElementById("chartTag").textContent;
  check(/2026-10-12/.test(head) && /2026-10-12/.test(tag), "chart and cards do not name the same session");
  check(!/confluence forecast/.test(tag), "legacy projected path still described on the chart");
  if (fails.length) { console.error("UI LAYOUT TEST FAILED:\n - " + fails.join("\n - ")); process.exit(1); }
  console.log("ui layout test OK: chart + 4 cards in main view, legacy panels behind Details, same session");
  process.exit(0);
}, 1500);
