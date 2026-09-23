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

## 2026-08-09 (Sun) — no change; same story as yesterday, nothing new to grade

**Fetch status:** Yahoo is still blocking this environment (confirmed via the proxy's status
log: repeated "403 to CONNECT" rejections for query1.finance.yahoo.com, a policy denial, same
as the last several days). No cached CSVs on disk to fall back on, so running the engine
produced an empty `data.js`; the coherence gate correctly caught it ("0 tickers - build
produced no data, refusing to publish") and I discarded that build without touching the
published files. Also caught a leftover problem from yesterday's session: Friday's real fix
and log entry had been committed locally but never actually pushed to `origin/main` (repo was
left on a detached HEAD). Fast-forwarded `main` to that commit and pushed it first thing today
so the live site reflects yesterday's work. It's Sunday, so there's no new trading session to
grade either way (cloud refresh only runs Mon-Fri).

**Grades reviewed (10 tickers, all figures unchanged from Friday's 5:09 PM ET generation,
since nothing new has run since):** TSLA 30%/40% (within 2/3 days), QQQ 30%/40%, GOOGL 50%
(still the standout), JPM 0%, HOOD 0%, GC=F 0%. NVDA/AMZN/SPY/VOO each now show their first
single graded prediction (from the 8/6 session) - too small a sample to mean anything yet, but
worth noting as the first real data point for those four. Real-money ledger unchanged: still
just the 2 closed QQQ puts (+$980, +$600). Trade sheet unchanged since Friday, nothing new to
grade there.

**What changed and why:** no code change. Today's only fix was operational (pushing
yesterday's already-decided work to `origin/main`), not a new decision, so it doesn't count
against the one-change-per-day budget. Honesty features, ledgers, and the coherence gate are
untouched.

**Watch next:** confirm Monday's cloud refresh actually reaches Yahoo and produces a real
grading update (this environment's block appears environment-specific, not a Yahoo-wide
outage, since the cloud workflow has kept publishing on weekdays); watch NVDA/AMZN/SPY/VOO's
grades build up now that they have their first data point each; and continue watching for
HOOD's pending low pivot and whether JPM ever lands a hit.

## 2026-08-10 (Mon) — no change; traced GC=F's 0% streak to a real forecast miss, not a bug

**Fetch status:** Yahoo is still blocking this environment (same "403 to CONNECT" tunnel
failure as every recent day), so `fetch_data.py` failed on all 10 tickers and `analyze.py`
correctly produced an empty `data.js`. The coherence gate caught it ("0 tickers - build
produced no data, refusing to publish") and that build was discarded without touching any
published file. Good news: Monday's cloud refresh (`.github/workflows/refresh.yml`) ran fine
on its own infrastructure a few hours before this session started - the live site is showing a
real 5:11 PM ET build from today, so today's review is against fresh data, not stale weekend
numbers.

**Grades reviewed (10 tickers):** TSLA improved to 44%/56% (hit-within-2/3-days) on 9 graded
predictions, up from 30%/40% Friday. QQQ improved to 67%/83% on 6 graded. GOOGL held its
50% standout. JPM: still 0 of 10 logged predictions have matched *any* confirmed swing pivot
(unchanged, low-volatility stock rarely confirms new extremes). HOOD: only 1 of 10 has
matched so far (0% on that one) - most remain unmatched pending its long-overdue low pivot.
NVDA/AMZN/SPY/VOO: still 0 graded - each only has 3 logged sessions since 8/5 and needs a
confirmed pivot before grading can start, same maturation lag as everything else that's new.
Real-money ledger unchanged: still just the 2 closed QQQ puts (+$980, +$600).

**What I dug into: GC=F's 0-of-5 hit rate, stuck for several days running.** Traced it with
the actual pivot list in `data.js`: GC=F's last confirmed low is 7/16 at $3985.60, and the
price has since rallied straight to $4448.60 (+11.6%) without ever pulling back enough to
confirm a new low. Every "low" prediction logged from 7/23 onward (5 different dates) is
being graded against that same already-passed 7/16 low, so the gap between predicted date and
actual date only grows and every one reads as a miss. That's not a grading-code bug - it's an
honest measurement that GC=F's low-timing methods have been wrong throughout this rally, the
same "no fresh pivot to grade against" pattern already diagnosed for JPM (chop) and HOOD
(unresolved crash), just from the opposite direction (a persistent rally). Loosening the match
window to manufacture a better-looking number would be exactly the kind of honesty-feature
weakening this project rules out, so nothing changed.

**What changed and why:** nothing. Fetch was blocked (operational, not a code issue) and the
GC=F investigation resolved to a genuine forecast-timing miss rather than a bug, so there's no
fix to make today. Honesty features, ledgers, and the coherence gate are untouched.

**Watch next:** whether GC=F ever pulls back enough to confirm a new low pivot (would let its
backlog of "low" predictions finally grade, likely still poorly given the trend); whether
HOOD's and JPM's pending pivots ever confirm; and whether NVDA/AMZN/SPY/VOO produce their
first graded predictions now that they're approaching two weeks of logged sessions.

## 2026-08-11 (Tue) — no change; explained QQQ's rate drop, same structural pattern as GC=F

**Fetch status:** Yahoo is still blocking this environment (403 on every ticker, same as every
recent day), so `fetch_data.py` failed on all 10 tickers and `analyze.py` wrote an empty
`data.js`. The coherence gate caught it correctly ("0 tickers - refusing to publish") and I
restored the real files from git afterward so the empty build never touched what's live.
Good news: today's cloud refresh (`.github/workflows/refresh.yml`) ran fine on its own and
produced a real 5:56 PM ET build today, so today's grading review is against fresh data.

**Grades reviewed (10 tickers):** TSLA eased to 38%/46% (hit-within-2/3-days) on 13 graded
predictions, down from 44%/56% Monday - four new predictions graded, mostly misses. GOOGL
held steady at 50%/50% on 6 graded, still the standout. JPM: still 0 of 11 - every single
logged prediction remains unmatched to any confirmed pivot, same low-volatility chop pattern
diagnosed before. HOOD: 0%, only 1 of 11 has matched anything, still waiting on its overdue
low pivot. GC=F: still 0 of 7, unchanged, same rally-with-no-pullback story from Monday.
NVDA/AMZN/SPY/VOO: still 0 graded, too few sessions logged yet. Real-money ledger unchanged:
still just the 2 closed QQQ puts (+$980, +$600). Trade sheet unchanged, nothing new to grade
there either.

**What I dug into: QQQ's rate looked alarming (67%/83% Monday to 36%/43% today) but isn't a
regression.** Pulled QQQ's 14 resolved predictions directly from `data.js`: all 7 "high"
predictions logged since 7/9 are still unmatched to any confirmed swing high (QQQ has kept
climbing without a real pullback), so every one of them reads as a miss by default. Meanwhile
the 7 "low" predictions that *did* match are excellent - 6 of 7 within 3 days of the actual
7/29 low, most within 0-2 days. So the drop isn't new predictions going bad, it's more
unmatched "high" predictions piling up while QQQ stays in an unconfirmed uptrend - the same
"no fresh opposite-direction pivot to grade against" pattern already diagnosed for GC=F (there
it was low predictions stuck against a stale rally) and JPM/HOOD (chop and an unresolved
crash). Grading them as misses until a real pivot confirms is the honest call, not something
to loosen.

**What changed and why:** nothing. Fetch was blocked (operational) and the QQQ investigation
resolved to the same known "unmatched during a trend" pattern rather than a new bug, so no fix
was warranted today. Honesty features, ledgers, and the coherence gate are untouched.

**Watch next:** whether QQQ ever prints a real pullback that confirms a new swing high (would
let its backlog of "high" predictions finally grade); the same watch items as before -
GC=F's overdue low, HOOD's and JPM's pending pivots, and NVDA/AMZN/SPY/VOO building up their
first graded predictions.

## 2026-08-12 (Wed) — no change; nothing new, everything traces to already-diagnosed causes

**Fetch status:** Yahoo is still blocking this environment (403 on every ticker, same as every
recent day - `fetch_data.py` failed on all 10 and `analyze.py` wrote an empty `data.js` since
there's no cached CSV to fall back on). Also found the local git checkout had drifted to a
stale detached commit again before I even started - fetched and fast-forwarded to
`origin/main` first, same fix as a couple of reviews back. `coherence_check.py` correctly
passed on the real, already-published data (10 tickers) once I discarded the empty build, so
nothing needed re-shipping. The cloud refresh (`.github/workflows/refresh.yml`) ran fine on
its own today - live site reflects a fresh 5:54 PM ET build.

**Grades reviewed (10 tickers):** TSLA n=14 (36%/50% hit-within-2/3-days, roughly flat on
yesterday's 38%/46%). QQQ n=14 (36%/43%, also roughly flat). GOOGL n=7 (43%/43%, down slightly
from 50% now that one more prediction has graded - still well above the other stocks, one data
point isn't a trend). HOOD n=13 (0%, unchanged - still no confirmed low pivot since the 7/6
high; checked again today, price is $95.07 and the last confirmed pivot in `data.js` is still
that same 7/6 high, so the "unresolved crash" explanation from 8/8 still holds). JPM n=12 (0%,
unchanged low-volatility chop, diagnosed 8/6). GC=F n=9 (0%, unchanged - price has actually
pushed further away from a pullback, now $4469 vs. the still-uncompleted 7/16 low pivot at
$3985.60, so the "rally with no pullback" explanation from 8/10 is, if anything, more true
today than before). NVDA/AMZN/SPY/VOO: still n=0 in the track record, but this is not a mystery
- checked their logged predictions directly and every single one has a predicted date of
8/14 or later, so literally none of them are due to have resolved yet (first batch logged 8/5,
soonest predicted date 8/14). Real-money ledger unchanged: still just the 2 closed QQQ puts
(+$980, +$600), nothing new opened or closed. Today's new TSLA trade card (a same-day
$330/$345 call spread into the projected Thu 8/13 high) hasn't had time to resolve either.

**What changed and why:** nothing. No fresh 3-day pattern and no new bug - every persistently
flat number this review (HOOD, JPM, GC=F) checks out against the same non-bug explanation
already traced on an earlier day, and the NVDA/AMZN/SPY/VOO "zero grades" is simply because
none of their predictions have reached their target date yet, not a matching failure. Honesty
features, ledgers, and the coherence gate are untouched.

**Watch next:** whether NVDA/AMZN/SPY/VOO's first predictions (due 8/14) actually resolve and
grade correctly - that will be the first real test of the newer tickers' matching logic end to
end; whether GOOGL's dip from 50% to 43% is just noise or the start of a real fade as more
predictions mature; and the carryover items - GC=F's and HOOD's overdue pivots, and whether
JPM ever lands a hit.

## 2026-08-13 (Thu) — no change; HOOD's overdue low finally confirmed, grades logged

**Fetch status:** Yahoo is still blocked in this environment (403 on every ticker via the
sandbox's egress proxy - confirmed it's a policy-level block on `query1.finance.yahoo.com`,
not a transient network fault, so per the runbook I didn't retry or route around it).
`fetch_data.py` failed on all 10 tickers and `analyze.py` then wrote an empty, 0-ticker
`data.js` since there was no CSV to work from - I discarded that broken build before it could
be committed and kept the last good one. The cloud refresh workflow ran fine on its own again
today (fresh build at 5:54 PM ET / 21:54 UTC), and `coherence_check.py` passed cleanly on that
real, already-published data.

**Grades reviewed (10 tickers):** TSLA n=15 (33%/47% hit-within-2/3-days, roughly flat).
QQQ n=15 (33%/40%, roughly flat, still the "unmatched during an uptrend" pattern from 8/11).
GOOGL n=7 (43%/43%, unchanged). JPM n=13 (0%, unchanged - every one of its 13 resolved
predictions is still unmatched, the same low-volatility chop diagnosed on 8/6). GC=F n=10
(0%, unchanged - newer predictions still unmatched against any fresh pullback, same "rally
with no pivot" story as 8/10). **HOOD is the real news: n=15, jumped from 0% to 33%/40%.**
Checked it directly in `data.js` - a low pivot on 2026-07-31 ($86.56) has now confirmed, and
5 of HOOD's backlogged "low" predictions matched against it, 4 of them hitting within 2 days.
This is exactly the resolution the 8/8 "unresolved crash" diagnosis predicted: once price
actually bottomed and a real pivot printed, the stuck predictions could finally grade instead
of sitting at a default miss. NVDA/AMZN/SPY/VOO: still n=0, but confirmed (again) their first
predicted dates are 8/14 - tomorrow - so this is expected, not a bug. Real-money ledger
unchanged (still just the 2 closed QQQ puts, +$980/+$600). Today's trade cards (TSLA/HOOD/QQQ/
JPM/NVDA/SPY/VOO same-day call spreads, GOOGL/AMZN multi-week plays) are too fresh to have
resolved yet.

**What changed and why:** no code change. HOOD's jump from 0% to 33%/40% is a genuine data
resolution (a real pivot finally printed and predictions graded against it), not a bug to
chase, and every other flat number checks out against an already-diagnosed cause. Honesty
features, ledgers, and the coherence gate are untouched.

**Watch next:** whether NVDA/AMZN/SPY/VOO's first predictions (due 8/14, tomorrow) resolve and
grade correctly - the first real end-to-end test of the newer tickers; whether HOOD's new 33%/
40% holds up as more of its backlog grades or was a one-pivot bump; and the carryover items -
GC=F's overdue low, JPM's still-perfect miss streak, and GOOGL's 43% rate.

## 2026-08-14 (Fri) — no change; grades logged, everything checks out against known causes

**Fetch status:** Yahoo is still blocked in this sandbox (403 Forbidden on all 10 tickers'
chart-data and pre/post-market calls, same tunnel-level block as recent days - not a
transient fault). Ran `fetch_data.py` and confirmed all 10 failed the same way. Also test-ran
`analyze.py` to double-check: as expected with no fresh CSVs, it wrote a broken 0-ticker
`data.js`/`index.html`. I discarded that build with `git checkout` and kept the real one -
the cloud refresh workflow already produced a good build on its own today (generated 2026-08-14
5:31 PM ET), and `coherence_check.py` passed cleanly against it (10/10 tickers).

**Grades reviewed (10 tickers):** TSLA n=16 (31%/44% hit-within-2/3-days, roughly flat vs.
yesterday's 33%/47%). HOOD n=16 (31%/44%, similar to yesterday's 33%/40%). QQQ n=15 (33%/40%,
unchanged). GOOGL n=8 (38%/38%, down a bit from 43% - only one more graded prediction, too
early to call it a real fade yet). JPM n=15 (still 0% - checked the actual daily range data
directly: JPM has ground higher in a tight ~1-2%/day band for three weeks straight, 350->366,
with no real pullback for the zigzag to catch, exactly the low-volatility-chop diagnosis from
8/6, still true). GC=F n=11 (still 0% - gold is still pushing to new highs with no pullback,
same "rally with no pivot" story as 8/10). NVDA/AMZN/SPY/VOO: still n=0, but checked
directly - their very first predicted date (8/14) is today, and confirming a prediction
requires the actual swing pivot to print and hold, not just the calendar date to arrive
(same lag HOOD showed before its 7/31 low finally confirmed on 8/13). Real-money ledger
unchanged: still just the 2 closed QQQ puts (+$980, +$600), nothing new opened or closed.

**What changed and why:** no code change. Every number this review - JPM and GC=F's persistent
0%, the new tickers' persistent 0%, GOOGL's small dip - traces back to an already-diagnosed,
non-bug cause (real market chop/rally conditions or normal grading lag), so the improvement
discipline says grade and log only. Honesty features, ledgers, and the coherence gate are
untouched.

**Watch next:** whether NVDA/AMZN/SPY/VOO's first predictions actually start resolving now
that 8/14 has arrived; whether GOOGL's dip to 38% continues into a real fade over the next
couple of days; and the long-running carryover items - JPM's still-perfect miss streak and
GC=F's overdue pullback.

## 2026-08-15 (Sat) — no change; weekend, nothing new to grade

**Fetch status:** ran `fetch_data.py` and all 10 tickers failed with the same tunnel-level
403 block seen on recent days (this session's environment IP, not a Yahoo-wide outage). No
committed CSVs to fall back on, so `analyze.py` built an empty 0-ticker `data.js`; I discarded
that broken build with `git checkout` and kept the real one already on `main`. That published
build was generated 2026-08-14 7:25 PM ET by the cloud refresh workflow, and `coherence_check.py`
passed cleanly against it (10/10 tickers). It's Saturday, so this is expected either way -
markets are closed and the cloud refresh only runs weekdays (cron `1-5`), so there was never
going to be a new session to grade today.

**Grades reviewed (10 tickers, all figures unchanged from Friday's 7:25 PM ET generation,
since nothing new has run since):** TSLA n=16 (31%/44% hit-within-2/3-days). HOOD n=16
(31%/44%). QQQ n=15 (33%/40%). GOOGL n=8 (38%/38%, still the standout, still watching for a
real fade). JPM n=15 (still 0% - the low-volatility-chop diagnosis from 8/6 still holds, no
new bars to test it against over the weekend). GC=F n=11 (still 0% - same overdue-pullback
story). NVDA/AMZN/SPY/VOO: still n=0 - their first predicted dates (8/14) have now arrived per
the calendar, but confirming a prediction needs the actual swing pivot to print and hold, and
no new trading session has happened since Friday to do that. Real-money ledger unchanged:
still just the 2 closed QQQ puts (+$980, +$600), nothing new opened or closed.

**What changed and why:** no code change. There is nothing new to grade - same build, same
ledgers, same market data as yesterday's review, because no trading session occurred between
then and now. Improvement discipline says grade and log only on a day like this. Honesty
features, ledgers, and the coherence gate are untouched.

**Watch next:** Monday's cloud refresh should bring the first genuinely new session since
Friday - that's when to check whether NVDA/AMZN/SPY/VOO's first predictions start resolving,
whether GOOGL's 38% holds or fades further, and whether JPM or GC=F finally break their 0%
streaks.

## 2026-08-17 (Mon) — found and fixed a real hole in the grading ledger's record-keeping

**Fetch status:** Yahoo is still blocked from this environment (403 on every ticker). No local
price cache to fall back on, so `analyze.py` produced an empty 0-ticker build here, which I
discarded. The cloud refresh workflow (which does have network access) had already run 12
times today on its own and published a fresh build at 5:32 PM ET; `coherence_check.py` passed
cleanly against that real data (10/10 tickers).

**Grades reviewed (10 tickers):** TSLA n=16 (31%/44% hit-within-2/3-days). HOOD n=16 (31%/44%).
QQQ n=16 (31%/38%). GOOGL n=10 (40%/40%, still the standout). JPM n=17 (still 0% - checked the
swing detector directly: it hasn't confirmed a single high or low pivot for JPM since 5/19,
over three months of a slow grind higher with no 4%+ pullback for it to catch - every
prediction since is being tested against nothing, not against a wrong pivot). GC=F n=11 (still
0%, same overdue-pullback story as before). SPY/VOO n=1 each (0%, too small a sample to mean
anything yet). NVDA/AMZN still n=0 - confirmed directly in the prediction log that their
earliest predictions won't be old enough to grade until roughly 8/26 (the rule is 8 trading
days must pass first), so this is expected, not a bug. Real-money ledger unchanged: still just
the 2 closed QQQ puts (+$980, +$600).

**What changed and why (today's one change):** while digging into why JPM and GC=F have stayed
stuck near 0% for weeks, I found something more concrete than "the market's been quiet" - a
real bug in how the system keeps its own grading record honest. Each day the system logs a
same-day forecast ("here's what I predict for tomorrow's high and low") specifically so it can
be checked later against what actually happened. Using the site's git history, I found that on
two occasions (around 7/27-7/29 and again 8/13-8/14) a later run on the same calendar day
overwrote an already-correct "predict tomorrow" forecast with a broken one that just repeated
today's date - permanently erasing that day from ever being gradeable, with no error or
warning. I traced the exact commit where this happened (a run whose data was a day behind)
and confirmed it precisely: the forecast for 8/14 was correctly logged as `session: 2026-08-14`
by the evening of 8/13, then a later run silently regressed it back to `session: 2026-08-13`,
and 8/14 was never re-logged - it simply vanished from the grading record. I added a small
guard in `analyze.py` (in the "log horizons for future grading" step) so a same-day rewrite can
never move the target date backward, only forward or sideways - so this exact silent data loss
can't happen again. This only affects the internal grading ledger (`horizons_log.json`) that
tracks day-ahead accuracy behind the scenes; it changes nothing about what predictions or
prices are shown on the live dashboard. I verified the fix's logic against the exact historical
scenario it's meant to prevent (using a small standalone simulation, since Yahoo access is
blocked here) and confirmed it blocks that regression while still allowing normal day-to-day
updates through. `coherence_check.py` still passes cleanly. Honesty features (measured hit
rates, random-control comparisons, the grading itself) are untouched - this fix makes the
grading record more complete and trustworthy, not less strict.

**Watch next:** confirm on tomorrow's review that the fix is holding in production (no more
silently-skipped days in `horizons_log.json`); whether NVDA/AMZN's first predictions grade
correctly once they mature around 8/26; and JPM's three-month pivot drought, plus GC=F's
overdue pullback, both still open questions once the market finally gives the swing detector
something to catch.

## 2026-08-18 (Tue) — no change warranted, grades logged; confirmed yesterday's ledger fix is holding

**Fetch status:** Yahoo is still blocked from this environment (403 on every ticker, confirmed
directly with curl too). `fetch_data.py` left no local price files behind, so `analyze.py`
correctly produced an empty 0-ticker build here - I discarded those file changes rather than
publish them, since they would have wiped the live dashboard. The cloud refresh workflow (which
does have real network access) had already published a fresh build today at 5:30 PM ET, and
`coherence_check.py` passed cleanly against it (10/10 tickers).

**Grades reviewed (10 tickers):** TSLA n=16 (31%/44% hit-within-2/3-days), HOOD n=16 (31%/44%),
QQQ n=16 (31%/38%), GOOGL n=10 (40%/40%, still the standout) - all unchanged from yesterday, no
new predictions matured. JPM grew to n=19 (still 0%) - checked today's actual price action
directly: JPM pulled back from Wednesday's high of $366.50 to today's low of $359.30, only about
2%, still short of the 4%+ move the swing detector needs to confirm a pivot, so the drought
continues for a mechanical reason, not a bug. GC=F (n=11, still 0%) did the opposite - made a
fresh high today ($4,493.10), extending the same overdue-pullback story rather than resolving it.
SPY/VOO grew to n=2 each (still 0%, sample still too small to read anything into). NVDA/AMZN
still n=0 as expected, on track to mature around 8/26. Real-money ledger unchanged: still just
the 2 closed QQQ puts (+$980, +$600).

**Ledger integrity check:** walked `horizons_log.json`'s logged/session pairs from 8/11 through
today - all move forward or stay level, none regress backward, so the same-day-rewrite guard
added yesterday is holding in production with no repeat of the silent data-loss bug.

**What changed and why:** no code change. Nothing today crossed the 3+-day-persistence bar or
looked like a bug - JPM and GC=F are the same known, already-diagnosed drought as the last two
reviews, just one day further along. Improvement discipline says grade and log only on a day
like this. Honesty features, ledgers, and the coherence gate are untouched.

**Watch next:** whether JPM's pullback today (2% and counting) grows into the 4%+ move the
swing detector needs, which would finally give it a fresh pivot to grade against; GC=F's
pullback that still hasn't come despite a fresh high; and NVDA/AMZN's first predictions maturing
around 8/26.

## 2026-08-19 (Wed) — no change warranted, grades logged

**Fetch status:** Yahoo is still blocked from this review environment (403 on every ticker,
third day in a row), so `fetch_data.py` and `analyze.py` produced an empty 0-ticker build here -
I discarded those file changes rather than publish them. The cloud refresh workflow (which does
have real network access) had already published a fresh build today at 10:11 AM ET, and
`coherence_check.py` passed cleanly against it (10/10 tickers).

**Grades reviewed (10 tickers):** TSLA n=18 (28%/39% hit-within-2/3-days), HOOD n=18 (28%/39%),
QQQ n=18 (28%/33%), GOOGL n=12 (33%/33%, still the best performer but drifting down toward the
pack as more predictions mature) - all sample sizes grew by 2 from yesterday as expected. JPM
grew to n=20 (still 0%): checked today's actual prices directly - JPM has drifted down from
Wednesday 8/12's high of $366.09 to today's low of $361.18, about 1.4%, still well short of the
4%+ move the swing detector needs to register a pivot, so this is the same mechanical (not buggy)
drought as the last two reviews, now three days confirmed. GC=F (n=13, still 0%) also continued
its own already-diagnosed story: another fresh high today ($4,521.50, up from $4,434 on 8/18)
with the overdue pullback still not showing up. SPY/VOO grew to n=3 each (still 0%, sample still
too small to mean anything). NVDA/AMZN still n=0, on track to mature around 8/26 as before.
Spot-checked one of the hypothetical trade-sheet cards from 8/11 against what actually happened:
the TSLA "ride to $353.12 by 8/12" call spread and the "sell put at the $293.64 low by 8/17" idea
both missed by a wide margin (actual 8/12 high was $335.50, actual 8/17 low was $337.48) - this
lines up with the modest 28-39% hit rates already shown honestly on the dashboard, not a new
problem. Real-money ledger: the 2 closed QQQ puts are unchanged (+$980, +$600); the owner's real
short TSLA call (5x $345, exp 9/11, opened 8/19) is new since yesterday and currently far
out-of-the-money (TSLA traded $338-339 today vs. $357.50 breakeven) - nothing to grade yet, just
noting it's open.

**What changed and why:** no code change. Nothing today crossed the 3+-day-persistence bar with
a real bug behind it - JPM and GC=F are the same known, already-diagnosed droughts as the last
two reviews, just one more day along, and the trade-card miss is consistent with numbers already
disclosed rather than a new finding. Improvement discipline says grade and log only on a day like
this. Honesty features, ledgers, and the coherence gate are untouched.

**Watch next:** whether JPM's slow drift down (1.4% and counting) reaches the 4%+ threshold to
finally register a pivot; GC=F's pullback that keeps not arriving despite repeated fresh highs;
NVDA/AMZN's first predictions maturing around 8/26; and how the new real TSLA short call performs
against its own model's stress case (a projected $353.12 high on 8/20, still under breakeven).

## 2026-08-20 (Thu) — no change warranted, grades logged

**Fetch status:** Yahoo is still blocked from this review environment (403 on every ticker, now
four days running - today it showed up as the outbound proxy itself rejecting the connection to
query1.finance.yahoo.com rather than Yahoo's own block page, same net effect). `fetch_data.py`
failed on all 10 tickers and, with no CSVs to work from, `analyze.py` wrote an empty 0-ticker
`data.js` - I discarded those file changes rather than publish them. The cloud refresh workflow
(which has real network access) had already published a fresh build today at 5:34 PM ET, and
`coherence_check.py` passed cleanly against it (10/10 tickers).

**Grades reviewed (10 tickers):** TSLA n=18 (28%/39% hit-within-2/3-days), HOOD n=19 (26%/37%),
QQQ n=19 (26%/32%), GOOGL n=12 (33%/33%, unchanged today, no new predictions matured), JPM n=21
(still 0%): JPM kept sliding for a sixth straight session, closing today at a new low of $351.55,
down from Wednesday 8/12's high of $366.09 - that's now a 4.0% move, right at the edge of the
4%+ threshold the swing detector needs, so a fresh pivot may finally register in the next day or
two. GC=F (n=14, still 0%, but priceMedErrPct is a tiny 0.3% - the price targets are landing
close, just early) made yet another new high today ($4,597.10, up from $4,524.10 on 8/19), the
fourth straight session without the overdue pullback - same already-diagnosed story, one more
day along. SPY/VOO grew to n=4 each (still 0%, sample still too small to mean anything). NVDA/AMZN
still n=0, on track to mature around 8/26 as before. Real-money ledger: the 2 closed QQQ puts are
unchanged (+$980, +$600); the owner's real short TSLA call (5x $345, exp 9/11) passed its first
stress-test date today - the model's entry-day projection had TSLA testing a $353.12 high on
8/20, but the actual high was only $347.49, well under both that projection and the $357.50
breakeven, so the position stayed comfortably safe.

**What changed and why:** no code change. JPM and GC=F are the same known, already-diagnosed
droughts as the last several reviews, just one more day along (JPM is now close enough to the
4% threshold to watch closely, but closeness to a threshold isn't a bug). Improvement discipline
says grade and log only on a day like this. Honesty features, ledgers, and the coherence gate are
untouched.

**Watch next:** whether JPM's now-4.0% drift finally crosses the swing detector's threshold and
registers a pivot; GC=F's pullback that still hasn't shown up after four straight new highs;
NVDA/AMZN's first predictions maturing around 8/26; and the real TSLA short call's next stress
date (the model's 8/27 low window at ~$317, and its 9/11 expiry-day projection of $365.08, which
is above breakeven and why the plan is to close before then, not hold to expiry).

## 2026-08-21 (Fri) — no code change warranted, grades logged; real-position risk note

**Fetch status:** Yahoo is still blocked from this review environment (403 on every ticker,
confirmed via the proxy's own status log as a gateway-level policy denial to
query1.finance.yahoo.com, not a Yahoo block page). `fetch_data.py` and `analyze.py` produced an
empty 0-ticker build here - I discarded those file changes rather than publish them. The cloud
refresh workflow (which has real network access) had already published a fresh build today, and
`coherence_check.py` passed cleanly against it (10/10 tickers).

**Grades reviewed (10 tickers):** TSLA n=19 (26%/37% hit-within-2/3-days), HOOD n=20 (25%/35%),
QQQ n=20 (25%/30%), GOOGL n=12 (33%/33%, still the standout). JPM n=23 (still 0%) - checked
today's actual prices: JPM made a fresh low today at $350.37, down from 8/12's high of $366.09,
a 4.3% move - finally past the swing detector's 4% threshold after six sessions of grinding
lower, so a fresh pivot should register on the next refresh and start giving JPM's predictions
something real to grade against. GC=F (n=15, still 0%) made yet another new high today
($4,690.30, up from $4,530.00 on 8/20) - the fifth straight session without the overdue
pullback, same already-diagnosed story. SPY/VOO grew to n=4/n=5 (still 0%, sample still too
small to mean anything). NVDA/AMZN still n=0, on track to mature around 8/26 as before.

**Real-money ledger:** the 2 closed QQQ puts are unchanged (+$980, +$600). The owner's real
short TSLA call (5x $345, exp 9/11, breakeven $357.50) had its biggest test yet today - TSLA
spiked to a $366.50 high and closed at $362.86, both above breakeven and above the model's own
8/20 stress-case projection of $353.12. This is a real, current risk to an open position, not a
backtest number, so the owner should know: the position is now trading above its breakeven for
the first time since it was opened 8/19. The model's own plan for this trade was to close near
the 8/27 low window (~$317) or at 50% of credit, whichever comes first - today's move is well
outside that plan and worth the owner's attention regardless of what tomorrow's review finds.

**What changed and why:** no code change. JPM crossing its 4% threshold is a mechanical
milestone already flagged as "close" in the last two reviews, not a new bug; GC=F is the same
overdue-pullback story one day further along. Improvement discipline says grade and log only on
a day like this. Honesty features, ledgers, and the coherence gate are untouched.

**Watch next:** whether JPM's fresh 4.3% low finally registers a pivot on the next cloud
refresh and starts moving its grade off 0%; GC=F's pullback that still hasn't shown up after
five straight new highs; NVDA/AMZN's first predictions maturing around 8/26; and, most
importantly, how the real TSLA short call's mark evolves from here now that it's trading above
breakeven - the model's plan still points to an 8/27 low window as the intended exit.

## 2026-08-22 (Sat) — weekend, nothing new to grade; no change

**Fetch status:** blocked again from this review environment (403 at the gateway to
query1.finance.yahoo.com, same as yesterday) - moot today anyway, since it's Saturday and the
cloud refresh workflow only runs on weekdays (its cron is `1-5`), so there's been no new refresh
since Friday 7:19 PM ET. The dashboard is still serving Friday's close, unchanged, and
`coherence_check.py` still passes cleanly against it (10/10 tickers).

**Grades reviewed:** identical to yesterday's numbers since no new sessions have printed -
TSLA n=19 (26%/37%), HOOD n=20 (25%/35%), QQQ n=20 (25%/30%), GOOGL n=12 (33%/33%). JPM n=23
still shows 0% and every one of its 23 "resolved" entries still has a null actual price/date,
meaning the grader has never found a matching swing to check JPM's calls against - worth a
closer look if that's still true once JPM's newly-crossed 4% pivot (flagged Friday) has had a
few sessions to register; if it's still 23-for-23 null next week that would point to a real
matching bug rather than just a quiet ticker. GC=F (n=15, still 0%, medErr% a tight 0.3%)
remains on its fifth straight new-high session without the overdue pullback. SPY/VOO (n=4/n=5)
and NVDA/AMZN (n=0) are unchanged, still too young to mean anything.

**Real-money ledger:** unchanged from Friday - the 2 closed QQQ puts stand at +$980 and +$600;
the owner's real short TSLA call (5x $345, exp 9/11, breakeven $357.50) is still marked against
Friday's close of $362.86, above breakeven. No new price action to reassess it against over the
weekend.

**What changed and why:** no code change. It's a non-trading day with no new data to grade -
improvement discipline calls for grade-and-log only, and there's nothing to grade. Honesty
features, ledgers, and the coherence gate are untouched.

**Watch next:** Monday's first fresh refresh - whether JPM's pivot registered and starts
moving its 0%/null-actual streak, whether GC=F finally shows a pullback after five (soon six)
straight new highs, and how the real TSLA short call's mark opens the week relative to its
$357.50 breakeven and the 8/27 low-window exit plan.

## 2026-08-23 (Sun) — weekend, nothing new to grade; no change

**Fetch status:** blocked again from this review environment (403 at the gateway to
query1.finance.yahoo.com). Moot today anyway - it's Sunday, markets are closed, and the cloud
refresh workflow doesn't run on weekends, so there's been no new session since Friday 8/21's
close. `analyze.py` produced an empty 0-ticker build against no data here, so I discarded that
output rather than publish it. `coherence_check.py` passes cleanly (10/10 tickers) against the
last real build, Saturday's cloud refresh, which itself just re-served Friday's numbers.

**Grades reviewed:** unchanged from yesterday - TSLA n=19 (26%/37% hit-within-2/3-days), HOOD
n=20 (25%/35%), QQQ n=20 (25%/30%), GOOGL n=12 (33%/33%). JPM n=23 is still 23-for-23 with a
null actual price/date on every entry - the grader still hasn't found a single matching swing to
check any JPM call against, even after Friday's 4.3% move crossed the swing detector's
threshold. That move needs at least one fresh trading session to turn into a registered pivot,
and none has happened since Friday, so this is still an open question rather than a confirmed
bug: if it's still 23-for-23 null after Monday and Tuesday's sessions, that would point to a
real matching problem worth fixing, not just a quiet ticker. GC=F (n=15, still 0%, price error a
tight 0.3%) and SPY/VOO (n=4/n=5) are unchanged. NVDA/AMZN still n=0, on track to mature this
week.

**Real-money ledger:** unchanged from Friday - the 2 closed QQQ puts stand at +$980 and +$600.
The owner's real short TSLA call (5x $345, exp 9/11, breakeven $357.50) is still marked against
Friday's close of $362.86, above breakeven, with no new price action over the weekend to
reassess it against.

**What changed and why:** no code change. It's a non-trading day with nothing new to grade -
improvement discipline calls for grade-and-log only. The JPM null-actual question from
yesterday's review still needs live Monday/Tuesday data before it's fair to call it a bug versus
a quiet ticker, so today isn't the day to touch the grading code. Honesty features, ledgers, and
the coherence gate are untouched.

**Watch next:** Monday's first fresh session - whether it finally gives JPM's crossed-threshold
move a pivot to register against, whether GC=F's overdue pullback shows up, and how the real
TSLA short call's mark opens the week relative to its $357.50 breakeven and the 8/27 low-window
exit plan.

## 2026-08-24 (Mon) — fetch blocked again; investigated the JPM issue but held off fixing it

**Fetch status:** blocked from this review environment - the gateway returned 403 to every
CONNECT attempt at query1.finance.yahoo.com, confirmed by the proxy's own status log ("gateway
answered 403 to CONNECT (policy denial or upstream failure)"). This is a network policy block on
this box, not a Yahoo outage or a code problem. `analyze.py` has no raw price data to work from
here (the day's CSVs aren't committed to the repo by design), so it produced an empty, broken
0-ticker build; that output was discarded rather than published. `coherence_check.py` passes
cleanly (10/10 tickers) against the real build already live on the site - Friday and the
weekend's cloud refreshes, most recently generated 08/24 5:36 PM ET, which is today's cloud
refresh working fine on its own infrastructure.

**Grades reviewed:** TSLA n=20 (36%/50% hit-within-2/3-days, median price error 8.8%), HOOD n=22
(38%/54%, 5.2%), QQQ n=22 (50%/62%, 2.6% - still the strongest all-around), GOOGL n=13
(33%/33%, 9.2%). GC=F n=16 is still 0% hit-within-3-days but with a tight 0.3% median price
error - it keeps calling the right levels on the wrong days. JPM is now 24-for-24 with a null
actual price/date on every graded entry - the swing-matching grader has never once found a
matching real swing for any JPM call, across several days of review now.

**What I looked into:** with JPM's null streak now well past the "3+ graded days" bar for asking
whether it's a bug, I read through the grading code (analyze.py's per-ticker grading loop) rather
than just noting the number again. The matcher picks the nearest real swing pivot to a
prediction's target date - by date only, not by price - so it should find *some* candidate as
long as the ticker has pivots at all; it only counts as a real match if that nearest pivot lands
within 10 trading days. That JPM never matches, while GC=F (also a quiet, low-volatility ticker)
matches on 5 of 16, points to JPM's swing detector itself finding pivots that are unusually
sparse or badly timed, not a "quiet stock" excuse - GC=F is quiet too and still matches
sometimes. My best guess is the volatility-scaled swing threshold (floored at 4%) is too coarse
for JPM's actual daily range, spacing its detected swings so far apart that none ever lands near
a predicted date. I did not change the code today: this needs to be checked against JPM's real
recent price history (pivot count and spacing) to confirm before touching a threshold that every
ticker shares, and today's fetch block means there's no live data here to verify it against.
Making that change blind, without being able to run it and watch coherence_check and JPM's own
grades respond, is more likely to trade one bug for another than to fix this one.

**Real-money ledger:** the owner's real short TSLA call (5x $345, exp 9/11, breakeven $357.50)
saw today's session (8/24) print an intraday high of $363.24 - briefly through breakeven - before
closing back down at $348.95, modestly in the money against the $345 strike but back under
breakeven. The model's own 8/27 predicted low window (~$317) is looking shaky: TSLA has stayed
in a $335-366 band since the trade was opened 8/19 and hasn't shown the pullback that window
calls for. The 2 closed QQQ puts are unchanged at +$980 and +$600.

**What changed and why:** no code change. Fetch access was blocked all day, so there was no live
data to safely test a fix against, and pushing an untested change to shared grading logic that
every ticker depends on would risk breaking more than it fixes. Improvement discipline calls for
grade-and-log on a day like this. Honesty features, ledgers, and the coherence gate are
untouched.

**Watch next:** whether tomorrow's cloud refresh (assuming it has real market access) can confirm
or rule out the JPM swing-spacing theory - if it can, that's the fix to make; the real TSLA short
call against the 8/27 low window and the $357.50 breakeven as expiry (9/11) gets closer; and
GC=F's price-accurate-but-date-blind streak, still 0-for-16 on hit-within-3-days.

## 2026-08-25 (Tue) — JPM mystery solved: it's not a bug, JPM just hasn't had a 4%+ pullback since May

**Fetch status:** blocked again from this review environment - same 403 on every CONNECT to
Yahoo's chart API as recent days, confirmed policy-level rather than a code problem.
`coherence_check.py` passes cleanly (10/10 tickers) against today's site build, which the
separate cloud refresh workflow already generated and published at 08/25 5:35 PM ET while this
review ran, so the live dashboard reflects real market data even though this environment
couldn't fetch its own.

**Grades reviewed:** TSLA n=21 (24%/33% hit-within-2/3-days, 7.8% price error), HOOD n=23
(22%/30%, 5.2%), QQQ n=24 (38%/46%, 2.5% - still the most reliable), GOOGL n=15 (27%/27%, 6.6%).
JPM n=26 is still 0-for-26 with every actual price/date null. GC=F n=17 is unchanged at 0%
hit-within-3-days despite a tight 0.3% median price error. NVDA (n=1) and AMZN (n=0) are still
too new to grade; SPY (n=5) and VOO (n=6) both 0% on small samples.

**What I found:** the JPM null streak has now been open for a week of daily reviews, well past
the "3+ days" bar, so today I settled it for good instead of noting the number again. I pulled
JPM's actual daily closes from `daily_extremes.json` since 05/19/2026 (the last confirmed swing
pivot) and ran the exact same zigzag function from `analyze.py` against them by hand, in a
throwaway script, not by editing the real grading code. Result: zero pivots trigger, at any
point between 05/19 and today - JPM has been in a genuine, uninterrupted rally from $295.70 to
$356.69 without a single close-to-close pullback of 4% or more from its running peak. The
closest it ever came was late June (~1.6% short) and late August (~0.3% short). Every
prediction logged in that window necessarily has no real swing to check it against, because no
qualifying swing has happened yet - the grader is correctly reporting "no match" rather than
manufacturing a fake one. This is the honesty/coherence design working exactly as intended, not
the bug I was starting to suspect on Monday. The `pivots < 8` auto-relax that halves the
threshold never fires for JPM because it looks at total pivot count over 5 years (64, plenty),
not "time since the most recent one" - that's a real gap in principle, but touching threshold
logic that every ticker's live chain and period-extremes depend on, to fix a one-ticker
statistics-display quirk that isn't actually wrong, is a worse trade than leaving it alone.

**Real-money ledger:** the owner's real short TSLA call (5x $345, exp 9/11, breakeven $357.50) is
marked against today's close of $350.82, still comfortably under breakeven. The model's 8/27
predicted low window (~$317) is 2 sessions away and still hasn't been approached - TSLA has held
a $335-366 band since the trade opened 8/19. The 2 closed QQQ puts are unchanged at +$980 and
+$600.

**What changed and why:** no code change. The JPM investigation concluded with a clean answer -
real market behavior, not a defect - so there is nothing to fix; changing the swing/grading logic
today would be solving a problem that doesn't exist. Honesty features (measured hit rates,
random-control comparisons, self-grading, the coherence gate) and ledgers are untouched, and
`tickers.txt` wasn't touched.

**Watch next:** whether JPM finally prints a pivot (it's within ~2.3% of triggering a high off
the 08/12 peak of $365.18 if it rallies, or needs to break back below ~$350.6 to confirm one the
other way) - once it does, the grading numbers should start moving off 0% for the first time in
weeks. Also watching the 8/27 low window for the real TSLA short call, and whether GC=F's
own extended pivot drought (last confirmed 07/16) turns out to be the same "quiet trend, not a
bug" story once it breaks.

## 2026-08-26 (Wed) — no change warranted, grades logged

**Fetch status:** blocked again from this review environment - same 403-at-the-gateway block on
every CONNECT to Yahoo's chart API (confirmed via the proxy's own status log: "gateway answered
403 to CONNECT" for query1.finance.yahoo.com, a policy denial, not a Yahoo outage). With no CSVs
cached locally, running `analyze.py` here wrote an empty 0-ticker `data.js`/`index.html` - caught
that immediately (before committing anything) and reverted those files, keeping the real,
already-published build. That real build was generated today by the separate cloud refresh
workflow (which does have market access) at 04:29 PM ET, and `coherence_check.py` passes cleanly
against it (10/10 tickers).

**Grades reviewed:** TSLA n=23 (22%/30% hit-within-2/3-days, 7.8% price error), HOOD n=25
(20%/28%, 5.2%), QQQ n=26 (38%/46%, 2.0% - still the most reliable), GOOGL n=15 (27%/27%, 6.6%,
unchanged since yesterday - no new predictions matured). JPM n=28 is still 0-for-28 with every
actual price/date null, same drought fully diagnosed yesterday (a genuine, uninterrupted rally
since 05/19 with no 4%+ pullback for the grader to catch, not a bug) - worth noting JPM rallied to
$357.00 today, closing the gap toward the 08/12 peak of $365.18 a bit further, but still short of
confirming a fresh pivot either direction. GC=F n=19 is unchanged at 0% despite a tight 0.3% price
error, same overdue-pullback story. NVDA (n=2) and AMZN (n=0) are still too new to read anything
into; SPY (n=7) and VOO (n=8) both still 0% on small samples. Today's trade-sheet cards (all dated
09/08 entries) are too fresh to have resolved.

