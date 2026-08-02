# Improvements Log — Stock Timing Dashboard

Plain-English record of every review: what the grades said, what changed, and why.

## 2026-07-25 (Sat) — Friday review, run manually with Claude

**Grades so far (first matured batch):** 7 predictions graded, 1 hit within ±2 days (GOOGL).
TSLA 0/3, JPM 0/2, HOOD 0/1 — all from the earliest engine (7/9–7/14, before the
volatility caps, level-snapping, and ordering fixes), and spanning two earnings crashes.
Typical price miss on graded calls: 7–9%.

**Where the system IS working:** price levels. QQQ's predicted $685.01 low printed at
$684.86 on the predicted date (Fri 7/24) — third touch of that zone. JPM's $351.24
resistance target was exceeded the same day ($353.37 high). GOOGL's $322.72 low target
hit within 0.2% on 7/23. Dates remain the weak leg; levels are the strong one.

**Trade-sheet grading (7/23 BOUNCE "lotto" spreads):** JPM $347.5/$352.5 call spread
finished Friday above its top strike (on track for +124%) — the only bounce bet aligned
with its trend. TSLA/HOOD/QQQ bounce spreads died betting on a turn mid-crash.

**Changes made this cycle (Fri 7/24–Sat 7/25):**
1. Each support/resistance level may be used only once per prediction chain (fixes
   duplicate price targets on predictions 2&4, 3&5).
2. BOUNCE trades now require confirmation: enter only after price reverses +3% off the
   low — never on the date alone. Lesson graded from the 7/23 sheet.
3. Crash-regime cap widening (targets stretch with drawdown) — added 7/23 after TSLA
   blew through its calm-market target.

**No further engine changes today** — Saturday, no new market data; changes above need
live grading before more tuning (avoid overfitting to one crash week).

**Watch next:** Monday 7/27 is the predicted-low date for TSLA ($311), HOOD ($94),
QQQ ($684 retest), gold ($3,975). First clean test of the fixed engine. Earnings-date
overlay remains the top queued improvement (both crash misses were earnings gaps).

## 2026-07-30

**Grades reviewed:** Looked at the trackRecord and horizonGrades for all 6 tickers (TSLA, HOOD, QQQ, JPM, GOOGL, GC=F). Hit rates on exact-date predictions are still low across the board (mostly 0%, GOOGL best at 50% on just 4 resolved calls) — but the sample sizes are tiny (3-5 resolved predictions per ticker since the ledger started 2026-07-09), so this is too early to call a real pattern and doesn't warrant a weight change yet. Daily horizon high/low error percentages look reasonable (mostly under 5%). Open option trade cards (TSLA, HOOD, etc.) haven't reached expiration yet, so nothing to grade there.

**What changed and why:** In this run, Yahoo's data API was blocked for this environment (403 Forbidden on every ticker), and — unlike I expected — the repo doesn't actually keep a committed fallback copy of the price CSVs (they're gitignored), so `analyze.py` had nothing to work from and wrote out a completely empty dashboard (`DATA_ALL = {}`). I did NOT commit that broken output. Testing it against `coherence_check.py` turned up a real bug: the "must-pass" gate silently reports "PASSED for 0 tickers" on an empty dataset instead of failing. I fixed that with a one-line check so a data outage can never slip through the gate looking like a clean, valid build. Verified the fix: it now fails on an empty `DATA_ALL` and still passes cleanly on today's real data (6 tickers). No other code was touched; the live site's data is untouched from today's earlier successful cloud refresh (21:40 ET).

**Watch tomorrow:** Keep tracking hit2/hit3 rates as more predictions resolve — GOOGL's methods (Gann/Fib/Hurst) are doing best so far, TSLA/HOOD/QQQ/JPM chains are mostly missing their target dates. If that split holds for a few more days, it may be worth revisiting per-method weighting. Also confirm the cloud refresh workflow (which has real internet access) continues to run cleanly, since this environment's own fetch was blocked today.

## 2026-07-31

**Grades reviewed:** Checked the trackRecord and horizonGrades for all 6 tickers again. Same shape as yesterday, one more day resolved: TSLA (n=5, 0% hit rate), HOOD (n=3, 0%), QQQ (n=3, 0%), JPM (n=4, 0%), GOOGL (n=4, still 50%), GC=F (no resolved predictions yet, ledger only started 2026-07-22). Daily horizon high/low error percentages remain reasonable (mostly under ~5%, a couple in the 6-7% range). No option trade cards have hit their expiration date yet (earliest is Aug 21), so nothing to grade there.

**What changed and why:** No code change today. Yahoo's data API was blocked again for this environment (403 Forbidden on every ticker, same as yesterday), so I skipped running `fetch_data.py`/`analyze.py` locally rather than risk overwriting good data with an empty build. The live dashboard's `data.js` was already refreshed a few hours earlier by the cloud workflow (2026-07-31, 5:36 PM ET) and passes the coherence gate cleanly (6 tickers) as-is, so nothing needed fixing or re-shipping. The GOOGL-vs-everyone-else split is now 2 days running, but the sample sizes are still only 3-5 resolved predictions per ticker, so per-method weighting still isn't warranted yet — the discipline calls for 3+ days of a persistent pattern before touching that logic.

**Watch tomorrow:** One more day of GOOGL outperformance (currently 50% vs. 0% elsewhere) would hit the 3-day bar — worth a closer look at whether Gann/Fib/Hurst are systematically better calibrated for GOOGL specifically, or whether it's just luck on a 4-sample ledger. Also keep an eye on whether this environment's Yahoo access stays blocked or recovers, and confirm the cloud refresh workflow keeps running on its own schedule regardless.

## 2026-08-01 (Sat)

**Grades reviewed:** No new market session since Friday 7/31 (today is Saturday), so the numbers are unchanged from yesterday's review: TSLA n=5 (0% hit), HOOD n=3 (0%), QQQ n=3 (0%), JPM n=4 (0%), GOOGL n=4 (still 50%), GC=F n=0 (ledger too new). Daily horizon errors still mostly under 5%. Nothing new to grade on the trade-card sheet either — same reason.

**What changed and why:** No engine change today. Earlier today a prior run of this review added a "full transparency" history feature (analyze.py now surfaces every logged prediction, resolved or not, plus real trade fills) — that's already this cycle's one code change, so I made no second one. While checking that commit I found it had accidentally wiped this log's 7/30 and 7/31 entries when it rewrote the file (replaced with an unrelated older 7/25 entry, losing two real days of history). I restored the missing entries above so the review record stays complete — this is a data-integrity fix to the audit trail, not a change to the prediction engine. I spot-checked predictions_log.json and trades_log.json from that same commit for similar damage: no resolved grades (actualDate/actualPrice/hit2/hit3) were altered, only forward-looking unresolved targets were refreshed, so those ledgers look intact.

**Watch tomorrow:** GOOGL's 50% vs. everyone else's 0% has now held for 3 straight reviews (7/30, 7/31, 8/1) — but note it's the *same* 4 resolved predictions counted each time, not new data, so this still isn't a fresh 3-day trend and doesn't yet justify a per-method weight change. Revisit once new GOOGL predictions actually resolve. Also worth a quick check next review that the new history feature keeps writing to improvements_log.md correctly (append, not overwrite).
