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

## 2026-08-03 (Mon) - recalibrate: weight confluence by backtested skill + lead with proven edges

**Change 1 - the "strength" bars now reflect the walk-forward backtest, not just today's
confluence.** Each stock's plus-or-minus-3-day hit rate from the 1,558-prediction backfill
test now scales its forecast confidence: HOOD (backtests at 36.7%, well above the ~20%
chance level) gets its strength bars scaled up toward the top of the scale; GOOGL (14.2%,
near/below chance) gets scaled down. Nothing about which dates or prices are predicted
changed - only how confident the bars say to be. The prediction section also now states
each stock's own backtested hit rate in plain text, so it's clear the confidence isn't a
made-up number.

**Change 2 - a new "What actually works" box now sits at the top of the page,** above
the date predictions, for every stock. It shows the three best-evidenced things this
project has actually proven: which session (overnight vs. regular hours) has the real
edge, the nearest real support/resistance levels, and the backtested plus-or-minus-3-day
accuracy - plus any real trades placed, when there are some. The date/time forecasts are
still on the page, just lower down, since they're the weaker, more speculative part of
the system.

**How this was tested:** this session had no live internet access to fetch fresh stock
prices (sandboxed environment), so the changes couldn't be run against real data here.
Instead, the new code was smoke-tested end to end against synthetic stand-in price data
for two stocks (one that backtests well, one at chance level) - it ran cleanly, the
strength-bar math behaved exactly as intended, and the coherence check passed. The new
"what works" box was also checked against the real, currently-live dashboard data and
renders correctly. The live dashboard files (data.js, index.html, etc.) will pick up
real numbers automatically on the next scheduled hourly refresh, which does have data
access and re-runs the same coherence check as a safety gate before publishing.