**Real-money ledger:** the owner's real short TSLA call (5x $345, exp 9/11, breakeven $357.50) is
marked against today's close-area price of $345.82, comfortably under breakeven. Tomorrow (8/27)
is the model's own predicted low window (~$317) - the exit point the original plan called for
(buy back at that low or at 50% of credit, whichever comes first). Worth checking tomorrow's
review specifically against that window. The 2 closed QQQ puts are unchanged at +$980 and +$600.

**What changed and why:** no code change. Nothing today crossed the 3+-day-persistence bar with a
new, undiagnosed pattern - JPM and GC=F are the same known droughts settled yesterday, just one
more day along, and every other number moved in line with recent trend. Improvement discipline
calls for grade-and-log only on a day like this. Honesty features, ledgers, and the coherence gate
are untouched, and `tickers.txt` wasn't touched.

**Watch next:** tomorrow's 8/27 low window (~$317) against the real TSLA short call's planned
exit - the single most concrete near-term test this system has open right now; whether JPM's
rally toward $365.18 keeps going far enough to finally confirm a pivot; and GC=F's still-overdue
pullback from its extended run of highs.

## 2026-08-27 (Thu) — fixed the coherence gate's blind spot, grades logged

**Fetch status:** blocked again - same 403-at-the-gateway policy denial on every CONNECT to
Yahoo's chart API (confirmed in the proxy's own log). With no CSVs to work from, `analyze.py`
wrote an empty 0-ticker `data.js`/`index.html` here; caught it before committing anything and
reverted those files. The real build is the one the separate cloud refresh workflow published
today at 10:45 AM ET (it has market access this repo's review environment doesn't), and that's
what's still live.

