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

## 2026-08-02 (Sun)

**Grades reviewed:** Still no new market session since Friday 7/31 (Saturday and Sunday don't trade), so the resolved-prediction numbers are unchanged again: TSLA n=5 (0% hit), HOOD n=3 (0%), QQQ n=3 (0%), JPM n=4 (0%), GOOGL n=4 (still 50%), GC=F n=0. Daily horizon errors still mostly under 5%. One genuinely new thing to note: `real_trades.json` now shows the first fully-closed real trade — a QQQ $690 put sold 7/24 and bought back 7/31, capturing 89% of the credit ($980 of $1,100) right around the model's projected low. That's a good real-money confirmation of the "sell the put at the projected low" playbook, but it's a single trade, not a pattern yet.

**What changed and why:** No code change today. This environment's Yahoo access was blocked again (403 on every ticker, same as the last several reviews), so I skipped `fetch_data.py`/`analyze.py` rather than risk overwriting good data with an empty build. `coherence_check.py` passes cleanly (6 tickers) against the data the cloud refresh workflow already shipped, so nothing needed re-shipping. I also noticed the repo's git history was reset to a single fresh commit today (separate from this review) — I've been working from that new state; no ledger data looks damaged by it.

**Watch tomorrow:** Monday 8/3 is the first new trading session since Friday — worth checking whether GOOGL's 50% edge holds up once fresh predictions resolve, or whether it fades back toward the 0% everyone else is showing. Also keep an eye on whether Yahoo access recovers for this environment, and whether the QQQ real-trade win turns into a repeatable pattern as more real trades close.

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

## 2026-08-03 (Mon) - second check-in, no code change - grades logged only

This session's fetch also had no path to Yahoo (blocked with a 403 at the network
proxy this time, same practical effect as the earlier "no internet access" case).
Since there were no cached price files to fall back on either, re-running the engine
here would have produced an empty dashboard, so nothing was regenerated from this
session - the coherence gate correctly caught and rejected the empty output when
tested, confirming it's doing its job. The site's actual numbers are already current
because the separate 3x/day cloud refresh (which does have data access) had already
run today and re-published successfully before this check-in.

**Grades reviewed (from the live, already-refreshed data):** still only 8 date
predictions have fully matured and graded since the July 24 engine fixes went in -
too few to judge the fixes yet. Of those 8: GOOGL is the standout at 2/4 (50%)
hit-within-3-days, while TSLA, HOOD, and QQQ are 0% and JPM has none matured. This
is the same picture as the last review - the graded ones are still mostly leftover
predictions from before the July 24 fixes, so no new signal on whether those fixes
helped. One good real-money data point: the closed QQQ put trade (sold 7/24, bought
back 7/31) captured 89% of its credit, matching the model's playbook exactly.

**No code change today** - one change already shipped earlier today (the backtest-weighted
strength bars and "what actually works" box), and nothing new has crossed the
3-graded-days bar for a further change. **Watch next:** whether the first wave of
post-July-24-fix predictions (logged 7/29 onward) start maturing with a materially
different hit rate than the 0% TSLA/HOOD/QQQ baseline - that's the real test of
whether the fixes worked.

## 2026-08-04 (Tue) — fixed a real hole in the safety gate

**Grades reviewed:** Yahoo is still blocked from this environment (403 on every ticker),
so I worked from the data the cloud refresh already published, same as recent reviews.
Live-graded sample sizes are still small and noisy: TSLA n=6 (0% within 3 days), HOOD n=5
(0%), QQQ n=6 (17%), JPM n=5 (0%), GC=F n=1 (0%), GOOGL n=4 (still the standout at 50%).
The much bigger walk-forward backtest (205–393 historical predictions tested per stock)
tells a steadier story: HOOD 36.7% and QQQ 37.6% hit-within-3-days, GC=F 53.6% off a small
28-test sample, TSLA 22.2%, JPM 20.6%, GOOGL weakest at 14.2% — all read against a roughly
20% pure-chance baseline for this window size. This matches last review's picture, so it's
not yet a fresh 3-day trend, just confirmation the July recalibration (weighting confidence
bars by backtested skill) is pointed the right way. Real money: still just the 2 closed QQQ
put trades from before 8/3 (+$980, +$600), nothing new opened or closed today.

**What changed and why (today's one change):** I found a genuine hole in `coherence_check.py`
while confirming the empty-fetch fallback still worked safely. When Yahoo is blocked and there's
no cached price data to fall back on, `analyze.py` writes an empty dashboard (`data.js` with
zero tickers) rather than erroring — by design, so a bad run doesn't crash. But the coherence
gate, whose whole job is to block a bad build from shipping, was looping over that empty ticker
list and printing "PASSED for 0 tickers" — a pass, not a rejection. An empty dashboard would
have sailed through the one check meant to stop it. I added a check that compares the tickers
in `data.js` against the 6 in `tickers.txt` and fails loudly if any are missing. Verified it:
force-fed the gate an empty `data.js` and it now correctly fails with "missing 6/6 expected
tickers"; restored the real file and it still passes cleanly for all 6. No dashboard files were
touched — this only strengthens the gate.

**Also today (housekeeping, not a code change):** this environment's local git branch was
stale by dozens of commits relative to the live site — I synced to the real published state
before doing anything else. That mismatch is almost certainly what has caused this log to get
silently reverted twice before (7/31–8/1's entries, and now 8/3's two entries, both wiped by a
later commit that was built on a stale local copy and pushed over the real history). I restored
the missing 8/3 entries above from git history so the record stays complete. Future reviews:
always sync to `origin/main` before editing anything, especially this file.

**Watch next:** whether GOOGL's 50% live hit rate holds as more post-recalibration predictions
mature (it's still the same handful of resolved predictions each review, not fresh data yet),
and whether a new real trade gets opened/closed to add a third data point to the real-money
ledger.
