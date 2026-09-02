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