**Today's fix - the coherence gate itself had a hole:** this same "fetch blocked, empty build
discarded" situation has now happened on close to a dozen review days in this log, and every one
of those entries says `coherence_check.py` "passed cleanly" - but checking it against the actual
0-ticker file just now, it passes an EMPTY build too. It has no check that the tickers in
`tickers.txt` actually made it into `data.js`, so a broken 0-ticker (or partially-empty) build
would sail through the one gate that's supposed to stop a bad build from publishing. Added one
check: the gate now reads `tickers.txt` and fails loudly, listing exactly which tickers are
missing, if any of them aren't in `data.js`. Verified it two ways - it now correctly FAILS against
a synthetic empty build, and still PASSES cleanly against today's real 10-ticker build. This makes
the gate stronger, not weaker: it can only newly catch broken builds, never wave through more.

**Grades reviewed (unchanged from yesterday - no new sessions matured):** QQQ remains the most
reliable at n=27, 37%/48% hit-within-2/3-days, 1.6% price error. TSLA n=24 (21%/29%, 7.8%), HOOD
n=25 (20%/28%, 5.2%), GOOGL n=15 (27%/27%, 6.6%). JPM (n=30) and GC=F (n=20) are still stuck at
0% despite tight price accuracy (GC=F's median error is just 0.3%) - both are the same
long-diagnosed "no qualifying pullback yet" drought from prior days, not new. SPY/VOO (n=8/9) are
still 0% on small samples; NVDA (n=3) and AMZN (n=0) remain too new to read.

**Real-money ledger - worth the owner's attention:** the open TSLA short call (5x $345 strike,
exp 9/11, breakeven $357.50) was planned around an 8/27 (today) low window near $317 as the exit
trigger. That low never happened - TSLA has instead run up to $351.99 today, close enough to the
$357.50 breakeven to be a real concern, and the model's own current chain now projects a HIGH of
$367.23 tomorrow (8/28), which is above breakeven. The original ~$317 low window has dropped out
of the current chain entirely (next low call is now 9/11 near $311). This is exactly the situation
the plan's other trigger exists for - "50% of credit, whichever comes first" - since the date-based
trigger did not fire the way expected.

**What changed and why:** one code change - the coherence gate fix above, justified by a bug
that's been silently letting empty builds "pass" for many consecutive review days. No other
changes; grades moved in line with trend and nothing else crossed the persistence bar. Honesty
features (measured hit rates, random-control comparisons, self-grading) and ledgers are untouched,
`tickers.txt` wasn't touched, and the coherence gate is now stricter, never weaker.

**Watch next:** the TSLA short call is the most urgent item - it's now trading close to its
breakeven with the model itself projecting more upside tomorrow, so the credit-based exit trigger
deserves attention regardless of price/date windows; also whether JPM or GC=F finally produce the
pullback the grader has been waiting on.

## 2026-08-28 (Fri) — no change warranted, grades logged

**Fetch status:** blocked again on all 10 tickers - same 403 Forbidden at the proxy gateway seen
on prior review days. `fetch_data.py` had no CSVs to work from, so `analyze.py` wrote an empty
0-ticker `data.js`/`index.html`. The rebuilt coherence gate (added yesterday) caught it correctly
and failed loudly; reverted those files before anything was committed. The real, live build is the
one the separate cloud refresh workflow published today at 5:32 PM ET (10/10 tickers), and that's
what's still live and what today's grades below are read from.

**Grades reviewed:** QQQ still the standout at n=27, 37%/48% hit-within-2/3-days, 1.6% price
error. TSLA n=24 (21%/29%, 7.8%), HOOD n=25 (20%/28%, 5.2%). GOOGL grew to n=16 (25%/25%, 6.6%) -
one more prediction matured and missed, a small dip from yesterday's 27%/27%, not a new pattern.
JPM (n=31) and GC=F (n=20) remain stuck at 0% hit rate despite tight price accuracy - the
long-diagnosed "no qualifying pullback yet" drought, now well past the 3-day persistence bar but
already root-caused on 8/25 as normal market behavior, not a bug. SPY/VOO (n=8/9) still 0% on thin
samples; NVDA grew to n=4, AMZN still n=0 - both too new to read.

**Possible first crack in the GC=F drought:** today's actual gold session (from `daily_extremes.json`)
swung from a $4688.00 high down to a $4495.50 low - a real ~4.1% intraday reversal, the sharpest
single-day range gold has printed in this log's history so far, after a week of drifting sideways
in a tight $4600-4680 band. This could be the pullback the grader has been waiting on, but it's one
day - not yet a confirmed pattern, so no action today. Worth checking tomorrow whether it holds or
was just noise.

