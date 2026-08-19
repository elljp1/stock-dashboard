/* Runtime smoke test: actually LOAD the built page and prove it comes up.
 *
 * The esprima gate catches syntax errors, but twice now a runtime error has
 * taken the page down (a literal newline in a string; an open trade's null
 * P&L crashing renderAll before buildSectionTabs ran). This test executes
 * index.html in jsdom and asserts the page reached its final, interactive
 * state. Canvas drawing is stubbed - chart pixels aren't the point here.
 */
const fs = require("fs");
const { JSDOM } = require("jsdom");

function makeCtx() {
  return new Proxy({}, {
    get(_t, k) {
      if (k === "measureText") return () => ({ width: 10 });
      if (k === "getImageData")
        return () => ({ data: new Uint8ClampedArray(4), width: 1, height: 1 });
      if (k === "createLinearGradient" || k === "createRadialGradient")
        return () => ({ addColorStop() {} });
      if (k === "canvas") return { width: 300, height: 150 };
      return () => {};
    },
    set() { return true; },
  });
}

const html = fs.readFileSync("index.html", "utf8");
const errors = [];
const dom = new JSDOM(html, {
  runScripts: "dangerously",
  pretendToBeVisual: true,
  url: "https://elljp1.github.io/stock-dashboard/",
  beforeParse(window) {
    window.HTMLCanvasElement.prototype.getContext = function () { return makeCtx(); };
    window.addEventListener("error", (e) =>
      errors.push(String((e.error && e.error.stack) || e.message)));
  },
});

setTimeout(() => {
  const d = dom.window.document;
  const btns = d.querySelectorAll("#sectionTabs button").length;
  const tickers = dom.window.DATA_ALL ? Object.keys(dom.window.DATA_ALL).length : 0;
  const probs = [];
  if (btns < 4)
    probs.push(`section tabs did not build (${btns} buttons) - a script crashed before buildSectionTabs()`);
  if (tickers < 10) probs.push(`DATA_ALL has only ${tickers} tickers`);
  for (const e of errors)
    if (!/getContext|canvas|crypto/i.test(e)) probs.push("page error: " + e.slice(0, 300));
  if (probs.length) {
    console.error("SMOKE TEST FAILED - the page would be broken for the user:\n - " + probs.join("\n - "));
    process.exit(1);
  }
  console.log(`smoke test OK: ${btns} tab buttons, ${tickers} tickers, ` +
              `${errors.length} canvas-stub errors suppressed`);
  process.exit(0);
}, 1200);
