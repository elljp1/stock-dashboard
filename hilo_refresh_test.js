/* Regression test: the daily high/low panel refreshes with the rest of the page.
 *
 * Builds the page from dashboard.html + data.js with a chosen initial HILO, then
 * presses Update with fetch stubbed to return data.js carrying a new HILO payload,
 * and checks what the primary panel shows. Synthetic forecasts only.
 */
const fs = require("fs");
const { JSDOM } = require("jsdom");

const template = fs.readFileSync("dashboard.html", "utf8");
const dataRaw = fs.readFileSync("data.js", "utf8").split("\n").filter(l => !l.startsWith("const HILO = ")).join("\n");
// HILO is written last, as analyze.py does
const withHilo = h => dataRaw.replace(/\n*$/, "\n") + "const HILO = " + JSON.stringify(h) + ";\n";

function ctx() {
  return new Proxy({}, { get(_t, k) {
    if (k === "measureText") return () => ({ width: 10 });
    if (k === "canvas") return { width: 300, height: 150 };
    if (k === "getImageData") return () => ({ data: new Uint8ClampedArray(4) });
    return () => ({ addColorStop() {} });
  }, set() { return true; } });
}

function side(price, time) {
  return { price, lo: price - 2, hi: price + 2, time, pBar: 0.3, topBins: [{ time, p: 0.3 }],
           window: { centre: "10:30", p60: 0.6, p30: 0.3 } };
}
function rec(kind, session, extra) {
  return Object.assign({ kind, session, model: "hilo-1", lastBar: session + " 09:45",
    issuedAt: new Date().toISOString(), dataCutoff: new Date().toISOString(),
    high: side(110, "09:30"), low: side(100, "14:00") }, extra || {});
}
function payload(ticker, session, slot, extra) {
  return Object.assign({ generatedAt: new Date().toISOString(), model: "hilo-1", targetSession: session,
    latest: { [ticker]: slot }, status: {}, ledger: { ok: true, records: 2 }, method: "test" }, extra || {});
}

function load(initialHilo) {
  const html = template.replace('<script src="data.js"></script>', "<script>" + withHilo(initialHilo) + "</script>");
  let next = null;
  const dom = new JSDOM(html, { runScripts: "dangerously", pretendToBeVisual: true, url: "https://example.test/",
    beforeParse(w) {
      w.HTMLCanvasElement.prototype.getContext = () => ctx();
      w.fetch = async () => ({ ok: true, status: 200, text: async () => next });
    } });
  return { dom, serve: t => { next = t; } };
}

const wait = ms => new Promise(r => setTimeout(r, ms));
async function update(page, text) {
  page.serve(text);
  page.dom.window.document.getElementById("btnUpdate").click();
  for (let i = 0; i < 40; i++) {
    await wait(50);
    if (!page.dom.window.document.getElementById("btnUpdate").disabled) break;
  }
  return page.dom.window.document.getElementById("hiloHead").textContent;
}

(async () => {
  const fails = [];
  const check = (cond, msg) => { if (!cond) fails.push(msg); };
  const page = load(null);
  await wait(300);
  const t = page.dom.window.eval("CUR");
  let head = page.dom.window.document.getElementById("hiloHead").textContent;
  check(/appear after the next scheduled run/.test(head), "initial null state not shown: " + head);

  // 1. recovery from an initial null, then a newer intraday checkpoint
  head = await update(page, withHilo(payload(t, "2026-10-09", { premarket: rec("premarket", "2026-10-09"),
    intraday: rec("intraday", "2026-10-09", { checkpoint: 4, lastBar: "2026-10-09 10:15",
      observed: { high: 109, highTime: "09:30", low: 101, lowTime: "09:45", bars: 4 } }) })));
  check(/checkpoint 4/.test(head), "checkpoint 4 not shown after refresh: " + head);
  head = await update(page, withHilo(payload(t, "2026-10-09", { premarket: rec("premarket", "2026-10-09"),
    intraday: rec("intraday", "2026-10-09", { checkpoint: 8, lastBar: "2026-10-09 11:15",
      observed: { high: 109, highTime: "09:30", low: 101, lowTime: "09:45", bars: 8 } }) })));
  check(/checkpoint 8/.test(head) && !/checkpoint 4/.test(head), "refreshed checkpoint not shown: " + head);

  // 2. a new target session replaces the old one
  head = await update(page, withHilo(payload(t, "2026-10-12", { premarket: rec("premarket", "2026-10-12") })));
  check(/2026-10-12/.test(head) && !/2026-10-09 \(/.test(head), "new target session not shown: " + head);

  // 3. an invalid payload is rejected and the previous forecast stays
  head = await update(page, withHilo({ generatedAt: "not a date" }));
  check(/2026-10-12/.test(head), "invalid payload replaced the panel: " + head);
  const st = page.dom.window.document.getElementById("updStatus").textContent;
  check(/previous data retained/.test(st), "invalid payload not reported: " + st);

  // 4. a failure payload hides the forecast
  head = await update(page, withHilo({ failed: { at: new Date().toISOString(), reason: "boom" }, stale: true,
    generatedAt: new Date(Date.now() - 3600e3).toISOString(), targetSession: "2026-10-12", latest: {} }));
  check(/UNAVAILABLE/.test(head) && /boom/.test(head), "failure payload not shown: " + head);
  check(page.dom.window.document.getElementById("hiloCards").innerHTML === "", "cards still shown after failure");

  if (fails.length) { console.error("HILO REFRESH TEST FAILED:\n - " + fails.join("\n - ")); process.exit(1); }
  console.log("hilo refresh test OK: null recovery, checkpoint refresh, new session, invalid rollback, failure state");
  process.exit(0);
})().catch(e => { console.error(e); process.exit(1); });