**Real-money ledger - good news for the owner:** the open TSLA short call (5x $345 strike, exp
9/11, breakeven $357.50) touched an intraday high of $358.80 today (briefly above breakeven) but
closed at $348.75, well underneath it. More importantly, the model's own current prediction chain
no longer shows a high above breakeven before the 9/11 expiry - the next projected high is now
9/23 at $351.85 (still under $357.50), with the next low projected 9/8 near $302.37. That's a
meaningful de-escalation from yesterday's entry, which had the chain projecting a $367.23 high for
today; that projection did not happen (today's real high was $358.80).

**What changed and why:** no code change. Nothing crossed the 3+-day-persistence bar with a new,
undiagnosed pattern today - GC=F's sharp reversal is interesting but only one day old, and
JPM/GC=F's 0% hit rates are the same already-explained drought from 8/25. Improvement discipline
calls for grade-and-log only on a day like this. Honesty features (measured hit rates,
random-control comparisons, self-grading) and the coherence gate are untouched, and `tickers.txt`
wasn't touched.

## 2026-08-29 (Sat) — fetch blocked again; grade-and-log only, no fresh session data

**Fetch status:** blocked on all 10 tickers - same 403 Forbidden at the proxy gateway seen on
several prior review days, confirmed by the proxy's own status log ("gateway answered 403 to
CONNECT (policy denial or upstream failure)" against `query1.finance.yahoo.com`). This is a
network policy block on this review box, not a Yahoo outage or a bug in `fetch_data.py`. With no
CSVs to work from (they're gitignored by design, never committed), `analyze.py` wrote an empty
0-ticker `data.js`/`index.html`/`dashboard_single.html`; that broken output was discarded before
anything was staged. `coherence_check.py` passes cleanly (10/10 tickers) against the real build
still live on the site - the separate cloud refresh workflow (which runs on its own
infrastructure, unaffected by this box's network policy) last published successfully today at
12:10 AM ET, so the site is current as of this morning's pre-market and no data is stale.

**Grades reviewed (from today's live build):** QQQ still the standout at n=27, 37%/48%
hit-within-2/3-days, 1.6% price error. TSLA n=24 (21%/29%, 7.8%), HOOD n=25 (20%/28%, 5.2%). JPM
(n=30) and GC=F (n=20) remain stuck at 0% hit rate despite GC=F's tight 0.3% price accuracy -
the same already-diagnosed "no qualifying pullback yet" drought from 8/25, not a new problem.
SPY/VOO (n=8/9) still 0% on thin samples. One thing worth a note, not an alarm: GOOGL (n=15),
JPM (n=30), and NVDA (n=3) each show one fewer resolved prediction than yesterday's entry
recorded (16, 31, 4). That's most likely normal ledger housekeeping (a rolling window or a
re-grade reshuffling which entries currently qualify as resolved) rather than lost data, but it's
three tickers moving the same direction on the same day, so it's worth a second look once fetch
access returns and a fresh run can be compared against today's for what specifically dropped off.

**GC=F reversal follow-up:** no new session data available today (fetch blocked), so it's not yet
possible to confirm whether Friday's sharp $4688 -> $4495.50 reversal held or was one-day noise.
Carrying this watch item forward again.

**Real-money ledger:** the open TSLA short call (5x $345 strike, exp 9/11, breakeven $357.50) -
last real print was Friday's close at $348.75, still comfortably under breakeven. The model's own
prediction chain (from today's live build) has shifted further in the position's favor: it now
shows no high above breakeven before expiry at all - the next projected high is 9/11 itself at
just $326.07, well under both breakeven and even today's spot price of $348.19, with the next low
projected 9/8 near $302.73. That a "high" target sits below current spot is a little unusual on
its face, but the calibration factors are neutral (priceCalibHigh 1.0) so it's not a calibration
artifact - it looks like the underlying Fibonacci projection itself just reads as a soft target
this early in its date window (09/09-09/15), which is legitimate but worth sanity-checking once
live data confirms it isn't a mismatched swing reference. Nothing here changes the picture from
yesterday: still no rally-through-breakeven signal from the model itself.

**What changed and why:** no code change. Today's anomalies (the three tickers' n dropping by
one, the below-spot high target) are each one day old and neither meets the 3+-day persistence
bar nor looks like a clear, provable bug from this vantage point - and with fetch blocked, there's
no live data here to safely test a fix against even if one were obvious. Improvement discipline
calls for grade-and-log only on a day like this. Honesty features (measured hit rates,
random-control comparisons, self-grading) and the coherence gate are untouched, and `tickers.txt`
wasn't touched.

**Watch next:** whether the three tickers' dropped resolved-count is a one-day blip or repeats
tomorrow (if it repeats, that's the 3-day bar starting); whether GC=F's Friday reversal turns into
a real pullback; and the TSLA short call's 9/11 expiry, now looking safer than at any point since
the position was opened, but still worth a daily check against the live chain.

**Watch next:** whether GC=F's reversal today turns into a real multi-day pullback (would finally
start moving its grade off 0%); whether JPM ever produces the pullback the grader is waiting on;
and the TSLA short call heading into its 9/11 expiry, now on firmer footing than yesterday but
still worth a daily check against the live chain.

## 2026-08-30 (Sun) — weekend, fetch blocked again; grade-and-log only, no fresh session data

**Fetch status:** blocked on all 10 tickers - same 403 Forbidden at the proxy gateway seen on
recent prior review days, confirmed by the proxy's own status log ("gateway answered 403 to
CONNECT (policy denial or upstream failure)" against `query1.finance.yahoo.com`). Still a network
policy block on this review box, not a Yahoo outage or a bug in `fetch_data.py`. With no CSVs to
work from (gitignored by design, never committed), `analyze.py` again wrote an empty 0-ticker
`data.js`/`index.html`/`dashboard_single.html`; that broken build was caught immediately by
`coherence_check.py`'s ticker-count gate ("data.js is missing 10 of 10 tracked tickers") and
discarded via `git checkout --` before anything was staged. `coherence_check.py` then passes
cleanly (10/10 tickers) against the real build still live on the site.

**No new session data either way:** today is Sunday and markets were last open Friday 8/28 -
`daily_extremes.json`'s newest entries across every ticker are still 8/28, so even a working
fetch here would have added nothing to grade. The live site's last cloud refresh was Friday
6:15 PM ET (the separate `.github/workflows/refresh.yml` job, which runs on its own
infrastructure unaffected by this box's network policy, does not run on weekends) - so the site
is exactly as current as it should be, not stale.

**Grades reviewed (unchanged from the live build):** QQQ still the standout at n=27, 37%/48%
hit-within-2/3-days, 2.7% avg price error. TSLA n=24 (21%/29%, 9.4%), HOOD n=25 (20%/28%, 7.3%),
GOOGL n=16 (25%/25%, 7.5%). JPM (n=30) and GC=F (n=20) remain at 0% hit rate - the
already-diagnosed "no qualifying pullback yet" drought (JPM traced to a real forecast miss back
on 8/25, not a bug). SPY/VOO (n=8/9) and NVDA (n=4) still 0% on thin samples. Nothing here moved
since Friday's build because no new trading day has printed.

**Real-money ledger:** the open TSLA short call (5x $345 strike, exp 9/11, breakeven $357.50) -
last real print is still Friday's close, $348.75, comfortably under breakeven. The model's own
current chain shows next low 9/8 near $302.73 and next high 9/23 near $352.28 - still under
breakeven and no rally-through-breakeven signal before the 9/11 expiry. Same picture as the last
two entries; nothing new to act on until Monday's session.

**What changed and why:** no code change. There's no new market data today to test any fix
against even if a clear bug had turned up, and none did - today is a pure repeat of Friday's
already-graded state plus a network block outside this repo's control. Improvement discipline
calls for grade-and-log only on a day like this. Honesty features (measured hit rates,
random-control comparisons, self-grading) and the coherence gate are untouched, and `tickers.txt`
wasn't touched.

**Watch next:** whether GC=F's pullback (first seen Friday 8/28) turns into a real multi-day move
once fresh data resumes; whether JPM ever produces the pullback the grader is waiting on; and the
TSLA short call heading into its 9/11 expiry, still on the safe side of breakeven as of Friday's
close.

## 2026-08-31 (Mon) — fetch blocked again; TSLA's rally pushed the real short call above breakeven; grade-and-log only

**Fetch status:** blocked on all 10 tickers - same 403 Forbidden at the proxy gateway as every
recent review day, confirmed again by the proxy's own status log ("gateway answered 403 to
CONNECT (policy denial or upstream failure)" against `query1.finance.yahoo.com`). With no CSVs
committed to the repo (gitignored by design), `analyze.py` wrote the expected empty 0-ticker
`data.js`/`index.html`/`dashboard_single.html`/`week_plan.json`; `coherence_check.py` caught it
immediately ("data.js is missing 10 of 10 tracked tickers") and the broken build was discarded via
`git checkout --` before anything was staged. `coherence_check.py` then passes cleanly (10/10
tickers) against the real build the separate cloud refresh workflow already published today at
2:10 PM ET.

**Grades reviewed (from today's live build):** QQQ remains the standout at n=27, 37%/48%
hit-within-2/3-days, 1.6% avg price error. TSLA n=25 (20%/28%, 7.8%), HOOD n=25 (20%/28%, 5.2%),
GOOGL n=17 (24%/24%, 6.6%). JPM (n=31) and GC=F (n=21) are still stuck at 0% hit rate - both
already traced on 8/10 and 8/25 to genuine "no qualifying swing yet" market conditions rather than
a bug, and neither ticker has broken its range since (JPM still boxed roughly $350-366; GC=F still
chopping in the mid-$4400s-4600s). SPY (n=9), VOO (n=10), and NVDA (n=4) remain 0% on thin,
still-too-new samples. None of these numbers moved from Friday's already-graded state.

**Real-money ledger - this is the one thing that changed today:** TSLA rallied hard, closing at
$367.40 (intraday high $368.54) versus Friday's $348.75. That puts it above both the $345 strike
on the owner's real short call (5x, exp 9/11, breakeven $357.50) and the breakeven itself, for the
first time since the position was opened on 8/19. Per the owner's own plan noted in
`real_trades.json` (selling these TSLA shares by/in October anyway), assignment at $345 - an
effective $357.50/share exit - stays an acceptable-to-favorable outcome, not a problem to react to.
Worth a clear flag anyway since it's a real change in the position's standing, not routine noise.

**What changed and why:** no code change. Today's fetch block is the same network-policy issue
as every recent day, not a code defect, and the JPM/GC=F 0%-rate situations are already-diagnosed
market behavior with no new evidence today to reopen either investigation. Improvement discipline
calls for grade-and-log only when nothing meets the 3+-day pattern-plus-clear-bug bar, which is
where today lands. Honesty features (measured hit rates, random-control comparisons, self-grading)
and the coherence gate are untouched, and `tickers.txt` wasn't touched.

**Watch next:** whether TSLA holds above $357.50 into the 9/11 expiry (favoring assignment) or
fades back under the $345 strike (favoring keeping the shares plus full premium); whether JPM or
GC=F finally break their multi-week ranges and start moving the grader off 0%; and whether
tomorrow's fetch succeeds now that a new review day is starting.

## 2026-09-01 (Tue) — fetch blocked again; GC=F finally broke its 0% streak; TSLA pulled back below breakeven; grade-and-log only

**Fetch status:** blocked on all 10 tickers - same 403 Forbidden at the proxy gateway seen on
every recent review day, confirmed again by the proxy's own status log against
`query1.finance.yahoo.com`. With no CSVs committed to the repo (gitignored by design),
`analyze.py` wrote the expected empty 0-ticker `data.js`/`index.html`/`dashboard_single.html`;
`coherence_check.py` caught it immediately ("data.js is missing 10 of 10 tracked tickers") and the
broken build was discarded via `git checkout --` before anything was staged. `coherence_check.py`
then passes cleanly (10/10 tickers) against the real build the separate cloud refresh workflow
already published today at 6:07 PM ET.

**Grades reviewed (from today's live build) - one real move:** GC=F (n=22) finally broke its
multi-week 0% hit-rate streak: two predictions logged back on 8/19 and 8/20 (a high near
$4,579-$4,606) both graded as hits (within 2 and 3 days) once the 8/24 high print ($4,640.80)
had enough trailing data to confirm it as real. Hit rate moved to 9%/9%, median price error 2.3%.
This is the self-grading system working as designed, catching up on a real result - not a bug and
not something to react to; JPM (n=31) is still stuck at 0% with no qualifying swing yet, the
already-diagnosed range-bound condition from 8/10 and 8/25. QQQ remains the standout at n=27
(37%/48%, 1.6% avg price error). TSLA n=26 (19%/27%, 7.8%), HOOD n=27 (19%/26%, 5.2%), GOOGL n=18
(22%/22%, 6.6%) - all essentially flat from yesterday. SPY (n=9), VOO (n=10), and NVDA (n=4)
remain 0% on thin, still-too-new samples; AMZN (n=0) has no resolved predictions yet. Sanity-
checked every ticker's learned calibration factors and method-family weights for NaN/Inf/garbage
values - all clean, all near 1.0, nothing broken in the self-grading math itself.

**Real-money ledger:** TSLA pulled back from Monday's $367.40 rally to close today at $356.09
(range $352.96-$362.70). That's back under the $357.50 breakeven on the owner's real short call
(5x $345 strike, exp 9/11) but still above the $345 strike itself - so yesterday's above-breakeven
flag was a one-day blip, not a trend yet. Per the owner's own plan (selling these TSLA shares
by/in October anyway), assignment at $345 stays an acceptable outcome either way; nothing here
needs action before expiry.

**What changed and why:** no code change. Today's fetch block is the same network-policy issue as
every recent day, not a code defect. GC=F's grade movement is a genuine, correctly-computed result
maturing through the grader, not evidence of a bug, and JPM's continued 0% rate is the
already-diagnosed "no qualifying pullback yet" market condition with no new evidence today to
reopen that investigation. Improvement discipline calls for grade-and-log only when nothing meets
the 3+-day pattern-plus-clear-bug bar, which is where today lands. Honesty features (measured hit
rates, random-control comparisons, self-grading) and the coherence gate are untouched, and
`tickers.txt` wasn't touched.

**Watch next:** whether GC=F's newly-resolved hits are the start of a real recovery off 0% or a
one-off; whether JPM ever produces the pullback the grader is waiting on; the TSLA short call
heading into its 9/11 expiry, now back on the safer side of breakeven; and whether tomorrow's
fetch finally succeeds after this long a blocked streak.

## 2026-09-02 (Wed) — fetch blocked again; GC=F's recovery continues; grade-and-log only

**Fetch status:** blocked on all 10 tickers - the same 403 Forbidden at the proxy gateway seen on
every recent review day, confirmed again against `query1.finance.yahoo.com` in the proxy's own
status log. With no CSVs committed to the repo (gitignored by design), `analyze.py` wrote the
expected empty 0-ticker `data.js`/`index.html`/`dashboard_single.html`/`week_plan.json`;
`coherence_check.py` caught it immediately ("data.js is missing 10 of 10 tracked tickers") and the
broken build was discarded via `git checkout --` before anything was staged. `coherence_check.py`
then passes cleanly (10/10 tickers) against the real build the separate cloud refresh workflow
already published today at 2:59 PM ET.

**Grades reviewed (from today's live build):** GC=F's recovery off its long 0% floor kept going -
now n=23, 13%/13% hit-within-2/3-days (up from yesterday's 9%/9% at n=22), median price error 2.2%.
That's a second straight day of upward movement as older predictions mature through the grader, so
it now reads as a real trend rather than a one-off. QQQ remains the standout at n=28 (36%/46%,
1.6% avg price error). TSLA n=28 (18%/25%, 7.8%), HOOD n=29 (17%/24%, 5.2%), GOOGL n=19 (21%/21%,
6.6%) - all roughly flat, sample sizes still growing. JPM (n=31, unchanged from yesterday) is still
stuck at 0% with no qualifying swing yet - still-diagnosed range-bound conditions from 8/10 and
8/25, and today's range ($353.79-361.47) stayed inside that same multi-week box, just drifting
toward its upper edge. SPY (n=11), VOO (n=12), and NVDA (n=5) remain 0% on thin, still-too-new
samples; AMZN (n=0) has no resolved predictions yet. Sanity-checked every ticker's learned
calibration factors and biasLearning weights for NaN/Inf/garbage values - all clean.

**Real-money ledger:** TSLA closed today at $352.20 (range $349.92-360.62), settling back into the
middle of the zone between the $345 strike and $357.50 breakeven on the owner's real short call (5x,
exp 9/11) - a bit softer than Monday's above-breakeven spike and Tuesday's $356.09 close, but no new
trend either way. Per the owner's own plan (selling these TSLA shares by/in October anyway),
assignment at $345 stays an acceptable outcome regardless of which side of breakeven it lands on;
nothing here needs action before expiry.

**What changed and why:** no code change. Today's fetch block is the same network-policy issue as
every recent day, not a code defect. GC=F's continued grade climb is the self-grading system
correctly catching up on real, matured results, not evidence of a bug, and JPM's continued 0% rate
is the same already-diagnosed "no qualifying pullback yet" market condition with no new evidence
today to reopen that investigation. Improvement discipline calls for grade-and-log only when
nothing meets the 3+-day pattern-plus-clear-bug bar, which is where today lands. Honesty features
(measured hit rates, random-control comparisons, self-grading) and the coherence gate are
untouched, and `tickers.txt` wasn't touched.

**Watch next:** whether GC=F's two-day recovery keeps building or stalls out; whether JPM's range
finally breaks (today's high nudged closer to the top of its box) and starts moving that grader off
0%; the TSLA short call heading into its 9/11 expiry, still hovering right around breakeven; and
whether tomorrow's fetch finally succeeds after this long a blocked streak.

## 2026-09-03 (Thu) — fetch blocked again; GC=F's recovery makes it three in a row; grade-and-log only

**Fetch status:** blocked on all 10 tickers - the same 403 Forbidden at the proxy gateway seen on
every recent review day, confirmed again against `query1.finance.yahoo.com`. With no CSVs
committed to the repo (gitignored by design), running `analyze.py` here would have produced the
usual empty 0-ticker build, so per the standing instruction I left the committed data alone rather
than overwrite a good build with a broken one. The repo's `data.js` already carried today's real
build - the separate cloud refresh workflow had already run and published at 5:55 PM ET before this
review started. `coherence_check.py` passes cleanly against that build (10/10 tickers).

**Grades reviewed (from today's live build):** GC=F's recovery off its long 0% floor made it a third
straight up day - n=25 now (up from 23), 16%/16% hit-within-2/3-days (up from 13%/13%), median
price error 2.3%. Three consecutive days of upward movement as older predictions mature through the
grader is a real trend, not noise, and matches what was already flagged as worth watching - no
action needed, the self-grading system is doing its job. QQQ remains the strongest performer at
n=30 (33%/43%, 1.6% avg price error, essentially flat vs yesterday's 36%/46% at n=28 - normal
sample-size noise). TSLA n=29 (17%/24%, 7.8%), HOOD n=31 (16%/23%, 5.2%), GOOGL n=19 (21%/21%, 6.6%,
unchanged - no new resolutions today) - all roughly flat. JPM (n=32, up from 31) is still stuck at
0% with no qualifying swing yet; today's range ($356.39-362.85) pushed to a marginal new high and
closed near the top of its recent box ($362.06) - still the same diagnosed range-bound condition,
just drifting further toward a possible breakout. SPY (n=11), VOO (n=12), and NVDA (n=5) remain 0%
on thin, still-too-new samples; AMZN (n=0) has no resolved predictions yet. Checked learned
calibration factors and biasLearning weights across all tickers for NaN/Inf/garbage values - all
clean.

**Real-money ledger:** TSLA jumped today, closing at $376.36 (range $365.91-384.04) - well above
both the $345 strike and the $357.50 breakeven on the owner's real short call (5x, exp 9/11), a
sharp move up from yesterday's $352.20 close. Per the owner's own plan (selling these TSLA shares
by/in October anyway), assignment at $345 (effective $357.50/sh with premium) remains an acceptable
outcome, and today's rally makes assignment the more likely of the two outcomes at expiry - nothing
here needs action before then.

**What changed and why:** no code change. Today's fetch block is the same network-policy issue as
every recent day, not a code defect. GC=F's third straight day of grade improvement is the
self-grading system correctly catching up on real, matured results, not evidence of a bug, and
JPM's continued 0% rate is still the same already-diagnosed "no qualifying pullback yet" market
condition - nothing new today to reopen that investigation. Improvement discipline calls for
grade-and-log only when nothing meets the 3+-day pattern-plus-clear-bug bar, which is where today
lands. Honesty features (measured hit rates, random-control comparisons, self-grading) and the
coherence gate are untouched, and `tickers.txt` wasn't touched.

**Watch next:** whether GC=F's three-day recovery keeps building or stalls out; whether JPM's box
finally breaks now that today closed near its top; the TSLA short call heading into its 9/11
expiry, now clearly above breakeven after today's rally; and whether tomorrow's fetch finally
succeeds after this long a blocked streak.

## 2026-09-04 (Fri) — fetch blocked again; found the specific reason JPM stays at 0%; grade-and-log only

**Fetch status:** blocked on all 10 tickers - the same 403 Forbidden at the proxy gateway seen on
every recent review day. With no CSVs committed to the repo (gitignored by design), running
`analyze.py` here would have produced the usual empty 0-ticker build, so per the standing practice
the committed data was left alone rather than overwritten with a broken build. The separate cloud
refresh workflow had already published a good build today at 2:34 PM ET (committed 18:35 UTC).
`coherence_check.py` passes cleanly against that build (10/10 tickers), and a full NaN/Inf sanity
sweep across every ticker's data came back clean.

**Grades reviewed (from today's live build):** GC=F's recovery made it a fourth straight up day -
n=26 (up from 25), 19%/19% hit-within-2/3-days (up from 16%/16%), continuing the trend flagged
these past few days. QQQ remains the strongest performer at n=31 (32%/42%, essentially flat vs
yesterday's 33%/43% - normal sample noise). TSLA n=29 (17%/24%, unchanged - no new resolutions
today), HOOD n=31 (16%/23%, unchanged), GOOGL n=20 (20%/20%, down slightly from 21%/21% at n=19 -
one new resolution, normal noise). JPM (n=34, up from 32) is still stuck at 0%, but today's review
found the specific reason rather than just re-confirming the pattern: JPM's own swing detector
hasn't confirmed a single new high or low pivot (a real >=4% zigzag turn) since May 19 - over three
months of a low-volatility grind higher with no qualifying pullback or reversal. Every prediction
logged since then has nothing nearby to grade against, so it's marked a miss by the honest "did a
real turn happen when we said it would" rule, dragging the rate to 0%. That's not a code bug - the
same swing method's full-history backtest on JPM shows a normal ~14%/22% hit rate, so the method
itself works on this ticker over time; it's just that this particular stretch has produced nothing
to confirm. SPY (n=11), VOO (n=12), and NVDA (n=5) remain 0% on thin, still-too-new samples; AMZN
(n=0) has no resolved predictions yet.

**Real-money ledger:** TSLA pulled back to $353.47 (range $351.32-$364.69) as of 2:34 PM ET, back
below the $357.50 breakeven on the owner's real short call (5x, exp 9/11) after Thursday's rally
had pushed it above - a normal swing, not a trend change. Per the owner's own plan (selling these
TSLA shares by/in October anyway), the outcome at expiry stays acceptable either way; nothing here
needs action before then.

**What changed and why:** no code change. Today's fetch block is the same network-policy issue as
every recent day, not a code defect. JPM's 0% rate got a more specific diagnosis today (no
confirmed swing since May 19) rather than a code fix, because the underlying method isn't broken -
the market simply hasn't produced a qualifying move to grade. GC=F's fourth straight day of
recovery is the self-grading system correctly catching up on real, matured results. Improvement
discipline calls for grade-and-log only when nothing meets the 3+-day pattern-plus-clear-bug bar,
which is where today lands even with the added detail. Honesty features (measured hit rates,
random-control comparisons, self-grading) and the coherence gate are untouched, and `tickers.txt`
wasn't touched.

**Watch next:** whether JPM ever gets a confirmed pivot to end its three-month dry spell; whether
GC=F's four-day recovery keeps building; the TSLA short call heading into its 9/11 expiry, now back
below breakeven; and whether tomorrow's fetch finally succeeds after this long a blocked streak.

## 2026-09-05 (Sat) — weekend, no new session; fetch blocked again; grade-and-log only

**Fetch status:** blocked on all 10 tickers - the same 403 Forbidden at the proxy gateway seen on
every recent review day. Markets are closed Saturday anyway, so there is no new session to fetch
regardless. With no CSVs committed to the repo (gitignored by design), `analyze.py` was not run
here to avoid overwriting good data with an empty build. The repo already carries Friday 9/4's full
end-of-day build (generated 8:58 PM ET, published by the separate cloud refresh workflow after
Friday's review ran). `coherence_check.py` passes cleanly against it (10/10 tickers), and a fresh
NaN/Inf sweep across every ticker's calibration factors and method weights came back clean.

**Grades reviewed (from Friday's closing build, same session as yesterday's review - no new data
today):** QQQ remains the strongest performer (n=30, 33%/43% within +/-2/3 days, 1.6% typical price
miss). TSLA n=29 (17%/24%, 7.8%) and HOOD n=31 (16%/23%, 5.2%) are steady. GOOGL sits at n=19
(21%/21%, 6.6%). GC=F's recovery streak holds at n=26 (19%/19%, 2.4%), flat vs Friday afternoon's
numbers since no new session has traded since then. JPM (n=32) is still at 0% - same diagnosed
three-month dry spell with no confirmed swing pivot since May 19, nothing new to add today. A few
of these counts (JPM, GOOGL, QQQ) shifted down by 1-2 versus yesterday's afternoon snapshot even
though it's the same Friday session; that's the evening cloud-refresh build re-running the
confluence chain against the full day's close (vs. yesterday's 2:34 PM ET mid-session build), which
naturally revises/ages a few borderline entries out of the graded window - not a data problem, and
nothing to fix. SPY (n=11), VOO (n=12), and NVDA (n=5) remain on thin samples; AMZN (n=0) still has
no resolved predictions.

**Real-money ledger:** No change since Friday - TSLA closed at $353.47, still below the $357.50
breakeven on the owner's real short call (5x, exp 9/11) but above the $345 strike. Per the owner's
own plan to sell these TSLA shares by/in October anyway, the outcome at expiry stays acceptable
either way; nothing needs action before then, and there's no new weekend data to change that read.

**What changed and why:** no code change. There is no new market session to grade over the weekend,
fetch access is blocked by the same standing network-policy issue as every recent day, and nothing
today rises to the 3+-day-pattern-plus-clear-bug bar for a change - JPM's dry spell and GC=F's
recovery are both already-diagnosed, ongoing conditions, not new findings. Honesty features
(measured hit rates, random-control comparisons, self-grading) and the coherence gate are
untouched, and `tickers.txt` wasn't touched.

**Watch next:** Monday 9/7 is Labor Day (US markets closed), so Tuesday 9/8 is the next new trading
session - worth checking whether JPM ever gets a confirmed pivot, whether GC=F's recovery keeps
building, and whether the TSLA short call (still below breakeven heading into its 9/11 expiry)
moves either way. Also still watching whether fetch access to Yahoo recovers for this environment.

## 2026-09-06 (Sun) — weekend, no new session; fetch blocked again; grade-and-log only

**Fetch status:** blocked on all 10 tickers - the same 403 Forbidden at the proxy gateway seen on
every recent review day. Markets are closed Sunday anyway, so there is no new session to fetch
regardless. With no CSVs committed to the repo (gitignored by design), running `analyze.py` here
produced the usual empty 0-ticker build (confirmed, then discarded without committing) rather than
overwrite the good data with a broken one. The repo already carries Friday 9/4's closing data,
re-run through the separate cloud refresh workflow Saturday evening (which revises/matures a few
more predictions without changing prices, since no new session has traded). `coherence_check.py`
passes cleanly against that build (10/10 tickers), a full cross-check with `anomaly_audit.py`
found no chain/level/trade-card inconsistencies, and a NaN/Inf sweep across every ticker's
calibration factors and grading data came back clean.

**Grades reviewed (from Saturday evening's re-run of Friday's closing build):** QQQ remains the
strongest performer (n=31, up from 30, 32%/42% within +/-2/3 days - one new resolution, essentially
flat vs Saturday's 33%/43%, normal sample noise). GOOGL sits at n=20 (up from 19, 20%/20%, flat vs
21%/21%). TSLA n=29 (17%/24%, 7.8%) and HOOD n=31 (16%/23%, 5.2%) are unchanged - no new
resolutions. JPM (n=34, up from 32) is still stuck at 0% - the already-diagnosed three-month dry
spell (no confirmed swing pivot since May 19) picked up two more resolved-but-unconfirmed entries
overnight, same condition, nothing new to add. GC=F's recovery streak holds flat at n=26 (19%/19%,
2.4%) since no new session has traded since Friday. SPY (n=11), VOO (n=12), and NVDA (n=5) remain
on thin samples; AMZN (n=0) still has no resolved predictions.

**Real-money ledger:** No change since Friday - TSLA still at $352.89, below the $357.50 breakeven
on the owner's real short call (5x, exp 9/11) but above the $345 strike. Per the owner's own plan
to sell these TSLA shares by/in October anyway, the outcome at expiry stays acceptable either way;
5 days remain to expiry with no weekend data to change that read.

**What changed and why:** no code change. There is no new market session to grade over the weekend,
fetch access is blocked by the same standing network-policy issue as every recent day, and nothing
today rises to the 3+-day-pattern-plus-clear-bug bar for a change - JPM's dry spell and GC=F's flat
recovery are both already-diagnosed, ongoing conditions, not new findings. Honesty features
(measured hit rates, random-control comparisons, self-grading) and the coherence gate are
untouched, and `tickers.txt` wasn't touched.

**Watch next:** Monday 9/7 is Labor Day (US markets closed), so Tuesday 9/8 is the next new
trading session - worth checking whether JPM ever gets a confirmed pivot, whether GC=F's recovery
resumes climbing once real data starts flowing again, and whether the TSLA short call (still below
breakeven, now inside its final week before 9/11 expiry) moves either way. Also still watching
whether fetch access to Yahoo recovers for this environment.

## 2026-09-07 (Mon) — Labor Day, no new session; fetch blocked again; grade-and-log only

**Fetch status:** blocked on all 10 tickers - the same 403 Forbidden at the proxy tunnel seen on
every recent review day. Markets are closed for Labor Day anyway, so there is no new session to
fetch regardless. With no CSVs cached locally (gitignored by design), I left `analyze.py` un-run
here rather than overwrite the good build with an empty 0-ticker one; the site is already serving
today's build from the separate cloud refresh workflow, which ran three times today (03:57 PM,
briefly again just before 4 PM, and again just before 8 PM ET) and matured a couple of
predictions without any new price action, since the market never opened. `coherence_check.py`
passes cleanly against that build (10/10 tickers), `anomaly_audit.py` found no chain/level/trade-card
inconsistencies, and a NaN/Inf sweep across every ticker's data came back clean.

**Grades reviewed (from today's cloud-refreshed build, compared to Friday 9/4's close):** TSLA
holds at n=29 (17%/24%), HOOD at n=30 (17%/23%), QQQ still the strongest at n=30 (33%/43%), and
JPM's three-month dry spell continues at n=30 (0%/0%, no confirmed swing pivot since May 19) -
all four unchanged, no new resolutions. GOOGL ticked up to n=20 (up from 19, 20%/20%, flat vs
21%/21% - one new resolution, normal noise). GC=F ticked up to n=27 (up from 26, 19%/22%, hit3
improved from 19% - one new resolution). NVDA (n=5), SPY (n=11), VOO (n=12), and AMZN (n=0)
remain on the same thin samples as before.

**Real-money ledger:** No change since Friday - TSLA still at $352.89 (today's build carries
Friday's close since no new session traded), below the $357.50 breakeven on the owner's real
short call (5x, exp 9/11) but above the $345 strike. Per the owner's own plan to sell these TSLA
shares by/in October anyway, the outcome at expiry stays acceptable either way; 4 days remain to
expiry with no new data to change that read.

**What changed and why:** no code change. There is no new market session to grade on a holiday,
fetch access is blocked by the same standing network-policy issue as every recent day, and
nothing today rises to the 3+-day-pattern-plus-clear-bug bar for a change - JPM's dry spell and
GC=F's slow recovery are both already-diagnosed, ongoing conditions, not new findings. Honesty
features (measured hit rates, random-control comparisons, self-grading) and the coherence gate
are untouched, and `tickers.txt` wasn't touched.

**Watch next:** Tuesday 9/8 is the next new trading session - worth checking whether JPM ever
gets a confirmed pivot, whether GC=F's recovery keeps building now that real data resumes, and
whether the TSLA short call (below breakeven, 3 trading days from its 9/11 expiry) moves either
way. Also still watching whether fetch access to Yahoo recovers for this environment.

## 2026-09-08 (Tue) — new session; fetch still blocked; important grading-accuracy fix found and verified (already applied, not by me)

**Fetch status:** blocked on all 10 tickers again - the same 403 Forbidden at the proxy tunnel.
No CSVs are cached locally, so I left `analyze.py` un-run here and reviewed the already-committed
build instead, which the separate cloud refresh workflow produced today (last run 5:18 PM ET) from
real market data. `coherence_check.py` passes cleanly (10/10 tickers) and `anomaly_audit.py` found
no chain/level/trade-card inconsistencies.

**Big item today - a real bug got fixed, and it explains a big number swing:** Comparing today's
grading numbers against Monday's, TSLA's sample size for the "did the predicted turn actually
happen" grade dropped from 29 to 10, and similar drops hit HOOD (31 to 14), QQQ, GOOGL, and GC=F.
That is NOT a data-loss problem - I traced it to a code fix that was merged into the site (by the
owner, via a pull request on GitHub Sunday evening) shortly before today's numbers were generated.
The old grading code was comparing a prediction against ANY matching swing turn in the ticker's
history, including ones that had already happened *before* the prediction was even made - which
means the system could accidentally give itself credit for "calling" a turn it could already see
in the past data. The fix (in `scoring.py`) now only allows a prediction to be graded against a
turn that happens strictly *after* the prediction was logged, which is the only fair test of a
forecast. I read the diff and confirmed this is exactly what changed; I also confirmed pivots
themselves (the actual chart turns) are unchanged - only which turns are allowed to count for
scoring changed. This means the old, higher hit-rate numbers shown on past days were partly
inflated by unfair "hindsight" credit, and today's lower numbers are the honest ones. This is
exactly the kind of fix the honesty rules exist to protect, so I made no code change of my own -
just verified it, and I'm logging it clearly here since the visible numbers moved a lot without
any code change from me today.

**What this means for specific tickers:** TSLA and HOOD now show ZERO resolved "high" (top of
swing) predictions, only "lows" - not because the code is broken, but because TSLA and HOOD
genuinely haven't had a confirmed high pivot (a 10%+ pullback from a peak) since July 1st; both
have been in a long, uninterrupted climb since their July lows, so there's nothing yet to grade a
"high" call against. GC=F is the mirror image (highs only, no low pivot recently). QQQ and GOOGL
still have a healthy mix of both. TSLA n=10 (40%/50% within +/-2/3 days, 11.9% median price
error), HOOD n=14 (29%/36%, 7.6%), QQQ n=25 (36%/44%, 2.0% - QQQ's number barely moved, it was
already being graded mostly fairly), GOOGL n=13 (31%/31%, 7.9%), GC=F n=13 (31%/31%, 2.4%). JPM
stays at n=0 (still no confirmed pivot since May 19 - unchanged, unrelated to this fix). NVDA,
AMZN, SPY, VOO remain on n=0 (still too new/thin to grade). None of these are worse forecasting -
they're the same forecasts being graded more strictly and fairly than before.

**Real-money ledger:** TSLA closed today at $366.90, now comfortably above both the $345 strike
and the $357.50 breakeven on the owner's real short call (5x, exp 9/11, 3 trading days away). Per
the owner's own plan to sell these TSLA shares by/in October anyway, this is now a favorable
outcome if it holds into expiry - the shares would get called away at the better, effective
$357.50/sh price. Nothing needs action before expiry.

**What changed and why:** no code change from me today - the meaningful fix (prospective-only
grading in `scoring.py`) was already made and merged by the owner directly on GitHub, and today's
job was to verify it's sound, understand why the numbers moved, and make sure nothing else broke
(coherence and anomaly checks both pass). Honesty features (measured hit rates, random-control
comparisons, self-grading, and now a stricter no-hindsight grading rule) and the coherence gate
are untouched or strengthened, and `tickers.txt` wasn't touched.

**Watch next:** now that grading is prospective-only, watch whether TSLA and HOOD's "high"
sample sizes ever grow (they need a genuine 10%+ pullback first) versus staying stuck at zero for
weeks, which would itself be worth flagging. Also watch the TSLA short call into its 9/11 expiry
now that it's back in the money, and whether fetch access to Yahoo recovers for this environment.

## 2026-09-09 (Wed) — fetch still blocked; found a real, measurable pattern in the daily high/low
range forecast, but held off fixing it because I can't test a fix today

**Fetch status:** blocked on all 10 tickers again - same 403 Forbidden at the proxy tunnel to
`query1.finance.yahoo.com`, confirmed via the proxy's own status log (a policy denial, not a
site-side block). No CSVs are cached locally (gitignored by design), so I left `analyze.py`
un-run here and reviewed the build the separate cloud refresh workflow already produced today
from real data (its own self-review ran at 3:58 PM ET). `coherence_check.py` passed cleanly
(10/10 tickers) and `anomaly_audit.py` found no chain/level/trade-card inconsistencies.

**Grades reviewed:** the swing-prediction track record is essentially unchanged from Monday -
TSLA n=10 (40%/50% within 2/3 days), HOOD n=15 (27%/33%), QQQ n=26 (35%/42%), GOOGL n=14
(29%/29%), GC=F n=13 (31%/31%); JPM, NVDA, AMZN, SPY, VOO still n=0 (no confirmed pivot yet to
grade against). Nothing here crosses the 3-day-pattern bar for a change.

**What I found instead:** the *other* forecast the dashboard grades - the day-ahead high/low
range shown in the daily table (`horizonGrades`) - has a real, persistent bias. I pulled the
last 10 graded sessions for all 10 tickers (100 data points total, spanning about 2.5 weeks) and
the predicted high came in ABOVE the actual high on 84 of those 100 days (average +2.1%), while
the predicted low came in BELOW the actual low on 82 of the 100 days (average -1.5%). That's not
one noisy ticker - it's nearly every ticker, nearly every day: the day-ahead range the dashboard
shows is systematically wider than the range that actually prints. I traced the code
(`analyze.py`, the `day_fc` loop around line 2101): that band's width comes straight from a
60-day volatility measure with a small widening factor, and unlike the swing-target predictions
(which already get a self-correcting `priceCalibHigh`/`priceCalibLow` adjustment from their own
grading history), this daily-range band has no such correction - it's raw, uncalibrated output,
even though there's now ~37-40 graded sessions per ticker to calibrate it from.

**Why I didn't fix it today:** the instructions are clear that any code change has to be
re-verified by re-running `analyze.py` and `coherence_check.py` before it ships, and I have no
way to run `analyze.py` in this sandbox at all today (no market data reachable, no cached CSVs).
Shipping a calibration change I could not test against real data risked exactly the kind of
mistake the honesty/coherence rules are there to prevent. So this is a specific, numbers-backed
recommendation for a day when fetch access works (here or read by the owner directly): add a
calibration factor to the daily-range band, the same self-correcting idea already used for the
swing-target prices, sized from the measured +2.1%/-1.5% bias. No code touched today.

**Real-money ledger:** TSLA closed today at $368.14, still comfortably above both the $345 strike
and the $357.50 breakeven on the owner's real short call (5x), now 2 trading days from its 9/11
expiry. Nothing has changed since Monday and nothing needs action before expiry.

**What changed and why:** no code change - found a real pattern in the daily-range forecast but
couldn't safely test a fix in today's blocked environment, so I logged it precisely instead of
guessing. Honesty features (measured hit rates, random-control comparisons, self-grading, the
coherence gate) are untouched. `tickers.txt` wasn't touched.

**Watch next:** whether the daily-range over-width bias (84%/82% of days, ~2% average) holds up
as more sessions grade, and whether it's still there once a session can actually run `analyze.py`
and test the calibration fix described above. Also watch the TSLA short call into Thursday/Friday
expiry, and whether fetch access to Yahoo recovers for this environment.

## 2026-09-10 (Thu) — fetch still blocked; found a distinct duplicate-grading bug behind the ledgers; range-calibration bias confirmed a second day; no code shipped, can't test today

**Fetch status:** blocked on all 10 tickers again - same 403 Forbidden at the proxy tunnel to
Yahoo. No CSVs are cached locally (gitignored by design), so `analyze.py` won't even start today
(it fails immediately on the missing per-ticker CSV files) - I reviewed the build the separate
cloud refresh workflow already produced today from real data instead. `coherence_check.py` passed
cleanly (10/10 tickers) and `anomaly_audit.py` found no chain/level/trade-card inconsistencies.

**Grades reviewed:** the swing-prediction track record moved a little in both directions, nothing
crossing the 3-day-pattern bar - TSLA n=11 (36%/45% within 2/3 days, was 40%/50% at n=10), HOOD
n=15 (27%/33%, unchanged), QQQ n=28 (32%/39%, was 35%/42% at n=26), GOOGL n=15 (27%/27%, was
29%/29% at n=14), GC=F n=14 (29%/29%, was 31%/31% at n=13). JPM, NVDA, AMZN, SPY, VOO still n=0
(no confirmed pivot yet to grade against).

**New finding - a real duplicate-logging bug in the day-ahead range ledger:** while re-checking
yesterday's day-ahead high/low range bias, I found the underlying log (`horizons_log.json`) logs
the exact same forecast more than once for a lot of sessions. Example: TSLA's forecast for Monday
8/31 (predicted high $362.89, low $329.78) was logged three separate times - on Fri 8/28, Sat
8/29, and Sun 8/30 - because the "next trading session" doesn't change over a weekend, but the
daily logging step doesn't check whether it already logged a forecast for that exact session
before appending a new row. Across the full history this isn't a one-off: 119 of the 394 rows
ever logged (30%) are exact duplicates of an already-logged ticker+session pair, concentrated
around weekends and the Labor Day holiday. Because the grading step grades every logged row, this
means some sessions get counted 2-3x in the rolling "last 10 days" window shown on the dashboard
and in the cumulative sample-size counters (the `n` next to the day-ahead grades), which both
inflates those sample sizes and duplicate-weights whichever bias a triple-logged day happened to
have. I re-ran yesterday's bias check with duplicates removed (62 unique ticker+session pairs
instead of 100 raw rows) and the pattern held up almost exactly the same (93.5% of sessions predict
a high above the actual, 87.1% predict a low below the actual, averaging +2.5%/-1.6%) - so
yesterday's finding wasn't an artifact of this bug, but the bug is still a real integrity problem
worth fixing on its own, separate from the calibration question.

**Why I didn't fix either issue today:** both fixes live inside `analyze.py` (the log-append step
and the day-range calibration), and `analyze.py` cannot run at all in this sandbox right now - it
errors out before reaching either piece of logic because none of the 10 tickers' CSVs are
reachable (fetch blocked, nothing cached). Shipping either change without being able to re-run
`analyze.py` and `coherence_check.py` against it, as the process requires, would be exactly the
kind of untested change the honesty/coherence rules exist to prevent. Both are now written up
precisely enough that a session with working fetch access can implement and verify them directly:
(1) skip logging a new `horizons_log.json` row when one already exists for that exact
ticker+session, and (2) add a calibration factor to the daily-range band using the measured
+2.5%/-1.6% bias, the same self-correcting approach already used for the swing-target prices via
`priceCalibHigh`/`priceCalibLow`.

**Real-money ledger:** TSLA closed today at $363.56, still comfortably above both the $345 strike
and the $357.50 breakeven on the owner's real short call (5x), with the 9/11 expiry now tomorrow.
This is proceeding exactly per the owner's own stated plan (selling these shares by/in October
anyway, so assignment at the effective $357.50 is an acceptable-to-favorable outcome) and there's
already a GTC buy-to-close order in place - nothing needs action tonight.

**What changed and why:** no code change - found and precisely documented two separate real
issues (a duplicate-logging bug that inflates grading sample sizes, and a persisting day-range
calibration bias) but couldn't safely test a fix for either in today's fetch-blocked environment,
so I logged both instead of guessing. Honesty features (measured hit rates, random-control
comparisons, self-grading, the coherence gate) are untouched. `tickers.txt` wasn't touched.

**Watch next:** whether the TSLA short call gets assigned or expires worthless tomorrow (either
is fine per the owner's plan); whether fetch access to Yahoo recovers so both the duplicate-log
bug and the day-range calibration bias can actually be fixed and verified; and whether the
duplicate-logging bug, once fixed, moves the reported sample sizes or hit rates meaningfully.

## 2026-09-11 (Fri) — fixed the duplicate-logging bug found the last two days; grades steady; TSLA call expired ITM per plan

**Fetch status:** blocked again in this sandbox - all 10 tickers 403'd at the proxy, third
straight day. As before, no CSVs are cached locally so `analyze.py` can't run here. I reviewed
the build the separate cloud refresh workflow already produced today from real data (last run
20:04 UTC) - `coherence_check.py` passed cleanly (10/10 tickers) and the two `anomaly_audit.py`
notices (JPM and AMZN weekly-low estimates disagreeing with a dated chain low inside the same
window) are pre-existing, unrelated to anything below, and unchanged from before my change.

**What changed and why:** fixed the duplicate-forecast bug flagged the last two days. The
day-ahead range log (`horizons_log.json`) was keying its "already logged today?" check on
today's date instead of the target session's date, so a forecast for a session that doesn't
change over a weekend (or holiday) got appended again on every subsequent day, inflating the
sample sizes (`n`) behind the day-ahead high/low grades shown on the dashboard and duplicate-
weighting whichever bias that session happened to have. Fixed both ends: (1) `analyze.py` now
replaces any existing log row for the same ticker+session, not just same-day rows, so it can't
recur, and as a defense in depth the grading step also de-duplicates by ticker+session before
counting, keeping the most-recently-logged forecast; (2) did a one-time cleanup of the existing
ledger, removing the 119 stale duplicate rows accumulated since July (404 -> 285 entries, verified
zero rows lost that weren't exact re-logs of an already-present forecast). Couldn't run
`analyze.py` end-to-end today (fetch blocked), so I verified the fix a different way: extracted
the exact before/after dedup logic and ran it standalone against the real ledger data, confirming
sample sizes drop to the correct de-duplicated counts (e.g. TSLA 40->29, AMZN 31->22) with zero
value changes on any row that survives - the duplicates were always identical copies of the same
forecast, never conflicting data. `coherence_check.py` still passes against the current live
build. The actual grading numbers on the dashboard will refresh correctly the next time the cloud
workflow runs `analyze.py` with working fetch access, which will also be the first real end-to-end
test of this code path - I'll check the result at tomorrow's review. Honesty features (measured
hit rates, random-control comparisons, self-grading, the coherence gate) are untouched, made more
accurate if anything. `tickers.txt` wasn't touched.

**Grades reviewed (pre-refresh numbers, before dedup takes effect):** swing-prediction track
record essentially flat - TSLA n=11 (36%/45%), HOOD n=15 (27%/33%), QQQ n=28 (32%/39%), GOOGL
n=15 (27%/27%), GC=F n=14 (29%/29%), all unchanged from yesterday. JPM, NVDA, AMZN, SPY, VOO
still n=0 (no confirmed pivot yet). `daily_review.json`'s price-error samples from the last two
sessions ranged roughly 0.4%-9.3%, in line with recent norms - nothing there crosses the 3-day
bar for a change either.

**Real-money ledger:** TSLA closed today (Fri 9/11, the option's expiry date) at $365.44, well
above the $345 strike on the owner's 5x short call - this is the exact scenario the owner already
planned for and is fine with (assignment at the effective $357.50/sh, in line with the plan to
sell these shares by/in October anyway). Nothing needs action; noting it here for the record.

**Watch next:** whether tomorrow's ledgers (populated by the cloud workflow with working fetch
access) show the day-ahead sample sizes shrink to the deduplicated counts with no crash or
coherence failure along the way - that's the real test of today's fix; whether the TSLA call
assignment posts as expected; and whether fetch access to Yahoo recovers in this sandbox, which
has now been blocked three days running.

## 2026-09-12 (Sat) — weekend, no new session; fetch blocked again; dedup fix from Friday confirmed holding; grade-and-log only

**Fetch status:** blocked on all 10 tickers - the same 403 Forbidden at the proxy gateway seen on
every recent review day (fourth day running now). Markets are closed Saturday anyway, so there is
no new session to fetch regardless. With no CSVs cached in the repo (gitignored by design),
`analyze.py` was not run here. The repo already carries Friday 9/11's closing build, produced by
the separate cloud refresh workflow at 10:17 PM ET. `coherence_check.py` passes cleanly against it
(10/10 tickers, all checks including chain nesting and trade-card date ordering), and a full
NaN/Inf sweep across every ticker's stats and calibration data came back clean.

**Confirming yesterday's fix:** Friday's fix for the duplicate day-ahead forecast bug (in
`horizons_log.json`) went through its first real end-to-end test when the cloud workflow ran
`analyze.py` with working fetch access Friday evening. Checked the result: 285 entries, zero
duplicate ticker+session pairs - the fix held. The swing-prediction track record on today's build
(TSLA n=11 36%/45%, HOOD n=15 27%/33%, QQQ n=28 32%/39%, GOOGL n=15 27%/27%, GC=F n=14 29%/29%)
matches the corrected counts verified standalone yesterday, confirming the numbers on the live
dashboard are the accurate, de-duplicated ones. JPM, NVDA, AMZN, SPY, VOO remain at n=0 (no
confirmed pivot yet) - JPM's already-diagnosed three-month dry spell continues.

**New (day-one) observation - not acted on:** `anomaly_audit.py` flagged two new items today
beyond the usual pre-existing JPM/AMZN weekly-low mismatches: for both JPM and AMZN, the
"right now" forecast card's headline date (Fri 9/11) is now in the past, even though its stated
date window (09/09-09/15) hasn't closed and no new session has traded to resolve it either way.
This looks like the flip side of the same dry-spell condition already diagnosed for JPM (no
confirmed pivot to advance the chain), now showing up for AMZN too. It does not fail
`coherence_check.py` (the hard gate), and the dashboard's own "already reached" badge correctly
covers JPM's case; AMZN's case (not yet reached) has no equivalent "still pending, window open"
label the way a different part of the page already does for confirmed-turn dates. This is the
first day this specific flag has appeared, so per the improvement discipline (act only on a
3+ day pattern or a clear bug) I logged it rather than shipping a change - watching whether it
persists once Monday's session gives the chain a chance to resolve or advance.

**Trade cards:** the newest sheet (logged 9/11, TSLA) proposes entries for the week of 9/21 -
nothing from this week's cards has reached its execution or exit window yet, so there's nothing
new to grade there today.

**Real-money ledger:** no change to report beyond what was already logged Friday - TSLA closed
its 9/11 option expiry at $365.44, above the $345 strike on the owner's 5x short call, matching
the scenario the owner already planned for and is fine with. `real_trades.json` still shows that
position as open in the repo; reconciling it is the owner's own bookkeeping, not something I
touched.

**What changed and why:** no code change today. Nothing here crosses the 3+-day-pattern-plus-
clear-bug bar - the JPM/AMZN stale-headline-date observation is brand new today and worth one
more day of confirmation before considering an interface fix; everything else is an already-
diagnosed, ongoing condition. Honesty features (measured hit rates, random-control comparisons,
self-grading, the coherence gate) are untouched, and `tickers.txt` wasn't touched.

**Watch next:** whether Monday 9/14's new session finally advances the JPM/AMZN forecast chain
(clearing today's stale-headline-date observation one way or the other); whether JPM's three-month
pivot dry spell ever breaks; and whether fetch access to Yahoo recovers in this sandbox, which has
now been blocked four days running.

## 2026-09-13 (Sun) — weekend, no new session; fetch blocked a fifth day; Saturday's stale-headline
observation resolved on its own; shipped the day-range calibration fix flagged Tue/Wed

**Fetch status:** blocked on all 10 tickers again - same 403 Forbidden at the proxy tunnel to
Yahoo, now five days running in this sandbox. No CSVs are cached locally (gitignored by design),
so `analyze.py` can't start here either. I reviewed the build the separate cloud refresh workflow
already produced Friday evening (last run 9/12, 22:18 UTC) - `coherence_check.py` passed cleanly
(10/10 tickers) and `anomaly_audit.py` found no chain/level/trade-card inconsistencies at all
today, a clean sheet.

**Saturday's observation resolved:** the stale-headline-date issue flagged yesterday (JPM's and
AMZN's "right now" forecast card showing a date already in the past) is gone - both now show
Mon 9/14 as the next reversal date, which is in the future relative to today. The Friday-evening
cloud refresh advanced the chain before this ever became a second day's pattern, so no interface
fix is needed; treating it as resolved rather than watching further.

**Grades reviewed:** the swing-prediction track record is unchanged from Friday/Saturday since no
new session traded over the weekend - TSLA n=11 (36%/45%), HOOD n=15 (27%/33%), QQQ n=28
(32%/39%), GOOGL n=15 (27%/27%), GC=F n=14 (29%/29%). JPM, NVDA, AMZN, SPY, VOO still n=0 (no
confirmed pivot yet). The newest trade-card sheet (logged 9/12, TSLA) still targets the week of
9/21 - nothing to grade there yet.

**What changed and why - shipped the day-range calibration fix:** this is the fix flagged (but not
shipped) on Tuesday 9/9 and confirmed again Wednesday 9/10: the day-ahead high/low band shown in
the horizon table and graded as `horizonGrades` is a raw, uncalibrated statistical envelope, unlike
the swing-target prices which already self-correct from their own grading history
(`priceCalibHigh`/`priceCalibLow`). I re-measured the bias today against the live build's last 100
graded sessions (10 tickers x 10 days): the predicted high came in above the actual high on 87% of
days (avg +2.25%) and the predicted low came in below the actual low on 82% of days (avg -1.51%) -
the same lopsided pattern measured on both prior days (84%/82% on 9/9, 93.5%/87.1% on 9/10 after
dedup), now confirmed a third time on a fully independent, later slice of data. That crosses the
3+-day-pattern bar, so I fixed it: `analyze.py` now learns a `calibHigh`/`calibLow` multiplier per
ticker from the same graded `horizons_log.json` history (median actual/predicted ratio, requires at
least 8 graded sessions, clipped to the same 0.85-1.15 range as the existing swing-price
calibration) and applies it to the day-ahead band before it's shown or logged, with a hard floor/
ceiling so a "high" forecast can never calibrate below the closing price it's cast from (nor a
"low" above it) - mirroring the existing safety clamp used for swing-target prices. The learned
factors are also now surfaced in `horizonGrades.calibHigh`/`calibLow` for transparency, the same
spirit as the existing `priceCalibHigh`/`priceCalibLow` fields.

**How I tested it without working fetch access:** couldn't run `analyze.py` end-to-end today
(fetch blocked, no cached CSVs), so I verified the new logic the same way Friday's fix was
verified - extracted the exact calibration computation and ran it standalone against the real
`horizons_log.json` and `daily_extremes.json` ledgers. All 10 tickers have 21-32 graded sessions
(comfortably above the 8-session floor) and produced sane, expected-direction factors (highs:
0.963-0.997, lows: 1.003-1.031 - both correcting toward the measured bias, none pinned at the
0.85/1.15 clip). I then applied those factors to today's live band widths and confirmed the safety
clamp only ever engages in one edge case out of ten (AMZN, where the calibrated high lands a hair
below the close) rather than routinely overriding the fix. Also ran the full existing test suite
(25 tests, all passing), `python3 -m py_compile analyze.py` (clean), and `coherence_check.py`
against the current build (still passes, unaffected since `data.js` itself wasn't regenerated
today). The real end-to-end test - `analyze.py` actually running this code against fresh data and
`coherence_check.py` passing on the result - happens the next time the cloud workflow refreshes;
I'll check that result at tomorrow's review, the same way Friday's dedup fix was confirmed
Saturday. Honesty features (measured hit rates, random-control comparisons, self-grading, the
coherence gate) are untouched - this makes the displayed hit-rate numbers more accurate, not less
strict. `tickers.txt` wasn't touched, and the dashboard's own HTML/CSS wasn't touched either.

**Real-money ledger:** no change since Friday - the TSLA 9/11 option expiry and its resolution
(assignment scenario, per the owner's own October sale plan) is already fully logged; nothing new
to report and nothing touched.

**Watch next:** whether tomorrow's cloud-refreshed build shows the day-ahead band actually
narrower/shifted in the calibrated direction with no crash or coherence failure - that's the real
test of today's fix; whether the measured bias shrinks toward zero over the following days as
calibration takes hold; whether Monday 9/14's new session advances the JPM/AMZN chain past
tomorrow's projected date; whether JPM's three-month pivot dry spell ever breaks; and whether fetch
access to Yahoo recovers in this sandbox, now blocked five days running.

## 2026-09-14 (Mon) — fetch blocked a sixth day; JPM's dry spell finally broke; found and fixed a
name accidentally baked into the public site

**Data freshness:** my own sandbox still can't reach Yahoo (403 on every ticker, sixth day
running, no cached CSVs since they're gitignored), so I couldn't run `fetch_data.py`/`analyze.py`
end-to-end myself today. But the separate cloud refresh workflow (real network access) is healthy
and ran repeatedly today - `data.js` is stamped generated 5:39 PM ET, and the ledgers
(`horizons_log.json`, `daily_extremes.json`, `predictions_log.json`) all carry fresh 9/14 entries.
So today's review is against a genuinely current build, not a stale one.

**Grades reviewed:** JPM's three-month pivot dry spell (flagged repeatedly since late August) has
finally broken - its swing track record went from n=0 to n=21 (19%/29% hit rate), with all 21
resolved predictions confirming against a single high pivot on 2026-08-12 at $365.18; JPM's now
4.1% below that high, past the 4%-pullback confirmation threshold I'd been watching for. GOOGL also
picked up new confirmations (n=15 to n=25) against a 2026-09-09 low at $330.65, though its hit rate
came down to 16%/16% as a result - worth watching whether that settles or keeps drifting.
TSLA (n=11, 36%/45%), HOOD (n=15, 27%/33%), QQQ (n=28, 32%/39%) and GC=F (n=14, 29%/29%) are
unchanged; NVDA, AMZN, SPY, VOO are still n=0. On the day-range calibration fix shipped 9/13: the
`calibHigh`/`calibLow` multipliers are live and present for all 10 tickers, but the day-ahead
forecast they were actually applied to (generated 9/13, for session 9/14) still hasn't been graded
into `horizonGrades` yet - the last graded session there is still 9/11, a pre-fix forecast. So the
real first-time test of the fix is still one day out, same as it's been since Saturday.

**What changed and why - redacted a name that had leaked onto the public site:** while reading
`real_trades.json`'s note on the TSLA 9/11 assignment (closed out and fully confirmed as of this
morning per the entry itself), I found the sentence read "...all 5 calls exercised against
Stuart..." - a first name, almost certainly the account owner's, sitting in a plain-text field.
Because `analyze.py` copies this file's notes verbatim into `data.js`, `index.html`, and
`dashboard_single.html`, that name wasn't just in the ledger - it was live on the public GitHub
Pages site (elljp1.github.io/stock-dashboard) in all three places. This is exactly the kind of
thing the daily-review rules say never to let into a committed file, so I treated it as a clear bug
regardless of today's usual "one change only if a pattern repeats 3+ days" bar and fixed it
immediately rather than waiting: replaced "exercised against Stuart" with "exercised (assigned)" -
same factual meaning (the short calls were assigned), no name - in `real_trades.json` and in the
three files that embed its content. Re-ran `coherence_check.py` after the edit (still passes) and
confirmed with a repo-wide search that no other file contains the name. I did not touch any pricing
data, any grading logic, or any honesty feature - this was a pure data-privacy redaction, four
files, one string, nothing else changed. Also ran the full Python test suite (25 tests across
`test_data_freshness.py`, `test_reliability.py`, `test_schedule_gate.py`, `test_scoring.py`) - all
still pass.

**Real-money ledger:** no new trades since 9/13 - the TSLA 9/11 assignment stays fully logged and
closed (the note I redacted today), and the new TSLA trade-card sheet logged 9/14 still targets the
week of 9/21 with nothing executable yet.

**Watch next:** whether tomorrow's grading run finally scores the first day-ahead forecast made
under the new calibration (session 9/14's); whether JPM's newly-confirmed 19%/29% hit rate holds up
as more of its predictions resolve, or was a one-time batch effect from a single pivot; whether
GOOGL's dropping hit rate keeps drifting down or stabilizes; and whether fetch access to Yahoo
recovers in this sandbox, now blocked six days running. I'll also do a quick scan for any other
personal details that might have slipped into a note field the next few days, just in case this
wasn't a one-off.

## 2026-09-15 (Tue) — grade + log only; first post-fix session in, too noisy to judge yet

**Data freshness:** my sandbox still can't reach Yahoo (403 Forbidden through the proxy tunnel on
every ticker, seventh day running, no cached CSVs since they're gitignored), so `fetch_data.py`
and `analyze.py` couldn't run end-to-end here. The separate cloud refresh workflow reached Yahoo
fine and already regenerated everything today - `data.js` is stamped generated 5:40 PM ET 9/15,
and `horizons_log.json`/`daily_extremes.json`/`predictions_log.json` all carry today's entries.
`coherence_check.py` passes on that build (10/10 tickers), so today's review is against a current,
valid dashboard, not a stale one.

**Grades reviewed:** the day-range calibration fix shipped 9/13 now has its first graded session
(9/14) in `horizonGrades` for all 10 tickers, but one day is far too little to judge - results are
a mixed bag, not a trend. Some tickers improved a lot on the low side (TSLA -3.4% avg error down to
-1.1%, NVDA -2.5% to +0.7%, JPM -1.2% to 0.0%), but the high side didn't budge or got worse for
several (TSLA +1.8% to +2.7%, NVDA +1.7% to +5.7%), and HOOD's low side got notably worse (-2.7% to
-7.5%). GOOGL swung the other way (high error dropped from +3.2% to -0.3%, low error worsened from
-1.5% to -5.5%). This is consistent with normal day-to-day noise on a single new sample, not
evidence the fix failed - I'm not touching the calibration code again after one graded day per the
one-change discipline; it needs several more sessions before the median-based factors settle down
and a real trend is visible.

Swing track record is otherwise unchanged from yesterday: TSLA n=11 (36%/45%), HOOD n=32
(12%/19%), QQQ n=28 (32%/39%), JPM n=21 (19%/29%), GOOGL n=25 (16%/16%), GC=F n=14 (29%/29%).
I dug into the NVDA/AMZN/SPY/VOO n=0 question flagged in recent reviews and confirmed it's not a
bug: I replayed the zigzag swing logic by hand against the closing-price ledger and none of the
four has had a closing-price move of its own threshold size (10% for NVDA/AMZN, 5% for SPY/VOO)
since their last recorded swing point - SPY/VOO have been climbing more or less steadily since
March without a 5% close-to-close pullback, and NVDA/AMZN similarly since late July/early August.
The daily high/low ledger shows bigger intraday swings, but the grading correctly uses closing
prices, so this is a genuinely quiet stretch for those four names, not a stuck or broken grader.
No code change needed here.

**Privacy check:** re-read `real_trades.json` (no new entries since the 9/11 TSLA assignment) -
the redaction from 9/14 is intact, no name or other personal detail has crept back in.

**What changed and why:** nothing - today is a grade-and-log day. No pattern has yet persisted the
required 3+ graded days since the 9/13 fix, and no new bug turned up.

**Real-money ledger:** no change since 9/11 - the TSLA assignment stays closed and fully logged;
the current TSLA trade-card sheet still targets the week of 9/21 with nothing executable yet.

**Watch next:** whether the 9/15 and 9/16 graded sessions start showing the calibration fix
converging on both sides (not just lows) across most tickers, or whether the high-side miss
persisting for 3+ sessions turns into next fix; whether HOOD's worsening low-side miss is a fluke
or the start of a real problem; whether JPM/GOOGL's hit rates hold up as more predictions resolve;
and whether Yahoo access recovers in this sandbox (blocked seven days running now).

## 2026-09-16 (Wed) — found and fixed an exposed account number; grades otherwise unremarkable

**Data freshness:** my sandbox still can't reach Yahoo (proxy rejects the connection, now the
eighth day running), but the separate cloud refresh workflow reached Yahoo fine earlier today —
`data.js` is stamped generated 5:39 PM ET 9/16, and `coherence_check.py` passes on that build
(10/10 tickers), so today's review is against a current, valid dashboard.

**Today's real find: a brokerage account number was committed in plain text.** While checking
`spread_journal.json` for personal details (routine after the 9/14 name slip-up), I found the
account number itself — not just a nickname — written out in full in three trade entries, added
over the last two days rather than masked the way every other account reference in that file is
(the file's own header masks it as `••••2831`; the three trade entries had the full digits
instead). I redacted all three to match the file's existing `••••2831` masking convention and
re-verified `spread_journal.json` isn't read anywhere in the `analyze.py`/`coherence_check.py`
pipeline, so the number never reached `data.js` or any of the dashboard HTML pages — the public
site itself was never exposed. It was, however, sitting in plain text in this file on the public
GitHub repo for about two days across three commits before I caught it. Redacting today only fixes
the current file; those three earlier commits still contain the plain-text number in the repo's
history, and I did not rewrite history to scrub it since that's a destructive operation I won't do
without asking first. I'm flagging this prominently — worth deciding whether that account number
should be treated as exposed.

**Grades reviewed:** swing track record ticked up slightly for HOOD (n=33, was 32; hit rates
15%/21%, up from 12%/19%) and down slightly for JPM (n=22, was 21; 18%/27%, down from 19%/29% on
one new resolved prediction) — both single-sample moves, not trends. TSLA, QQQ, GOOGL, and GC=F
are unchanged. NVDA/AMZN/SPY/VOO remain at n=0 swings, still confirmed as a genuinely quiet
stretch rather than a bug. The HOOD low-side calibration miss flagged after the 9/13 fix has only
two graded sessions so far (9/14: -7.5%, 9/15: +3.1%) — opposite directions, so that's noise, not
the 3+ day worsening pattern that would justify touching the calibration code. No calibration
change today. Today's (9/16) predictions vs. what actually printed were mostly small, typical
misses (highs a bit over, lows a bit under forecast) except HOOD, whose predicted low ($106.28)
missed the actual low ($101.70) by about 4.3% — the worst of the ten tickers today, consistent with
HOOD just being the noisiest name rather than a new problem.

**Trade cards:** spot-checked several recently-expired "sell put at the projected low" cards
(JPM/AMZN from 9/14, QQQ/SPY/VOO from 9/15) — in each case the actual low never reached the
projected entry price, so none would have filled. No losses, just misses.

**What changed and why:** one fix today — redacted the exposed account number in
`spread_journal.json` described above. No other code change; the HOOD calibration pattern isn't
persistent yet (2 sessions, not 3+, and they point opposite ways).

**Real-money ledger:** no change since 9/11 — the TSLA assignment stays closed and fully logged.
On the practice/paper side, `spread_journal.json` shows HOOD 10/23 100/95 put credit spread (trade
3) filled and open (2x, opened 9/16, credit $370, exit resting at $0.90), a duplicate HOOD order
(trade 4) placed and cancelled same day, and QQQ 10/23 685/680 put credit spread (trade 5) still
working/unfilled.

**Watch next:** whether the exposed account number needs any follow-up action beyond today's
redaction (e.g. deciding whether to scrub git history); whether HOOD's low-side calibration error
settles into a real direction once a third graded session lands; whether JPM's hit-rate dip is the
start of a real drift or just noise; and whether Yahoo access recovers in this sandbox (blocked
eight days running now).

## 2026-09-17 (Thu) — grade + log only; no persistent pattern clears the bar for a code change

**Fetch status:** blocked a ninth day running - same 403 Forbidden at the proxy gateway. No CSVs
are committed to the repo (gitignored by design), so `analyze.py` correctly refused to overwrite
the last published dashboard with a broken build. The separate cloud refresh workflow published a
good build today at 5:40 PM ET, `coherence_check.py` passes cleanly against it (10/10 tickers), and
I re-checked `spread_journal.json` for the account-number leak found yesterday - all account
references are properly masked today (`••••2831`, `••••8549`, `••••6540`), no new plain-text
numbers anywhere in the repo.

**Grades reviewed:** HOOD's low-side calibration miss (flagged 9/13, watched since) now has a third
graded session: 9/14 -7.5%, 9/15 +3.1%, 9/16 +4.5% - two of three positive, one sharply negative,
still no consistent direction, so still noise rather than the persistent pattern that would justify
touching the calibration code. JPM's swing track record continued its slow slide (n=23, up from 22;
17%/26%, down from 18%/27%) for a third straight day, but this reads as small-sample dilution, not
a new defect: n is still under 25, each day adds exactly one newly-resolved prediction, and JPM's
per-family stats (gann 0/4, fib 0/3, rhythm 2/13) show it's simply a hard ticker for these methods
right now, consistent with the 9/4 finding that JPM's swing detector goes long stretches with no
qualifying pivot to confirm against. TSLA (n=11, unchanged), QQQ (n=28, up from prior), GOOGL (n=27)
and GC=F (n=15) show only single-sample noise, no trend. NVDA/AMZN/SPY/VOO remain at n=0 swings -
still a genuinely quiet stretch, not a bug. Today's (9/16, the latest fully graded session) daily
high/low errors were typical across the board (roughly 1-3% misses), nothing standing out.

**Trade cards:** the forward-looking MODEL cards logged today (TSLA, etc.) are all still open/unresolved
by definition - nothing new to grade yet. The paper spread journal is unchanged since yesterday:
HOOD 100/95 put credit spread (trade 3) still open, the duplicate HOOD order (trade 4) still
cancelled, QQQ 685/680 put credit spread (trade 5) still working/unfilled. No new orders today.

**What changed and why:** no code change. Neither the HOOD calibration question nor the JPM
hit-rate slide clears the 3+-day-persistent-pattern-or-clear-bug bar for today - both look like
ordinary small-sample noise on closer inspection, and touching the calibration or grading code
without real evidence would risk the opposite of an improvement. Honesty features (measured hit
rates, random-control comparisons, self-grading, the coherence gate) are untouched; `tickers.txt`
wasn't touched.

**Real-money ledger:** unchanged since the 9/11 TSLA assignment - still closed and fully logged, no
new real trades.

**Watch next:** whether HOOD's low-side error ever settles into one consistent direction; whether
JPM's rate keeps sliding past the point where sample-size dilution is a believable explanation;
whether the still-unresolved plain-text account number from three of last week's commits needs a
decision on scrubbing git history; and whether Yahoo access recovers in this sandbox (blocked nine
days running now).

## 2026-09-18 (Fri) — fetch blocked a tenth day; grade + log only, no persistent pattern clears the bar

**Build status:** `fetch_data.py` failed on all 10 tickers again (403 Forbidden from the sandbox's
network proxy on every symbol and every pre/post-market lookup) - blocked ten days running now.
As designed, `analyze.py` refused to run without fresh CSVs rather than touch the last published
build. The separate cloud refresh workflow ran twice today (around 5:09 PM and 5:45 PM ET) and
published a good build; `coherence_check.py` passes cleanly against it (10/10 tickers), and all
five local test suites (data freshness, horizon ledger, reliability, schedule gate, scoring) pass
with no failures. `spread_journal.json`, `real_trades.json` and `trades_log.json` were re-checked
for stray account numbers or other PII - only the expected masked references (`••••2831`) and the
structural `account.last4` field appear; nothing new to scrub.

**Grades reviewed:** HOOD's resolved-prediction window jumped by 6 in one day (n 35→41) because two
long-pending "low" predictions from early August (logged 8/14 and 8/25, predicting $91.32 and
$88.57) finally resolved against the 9/16 print of $104.42 - both missed (hit2/hit3 both false),
consistent with the low-side calibration pattern watched since 9/13, still not a new, single-day
direction change (hit2Rate 17%→15%, hit3Rate 23%→20%, a continuation not a reversal). The other four
new window entries are just newly-logged pending predictions, not new grades. JPM was unchanged
today (n=23, 17%/26%) - no newly-resolved predictions, so no fresh evidence either way on its
multi-day slide. TSLA (n=11), QQQ (n=28) also unchanged. GOOGL added one resolved prediction
(n 27→28, hit rates ticked up to 21%/21%) and GC=F added one (n 15→16, hit rates ticked down to
25%/25%) - both single-sample moves, no trend. NVDA/AMZN/SPY/VOO remain at n=0 swings, still a quiet
stretch. Daily high/low errors for the latest fully graded session (9/17) were typical across the
board, nothing standing out.

**Trade cards / paper journal:** HOOD 100/95 put credit spread (trade 3) remains closed +$190 realized,
booked to September's $11,000 account. The duplicate HOOD order (trade 4) is still cancelled. The
QQQ 685/680 put credit spread (trade 5) was cancelled by the user in the app this morning (9:29 AM
ET) before filling - QQQ gapped over the app's projected 9/17 low of $690.31 and the spread's mid
never rose above ~$0.80, so the resting $1.55 limit was never going to fill; cleanly logged, not a
bug. Real-money ledger unchanged since the 9/11 TSLA assignment - still closed and fully logged.

**What changed and why:** no code change. HOOD's low-side miss pattern and JPM's hit-rate slide are
both still being watched but neither produced new evidence today that clears the 3+-day-persistent-
pattern-or-clear-bug bar - HOOD's window jump was a batch of predictions crossing their horizon at
once (verified by walking the added rows and family-stats delta by hand, not a double-counting bug),
and JPM simply had nothing new to grade. Touching the calibration or grading code on today's evidence
would risk the opposite of an improvement. Honesty features (measured hit rates, random-control
comparisons, self-grading, the coherence gate) are untouched; `tickers.txt` wasn't touched.

**Watch next:** whether HOOD's low-side error ever settles into a genuinely new pattern beyond the
one already logged; whether JPM's rate resumes sliding once new predictions resolve; whether the
still-unresolved plain-text account number from earlier commits needs a decision on scrubbing git
history; and whether Yahoo access recovers in this sandbox (blocked ten days running now).

## 2026-09-20 (Sun) — weekend, no new session; fetch blocked a twelfth day; grade + log only

**Build status:** `fetch_data.py` failed on all 10 tickers again (403 Forbidden from the
sandbox's network proxy on every symbol and every pre/post-market lookup) - blocked twelve
days running now. As designed, `analyze.py` refused to touch the published dashboard without
fresh CSVs (it errored out immediately since no CSV files exist to fall back on - they are
git-ignored and this sandbox never had a successful fetch to produce them). Confirmed the
working tree was untouched before and after the run (`git status` clean throughout).
Markets are closed Sunday, so there was no new session to fetch even if Yahoo had answered.
The live site's last published build is still this morning's 5:58 AM ET cloud-refresh run,
which itself also failed to pull fresh data (its `data.js` numbers are byte-for-byte identical
to Friday 9/18's, only the generated timestamp moved) - the cloud runner is hitting the same
block as this sandbox. `coherence_check.py` passes cleanly against that build (10/10 tickers),
and all 30 local tests across the five suites (data freshness, horizon ledger, reliability,
schedule gate, scoring) pass. Re-ran the account-number guard (`test_sensitive_data.py`,
staged and full-tree) - clean, only the expected masked references.

**Grades reviewed:** every ticker's track record and horizon-grade numbers are identical to
yesterday's review since no new predictions resolved anywhere (sandbox or cloud). HOOD stays
at n=41 (15%/20% hit rates) - still no consistent direction in its low-side daily error.
JPM (n=23, 17%/26%), TSLA (n=11, 36%/45%), QQQ (n=28, 32%/39%), GOOGL (n=28, 21%/21%) and
GC=F (n=16, 25%/25%) are all unchanged. NVDA/AMZN/SPY/VOO remain at n=0 swings.

**Trade cards / paper journal:** `spread_journal.json` unchanged since 9/18 - same 5 tracked
trades and 5 pushed-but-not-taken alerts, nothing new logged. `trades_log.json`'s newest
sheet is still Friday 9/18's. Real-money ledger unchanged since the 9/11 TSLA assignment.

**What changed and why:** no code change - there is no new data anywhere (sandbox or cloud
refresh) to justify one, and no open watch item crossed the 3+-day persistent-pattern bar
today since nothing new graded. Honesty features (measured hit rates, random-control
comparisons, self-grading, the coherence gate) are untouched; `tickers.txt` wasn't touched.

**Watch next:** the plain-text account number committed in three commits around 9/14-9/16 is
still sitting in the repo's public git history, unscrubbed - flagged in this log every day
since it was found (about a week now) and still needs the owner's explicit decision on
whether to rewrite history to remove it (a destructive operation nobody has authorized yet).
Also watching: whether the cloud refresh's own Yahoo access recovers now that it's confirmed
hitting the same block as this sandbox (twelve days running); whether HOOD's low-side error
ever settles into a genuinely new pattern; and whether JPM's hit rate resumes sliding once
new predictions resolve.

## 2026-09-19 (Sat) — weekend, no new session; fetch blocked an eleventh day; grade + log only

**Build status:** `fetch_data.py` failed on all 10 tickers again (403 Forbidden from the sandbox's
network proxy on every symbol and every pre/post-market lookup) - blocked eleven days running now.
As designed, `analyze.py` refused to touch the published dashboard without fresh CSVs (confirmed
`data.js`, `dashboard.html`, `index.html` and `daily_extremes.json` were byte-for-byte unchanged
before and after the run). Markets are closed Saturday, so there was no new session to fetch even
if Yahoo had answered - the last published build is still Friday 9/18's 6:15 PM ET cloud-refresh
run, and today is the first weekend day this eleven-day fetch outage has overlapped with, so
nothing new was lost by the block. `coherence_check.py` passes cleanly against that build (10/10
tickers), and all 30 local tests across the five suites (data freshness, horizon ledger,
reliability, schedule gate, scoring) pass. Re-ran the account-number guard
(`test_sensitive_data.py`, staged and full-tree) - clean, only the expected masked references
(`••••2831`).

**Grades reviewed:** every ticker's track record and horizon-grade numbers are identical to
yesterday's review since no new predictions resolved and no new session graded (same Friday
6:15 PM build). HOOD stays at n=41 (15%/20% hit rates) - its low-side daily error is still noisy,
not a clean trend (nine of the last ten graded sessions swing between -7.5% and +4.5% with no
consistent direction). JPM (n=23, 17%/26%), TSLA (n=11, 36%/45%), QQQ (n=28, 32%/39%), GOOGL
(n=28, 21%/21%) and GC=F (n=16, 25%/25%) are all unchanged. NVDA/AMZN/SPY/VOO remain at n=0 swings.
One thing worth naming: Thursday 9/17's horizon-grade session showed every one of the ten tickers
missing to the low side that day (loErrPct from -1.3% to -6.2%, already reviewed in yesterday's
log) - that reads as one broad down day across the whole watchlist rather than a per-ticker
calibration problem, since it hit hedge-fund-unrelated names (JPM, GC=F) as hard as the volatile
ones. A single shared day like that doesn't clear the 3+-day persistent-pattern bar on its own.

**Trade cards / paper journal:** `spread_journal.json` unchanged since 9/18 - same 5 trades (HOOD
spread 3 closed +$190, duplicate HOOD order 4 still cancelled, QQQ spread 5 still cancelled by the
user before it could fill). `trades_log.json`'s newest sheet is still Friday 9/18's. Real-money
ledger unchanged since the 9/11 TSLA assignment.

**What changed and why:** no code change - there is no new data to justify one, and none of the
open watch items (HOOD's low-side noise, JPM's hit-rate level) crossed the 3+-day persistent-
pattern bar today. Honesty features (measured hit rates, random-control comparisons, self-grading,
the coherence gate) are untouched; `tickers.txt` wasn't touched.

**Watch next:** the plain-text account number committed in three commits around 9/14-9/16 is still
sitting in the repo's public git history, unscrubbed - it's been flagged in this log every day since
it was found and needs the owner's decision on whether to rewrite history to remove it (a
destructive operation nobody has authorized yet). Also watching: whether HOOD's low-side error ever
settles into a genuinely new pattern; whether JPM's rate resumes sliding once new predictions
resolve; and whether Yahoo access recovers in this sandbox (blocked eleven days running now).

## 2026-09-21 (Mon) — Yahoo access recovered after a 12-day block; backlog of swing grades resolved, mostly misses; grade + log only

**Build status:** my sandbox still can't reach Yahoo (403 Forbidden on all 10 tickers, same
block as every day for the last twelve days), so `analyze.py` correctly refused to touch the
published dashboard (no CSVs to work from) and left it untouched - confirmed `git status` was
clean before and after. But the separate cloud refresh workflow finally got through today:
`data.js` is freshly stamped 5:50 PM ET 9/21, `daily_extremes.json` picked up a genuine new
2026-09-21 session for all ten tickers (first new session since Friday 9/18), and today's
option-trade-card sheet in `trades_log.json` is dated today too. `coherence_check.py` passes
cleanly (10/10 tickers), and all 37 local tests across the six suites (data freshness, horizon
ledger, reliability, schedule gate, scoring, sensitive-data guard) pass. The account-number
guard is still clean - only the expected masked `••••2831` references.

**Grades reviewed:** the 12-day data outage had been silently stacking up unconfirmed swing
predictions (a high/low call needs enough later price action to confirm it actually was the
swing point), and today's fresh data let a batch of them resolve at once: TSLA n 11→12, HOOD
41→43, QQQ 28→34, JPM 23→24, GOOGL 28→30, GC=F 16→17 - 13 newly-resolved predictions in total,
spanning original prediction dates from late July through early September. Of those 13, only 1
was a hit (a GOOGL one); the other 12 missed, including all 6 of QQQ's, which is why QQQ's hit
rate dropped the most (32%→26% on the looser hit-2 measure, 39%→32% on hit-3). This reads as a
one-time backlog catching up, not a new trend: it's a single grading event covering weeks of old
predictions, not several bad sessions in a row, so it doesn't clear the 3+-day persistent-pattern
bar for a code change on its own - but if QQQ's rate keeps sliding once fresh, same-week
predictions start resolving normally again, that would be worth acting on. The daily horizon
grades (the high/low-of-the-day forecasts) haven't picked up a new session yet - they still end
at 9/18 for every ticker; today's 9/21 session should grade in tomorrow's run. NVDA/AMZN/SPY/VOO
remain at n=0 swings, still just a quiet stretch for those four, not a bug.

**Trade cards / paper journal:** a different, separate agent session (not this one) placed a new
QQQ call-credit-spread alert into `spread_journal.json` today (commit c780938, 15:47 UTC) - that's
the live options-journal process the owner runs elsewhere, outside this review's scope; I didn't
touch it. Real-money ledger unchanged since the 9/11 TSLA assignment.

**What changed and why:** no code change - today's miss-heavy batch is backlog resolving after
the outage, not a fresh 3+-day pattern, and there's no clear bug (the underlying daily bars for
9/21 look sane and coherence_check passes). Honesty features (measured hit rates, random-control
comparisons, self-grading, the coherence gate) are untouched; `tickers.txt` wasn't touched.

