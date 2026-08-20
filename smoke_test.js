/* Runtime smoke test: actually LOAD the built page and prove it boots.
 *
 * The esprima gate catches syntax errors, but twice a runtime error has
 * taken the live page down (a literal newline in a string; an open trade's
 * null P&L crashing renderAll before buildSectionTabs ran). This executes
 * index.html in jsdom and asserts the page reached its interactive state.
 *
 * Fails ONLY on the two things that define "page is broken for the user":
 * the section tab bar didn't build, or the ticker data didn't load. Anything
 * else is printed as a warning - jsdom is not a real browser, and a false
 * failure here blocks every cloud refresh (which happened on 8/19-8/20).
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
    // pending-forever promise: no network in jsdom, and an instant rejection
    // would surface phantom errors the real page never shows
    window.fetch = () => new Promise(() => {});
    window.addEventListener("error", (e) =>
      errors.push(String((e.error && e.error.stack) || e.message)));
  },
});

setTimeout(() => {
  const d = dom.window.document;
  const btns = d.querySelectorAll("#sectionTabs button").length;
  // DATA_ALL is a top-level const - it lives in the global lexical scope, NOT
  // on window. window.eval shares that scope; window.DATA_ALL is undefined.
  let tickers = 0;
  try {
    tickers = Number(dom.window.eval(
      'typeof DATA_ALL === "undefined" ? 0 : Object.keys(DATA_ALL).length'));
  } catch (e) { errors.push("eval: " + e.message); }

  for (const e of errors) console.log("warning (non-fatal): " + e.slice(0, 300));
  const probs = [];
  if (btns < 4)
    probs.push(`section tabs did not build (${btns} buttons) - a script crashed before buildSectionTabs()`);
  if (tickers < 10) probs.push(`DATA_ALL has only ${tickers} tickers`);
  if (probs.length) {
    console.error("SMOKE TEST FAILED - the page would be broken for the user:\n - " + probs.join("\n - "));
    process.exit(1);
  }
  console.log(`smoke test OK: ${btns} tab buttons, ${tickers} tickers`);
  process.exit(0);
}, 1500);
