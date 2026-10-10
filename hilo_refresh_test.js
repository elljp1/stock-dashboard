/* The high/low results refresh with the rest of the page data: validated first,
 * older or invalid payloads rejected, failures shown as unavailable. Synthetic forecasts only. */
const fs = require("fs");
const { JSDOM } = require("jsdom");

const template = fs.readFileSync("dashboard.html", "utf8");
const dataRaw = fs.readFileSync("data.js", "utf8").split("\n").filter(l => !l.startsWith("const HILO = ")).join("\n");
const withHilo = h => dataRaw.replace(/\n*$/, "\n") + "const HILO = " + JSON.stringify(h) + ";\n";   // HILO last, as analyze.py writes it
const ctx = () => new Proxy({}, { get(_t, k) { return k === "measureText" ? () => ({ width: 10 }) : () => {}; }, set() { return true; } });
let clock = Date.now();
const stamp = () => new Date(clock += 60000).toISOString();
const side = (price, time) => ({ price, lo: price - 2, hi: price + 2, time, pBar: 0.3, window: { centre: "10:30", p60: 0.6 } });
const rec = (kind, session, hi, extra) => Object.assign({ kind, session, model: "hilo-2", lastBar: session + " 09:45",
  issuedAt: stamp(), dataCutoff: stamp(), high: side(hi, "09:30"), low: side(hi - 10, "15:45"),
  timing: { early: { time: "09:30", pBar: 0.6, p60: 0.8 }, late: { time: "15:45", pBar: 0.2, p60: 0.4 }, pHighFirst: 0.5, resolved: false } }, extra || {});
const payload = (t, session, slot) => ({ generatedAt: stamp(), model: "hilo-2", targetSession: session,
  latest: { [t]: slot }, ledger: { ok: true, records: 2 }, periods: {}, history: [] });

(async () => {
  const fails = [], check = (c, m) => { if (!c) fails.push(m); };
  let next = null;
  const html = template.replace('<script src="data.js"></script>', "<script>" + withHilo(null) + "</script>");
  const dom = new JSDOM(html, { runScripts: "dangerously", pretendToBeVisual: true, url: "https://example.test/",
    beforeParse(w) { w.HTMLCanvasElement.prototype.getContext = () => ctx(); w.fetch = async () => ({ ok: true, status: 200, text: async () => next }); } });
  const w = dom.window, d = w.document;
  await new Promise(r => setTimeout(r, 200));
  const t = w.eval("CUR");
  const update = async txt => { next = txt; await d.getElementById("gUpd").onclick(); };
  const shown = () => Number(d.querySelector('#gRes [data-side="high"]') ? d.querySelector('#gRes [data-side="high"]').dataset.price : NaN);
  check(/No forecast/.test(d.getElementById("gRes").textContent), "initial null state not shown");

  await update(withHilo(payload(t, "2026-10-09", { intraday: rec("intraday", "2026-10-09", 110, { checkpoint: 4 }) })));
  check(shown() === 110 && /live/.test(d.getElementById("gAsOf").textContent), "first forecast not shown after recovery from null");
  await update(withHilo(payload(t, "2026-10-09", { intraday: rec("intraday", "2026-10-09", 111, { checkpoint: 8 }) })));
  check(shown() === 111, "refreshed checkpoint not shown");
  await update(withHilo(payload(t, "2026-10-12", { premarket: rec("premarket", "2026-10-12", 120) })));
  check(shown() === 120 && /Mon, 10\/12/.test(d.getElementById("gAsOf").textContent), "new target session not shown: " + d.getElementById("gAsOf").textContent);
  await update(withHilo({ generatedAt: "not a date" }));
  check(shown() === 120 && d.getElementById("gUpd").className === "bad", "invalid payload replaced the forecast or was not flagged");
  await update(withHilo({ failed: { at: stamp(), reason: "boom" }, stale: true, generatedAt: stamp(), targetSession: "2026-10-12", latest: {} }));
  check(/unavailable/.test(d.getElementById("gRes").textContent) && /unavailable/.test(d.getElementById("gAsOf").textContent), "failure payload not shown");

  if (fails.length) { console.error("HILO REFRESH TEST FAILED:\n - " + fails.join("\n - ")); process.exit(1); }
  console.log("hilo refresh test OK: null recovery, checkpoint refresh, new session, invalid rollback, failure state");
  process.exit(0);
})().catch(e => { console.error(e); process.exit(1); });