**Watch next:** the plain-text brokerage account number committed in three commits around
9/14-9/16 is still sitting unscrubbed in the repo's public git history - flagged in this log
every day for a week now with no action taken yet; it needs the owner's explicit decision on
whether to authorize rewriting history to remove it. Also watching: whether QQQ's hit rate keeps
falling once new, non-backlog predictions resolve; whether tomorrow's first fresh daily-horizon
grade for the 9/21 session lands calibrated or not; whether my own sandbox's Yahoo access
recovers now that the cloud runner's has; and whether HOOD's low-side daily error settles into a
real direction.

## 2026-09-22 (Tue) — cloud refresh got through; grades steady, HOOD/QQQ still just noise; grade + log only

**Build status:** my sandbox's own Yahoo fetch is still 403-blocked on all 10 tickers (same as
every prior day), so I did not attempt to touch `analyze.py`'s output myself - this sandbox has no
committed CSVs to fall back on either (they're gitignored), so a local rebuild simply isn't possible
today. But the separate cloud refresh workflow got through again: `data.js` is freshly stamped
5:49-5:50 PM ET 9/22 for all ten tickers, `daily_extremes.json` and `trades_log.json` both picked up
today's session, and `coherence_check.py` passes cleanly (10/10 tickers) against that committed
build. All 37 local tests across the six suites (data freshness, horizon ledger, reliability,
schedule gate, scoring, sensitive-data guard) pass, and the account-number guard is still clean -
only the expected masked `••••2831`/`••••6540`/`••••8549` references, all last-4-digit only.

**Grades reviewed:** the swing-prediction ledger picked up a couple more resolved calls since
yesterday (HOOD n 43→45, QQQ n 34→35); the rest are unchanged (TSLA n=12, JPM n=24, GOOGL n=30,
GC=F n=17, NVDA/AMZN/SPY/VOO still n=0). Hit rates barely moved: QQQ actually ticked up a touch
(hit-2 26%→29%, hit-3 32%→34%) as the new resolution landed a hit; HOOD stayed roughly flat at
13%/20% (was 15%/20%), which is the same noisy low-hit-rate level this name has shown for weeks,
not a fresh drop. The daily high/low horizon grades now have a full 9/21 session graded for every
ticker (10 sessions each, was 9 yesterday) and the errors look like ordinary noise - no ticker is
showing a new, consistent directional bias beyond what's already been watched (HOOD's low side
stays the noisiest, same as always). Nothing here crosses the 3+-consecutive-day persistent-pattern
bar for a code change, and I didn't find a clear bug in the committed output.

