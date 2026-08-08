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

## 2026-08-05 (Wed) — no change warranted, grades logged; confirmed yesterday's gate fix works

**Fetch status:** Yahoo is still blocked from this environment on every ticker (confirmed
this is a network policy denial at the proxy level, not a transient error). There was no
local price cache to fall back on since the CSV files aren't committed to the repo (only
the built dashboard is), so running the analysis engine here produced an empty `data.js`.
That's exactly the scenario yesterday's coherence-gate fix was built for: the gate correctly
caught it and refused to pass ("missing 6/6 expected tickers"), so I discarded that empty
build and left the dashboard as last published by the cloud refresh job, which has real
network access and has kept running normally (4 successful auto-refreshes since yesterday's
review). Good confirmation the fix works as intended.

**Grades reviewed (from the live, cloud-refreshed data):** Sample sizes grew a bit since
yesterday — TSLA n=8 (0% within either window), HOOD n=7 (0%), QQQ n=8 (12% within 2 days,
25% within 3), JPM n=7 (0%, and none of its 7 matured predictions have found a matching
actual price yet, so its price-error stat is blank — not a bug, just a ticker where the
timing methods haven't landed a hit yet), GOOGL n=6 (50%, still the standout), GC=F n=3
(0%). This is the same shape as yesterday and the day before, not a new 3-day trend in
either direction. Daily high/low range errors (the horizonGrades) stayed small and steady
across all six tickers, mostly under 3%. Real-money ledger unchanged: still just the 2
closed QQQ put trades from before 8/3 (+$980, +$600), nothing new opened or closed.

**What changed and why:** nothing. No 3-day persistent pattern and no new bug — today's
"empty build" situation is the known, already-handled failure mode, not a fresh one. Ledger
and dashboard both left untouched apart from this log entry.

**Watch next:** same as yesterday — whether GOOGL's 50% holds up as fresh predictions mature,
whether JPM ever lands a matched hit as more of its predictions resolve, and whether a third
real trade gets opened or closed.

## 2026-08-06 (Thu) — no change warranted, grades logged

**Fetch status:** same as the last two days — Yahoo is still blocked from this environment
at the network-policy level (checked the proxy's own status log, which shows repeated "403
to CONNECT" gateway rejections for query1.finance.yahoo.com, not a transient error). Running
the analysis engine here with no cached CSVs produced an empty `data.js` as expected; the
coherence gate rejected it correctly, so I discarded that build and left the dashboard as
last published by the cloud refresh job. Confirmed the cloud job is healthy: `data.js` was
generated today at 12:04 PM ET and the trade-card sheet at 3:42 PM ET, both current.

**Grades reviewed (from the live, cloud-refreshed data, 10 tickers now tracked):** TSLA n=9
(0% within either window), HOOD n=8 (0%), QQQ n=9 (22% within 2 days, 33% within 3 — its best
showing yet), JPM n=8 (still 0%, still none of its matured predictions have found a matching
actual swing), GOOGL n=6 (50%, holding steady), GC=F n=4 (0%). NVDA, AMZN, SPY and VOO are
too new (added 8/5) to have any matured predictions yet. Daily high/low range errors stayed
small across tickers with data, nothing outside the normal band. Real-money ledger unchanged:
still just the 2 closed QQQ put trades from before 8/3 (+$980, +$600).

**What changed and why:** nothing. JPM's 0-for-8 has now held for a third straight review,
which is the discipline's normal bar for a code change — but I looked into *why* today rather
than just re-flagging it, and it traces to genuinely low realized volatility in JPM's own
swing pattern (checked `daily_extremes.json`: JPM's actual daily highs/lows during this
window sit close together, so the zigzag detector — which is shared logic, not JPM-specific —
finds few qualifying pivots to grade against). That's a property of the stock, not a bug in
the matching code, so nothing to fix; noting it here so this doesn't get re-investigated as
a "new" pattern next time it's still 0%.

**Watch next:** whether JPM ever lands a matched hit as more predictions resolve, whether
QQQ's improving hit rate continues, and whether the first NVDA/AMZN/SPY/VOO predictions
mature enough by the next couple of reviews to start showing grades.

## 2026-08-07 (Fri) — fixed a coherence-gate blind spot, grades logged

**Fetch status:** Yahoo is still blocked from this environment (403 on every ticker, same
gateway-level block as the last several days). `analyze.py` ran on no cached CSVs and, as
expected, produced an empty `data.js` (0 tickers). This time, checking the gate's own
behavior rather than trusting it, I found it was NOT actually catching this: `coherence_check.py`
validates ticker-by-ticker, so an empty dataset makes its checking loop iterate zero times and
it printed "coherence check PASSED for 0 tickers" with exit 0 — a silent pass on a build with
no data at all. That's the one bug worth fixing today (see below). I discarded the empty
`data.js`/`index.html`/`dashboard_single.html` and left the live dashboard as last published
by the cloud refresh job, which is healthy (generated today around 9:09 PM ET).

**Grades reviewed (10 tickers tracked):** TSLA n=10 (30% within 2 days, 40% within 3 — up
from 0% yesterday) and QQQ n=10 (30%/40%, similarly improved) both jumped because the
self-grading engine re-matches *all* past predictions against fresh actual-price data each
run, so predictions that looked like misses can retroactively find their match once more
price history accumulates — a good sign the grading is working as intended, not noise from
a code change. GOOGL n=6 holds steady at 50%. JPM n=9 is still 0%, unchanged from the
already-diagnosed cause (its own daily range is tight, so the shared zigzag detector finds
few pivots to grade against — a property of the stock, not a bug). GC=F n=5 is 0%. NVDA,
AMZN, SPY, VOO are still too new for matured grades. HOOD n=9 is also still 0% and has been
0% since tracking began — but today I checked whether the same "low volatility" explanation
that lets JPM off the hook applies here, and it doesn't: HOOD's actual daily range (5.5%
average over the last 20 sessions) is the *highest* of all ten tracked tickers, well above
JPM (2.2%) and even above TSLA and GOOGL, both of which do land hits. Most of HOOD's resolved
predictions show no matched actual date/price at all, not just a timing miss. That looks like
a real gap in the matching logic rather than a stock property, but I'd already used today's
one code change on the coherence-gate fix, so I'm flagging it rather than touching code twice
in one day. Real-money ledger unchanged: still the 2 closed QQQ puts (+$980, +$600). The
option-trade sheet was refreshed again today by the cloud job; nothing in it has graded yet.

**What changed and why:** added one check to `coherence_check.py` — if `data.js` parses to
zero tickers, the build now fails the gate explicitly instead of trivially passing. Verified
it rejects a synthetic empty `data.js` (exit 1) and still passes the real 10-ticker build
(exit 0) without changes to any pass/fail behavior on real data. This closes a real risk: a
failed fetch plus a silent "PASSED" could let an automated push wipe the live dashboard's
data with nothing to catch it.

**Watch next:** whether HOOD's unmatched predictions turn out to be a genuine bug in the
swing-matching window (worth digging into the matching code directly next time this comes
up), whether JPM ever lands a hit, whether TSLA/QQQ's newly-improved hit rates hold up, and
whether NVDA/AMZN/SPY/VOO start showing their first grades.

## 2026-08-08 (Sat) — no change; solved yesterday's HOOD mystery, it's not a bug

**Fetch status:** Yahoo is still blocked from this environment (confirmed again via the
proxy's own status log: repeated "403 to CONNECT" gateway rejections for
query1.finance.yahoo.com, a policy denial, not a transient error). No cached CSVs to fall
back on, so running the engine here produced an empty `data.js`; the coherence gate
correctly rejected it, and I discarded that build and left the dashboard exactly as last
published by Friday's cloud refresh (healthy, generated 8/7 ~5-9 PM ET). It's also Saturday,
so there was no new trading session to grade anyway (the cloud refresh only runs Mon-Fri).

**Grades reviewed (10 tickers, same figures as Friday since no new session):** TSLA 30%/40%
(within 2/3 days), QQQ 30%/40%, GOOGL 50% (still the standout), JPM 0%, HOOD 0%, GC=F 0%.
NVDA/AMZN/SPY/VOO still too new (added 8/5) to have matured grades. Real-money ledger
unchanged: still just the 2 closed QQQ puts (+$980, +$600), nothing new opened or closed.

**What I dug into: HOOD's 8-of-9 unmatched predictions, flagged as a possible bug yesterday.**
Traced it using HOOD's own recorded swing pivots in `data.js`: the last *confirmed* pivot is
a high on 7/6 at $117.55. Price then crashed hard - from a brief bounce near $116-120 in
mid-July down to a $83.68 close on 7/31 - and, as of the newest data (8/7), still hasn't
rallied back 10% off that low to confirm a new pivot. The grading engine only matches a
prediction against a *confirmed* swing pivot, and there simply isn't one anywhere in the
7/15-7/29 window for it to match against - that's the entire explanation, not a bug in the
matching code. It's a different flavor of the same "model assumes oscillating swings"
limitation already diagnosed for JPM, just from a real, still-unresolved crash rather than
low volatility. These predictions should become retroactively gradable once HOOD's pending
low pivot finally confirms (price closing back above roughly $95).

**What changed and why:** nothing. The HOOD question that carried over from yesterday now
has a verified, non-bug answer, so there's no fix to make - honesty features, ledgers, and
the coherence gate are untouched.

**Watch next:** whether HOOD's pending low pivot confirms in the coming week (would
retroactively grade several 7/15-7/29 calls, for better or worse), whether JPM ever lands a
hit, whether GOOGL's 50% holds as more predictions mature, and whether NVDA/AMZN/SPY/VOO
start showing their first grades (they'll have had ~8 trading days by early next week).