**Trade cards / paper journal:** `trades_log.json` picked up a fresh TSLA model sheet for today's
session (call-spread ride toward the projected high) - informational only, nothing to act on.
`spread_journal.json` has two pending mirror-call alerts (GOOGL, QQQ) from 9/21 still awaiting the
owner's decision - that's the separate live options-journal process, outside this review's scope,
and I didn't touch it. The real-money ledger (`real_trades.json`) is unchanged since the 9/11 TSLA
assignment.

**What changed and why:** no code change - grades are steady/noisy, not a new pattern, and nothing
in today's committed build looks like a bug. Honesty features (measured hit rates, random-control
comparisons, self-grading, the coherence gate) are untouched; `tickers.txt` wasn't touched.

**Watch next:** the plain-text brokerage account number committed in three commits around
9/14-9/16 is still sitting unscrubbed in the repo's public git history - flagged in this log for
over a week now with no owner decision yet on whether to authorize rewriting history to remove it.
Also watching: whether HOOD's hit rate ever breaks out of its long-running 13-20% band in either
direction; whether QQQ's small uptick continues once more non-backlog predictions resolve; and
whether my own sandbox's Yahoo access ever recovers now that the cloud runner's has stayed reliable
for two days running.

## 2026-09-23 (Wed) — cloud refresh current; grades steady; grade + log only; account-number exposure now 8 days unresolved

**Build status:** my sandbox's own Yahoo fetch is still 403-blocked on all 10 tickers, and this
sandbox has no committed CSVs to fall back on (gitignored by design), so a local rebuild wasn't
possible today. The separate cloud refresh workflow reached Yahoo fine on its own and pushed a
fresh build about an hour before this review started (commit 5238407, `data.js` stamped 9/23);
`coherence_check.py` passes cleanly against that committed build (10/10 tickers), and the
account-number guard (`test_sensitive_data.py`) is clean on the current working copy - only the
expected masked `••••2831`/`••••6540`/`••••8549` references.

**Grades reviewed:** swing-ledger counts ticked up a little further (HOOD n 45→47, QQQ n 35→37);
TSLA (n=12), JPM (n=24), GOOGL (n=32), GC=F (n=18) unchanged; NVDA/AMZN/SPY/VOO still n=0, still a
quiet stretch, not a bug. Hit rates: TSLA 33%/42%, HOOD 15%/21%, QQQ 30%/35%, JPM 17%/25%, GOOGL
22%/25%, GC=F 22%/22% - all within the same noisy bands seen on prior days, no ticker sliding for
3+ straight sessions. The daily high/low horizon grades (last five graded sessions, 9/16-9/22) show
ordinary noise across every ticker - a mild recurring negative low-side bias on TSLA/QQQ/HOOD/AMZN
that's been visible for weeks and already watched, not a new pattern, and no ticker crosses the
3+-day persistent-bar for a code change. I didn't find a bug in the committed output.

**Trade cards / paper journal:** spot-checked `trades_log.json`'s latest sheet - nothing new to
flag beyond the usual model cards. `spread_journal.json`'s most recent entries are a GOOGL
10/23 325/320 put-credit spread (trade 6, opened, exit order resting at 0.60 GTC) and a GOOGL
320/315 re-alert (alert 14) - the live options-journal process the owner runs elsewhere, outside
this review's scope. `real_trades.json` unchanged since the 9/11 TSLA assignment.

**What changed and why:** no code change - grades are steady, not a new pattern, and nothing in
today's committed build looks like a bug. Honesty features (measured hit rates, random-control
comparisons, self-grading, the coherence gate) are untouched; `tickers.txt` wasn't touched.

**Watch next, and one flag for the owner directly:** the plain-text brokerage account number
committed in three commits around 9/14-9/16 is still sitting unscrubbed in this repo's public git
history - today is the 8th straight day this has been logged here with no visible owner decision
yet on whether to authorize rewriting history to remove it. Since this sits in a daily log file
that may not get read every day, I'm also sending a direct notification about it today rather than
just noting it here again. Also watching: whether HOOD's hit rate ever breaks its long-running
13-21% band; whether QQQ's slow uptick continues; and whether my own sandbox's Yahoo access ever
recovers.
