# Research proposal: standalone timing methods versus simple controls

Status: **proposal only.** Nothing here is implemented, and nothing here changes
forecast weights, trade plans or risk settings. The scoring definition in
`TIMING_PROTOCOL.md` (daily-close turns, ±2 sessions, one turn per call) still
applies, and this study reuses it unchanged.

## Question

Can a standalone Gann count rule, a Hurst/Fibonacci cycle rule, or an explicit
astronomy-event rule predict the **date** of a daily-close reversal better than
simple controls, when every rule issues forecasts at the same rate? A separate
second question asks whether any timing skill survives trading costs.

This study does not evaluate the blended engine. Method tags inside blended
calls overlap, so they cannot show which method did the work (see the
scorecard's method-tag note).

## Pre-registration (freeze before any test data is examined)

Commit one file, `research/timing_prereg_v1.json`, and record its git hash
before running any evaluation. It fixes:

1. **Tickers.** The 10 in `tickers.txt`. GC=F is scored separately because of
   its futures session labels.
2. **Reference turns.** The `confirmed_turns` definition in `timing_review.py`
   (strict five-session closing extreme, two confirming sessions). Ties are
   excluded.
3. **Anchors.** Each rule counts forward from the most recent confirmed turn
   known at the forecast date. That turn must be confirmed by then, with no
   look-ahead. The first eligible turn is used, never a hand-picked one.
4. **Rules, with parameters fixed in advance:**

   | Family | Rule | Fixed parameters |
   |---|---|---|
   | C0 control | Uniform random session | Same count and lead as the rule it controls; 1,000 seeds |
   | C1 control | Median historical turn spacing from the anchor | Median computed from training data only |
   | C2 control | Fixed calendar spacing | Every 10 and every 21 sessions from the anchor |
   | G | Gann calendar counts | 30/45/60/90/120/144/180 **calendar** days from the anchor, rolled to the next session |
   | H | Hurst nominal cycle troughs and crests | 10/20/40-session nominal periods, phase taken from the anchor |
   | F | Fibonacci session counts | 8/13/21/34/55 sessions from the anchor |
   | A | Astronomy events | New/full moon, and ingress or station of Mercury and Mars, from `ephem` at a fixed 16:00 ET cutoff, rolled to the next session |

   The direction (high or low) of each forecast alternates from the anchor's
   type. No rule may use price targets.
5. **Signal-frequency matching.** Every rule and control is capped at the same
   budget of forecasts per ticker per 60 sessions: the smallest budget any
   family naturally produces. When a rule produces more candidates than the
   budget allows, a fixed rule decides which to keep (the nearest to the
   anchor). Where a rule cannot be capped, compare hit rates at an equal
   false-alarm rate instead.
6. **Lead times.** Forecasts are issued 1–10 sessions ahead only. Each
   forecast is stored with its issue timestamp before its window opens.
7. **Variations log.** Every parameter set tried goes into
   `research/variations_log.jsonl`, including the ones that fail.

## Data split

- **Training (rule selection only):** sessions before 2024-01-01. Only the
  median spacing for C1 and any tie-break choices may be set here.
- **Validation:** 2024-01-01 through 2025-12-31. Each family may run once
  here. After that, the only permitted change is to drop a family entirely.
- **Untouched test:** 2026-01-01 onward, plus the live forward period that
  begins 2026-09-24. The historical test run happens once. Data already viewed
  on the dashboard since 2026-03 counts as inspected, so it is reported
  separately and never relabeled as unseen.

`daily_extremes.json` only goes back to March 2026. The study needs a frozen
daily-bar archive, with a stored hash, built from the provider history before
evaluation starts.

## Metrics (all at matched signal frequency)

- **Timing hits:** matched same-type turn within ±2 sessions, with each turn
  claimed at most once.
- **False alarms:** forecasts with no claimable turn.
- **Missed turns:** confirmed turns in coverage that no forecast claimed.
- **Signed timing error** (early or late) among hits, reported next to the
  counts above, never instead of them.
- **Lift over controls:** hit rate minus the C0 distribution (as a
  percentile) and minus C1 and C2.

Uncertainty is estimated with a block bootstrap. Blocks are 20 sessions long
and are resampled jointly across tickers to account for cross-ticker
correlation and overlapping windows. Report 95% intervals. Five families are
compared against controls, so apply a Holm correction.

## Power and promotion rule

Before the test run, compute the number of scored forecasts needed to detect a
10-percentage-point lift over C1 with 80% power at α = 0.05 (Holm-adjusted),
using the block-bootstrap variance from the training period. The test count
comes from that calculation, not from a count of profitable days.

A family may be **proposed** for inclusion (not auto-promoted) only if all
four conditions hold on the untouched test:

- its lower 95% bound for lift over C1 is above zero;
- it does not increase missed turns at matched frequency;
- the result holds in at least two of three independent time blocks and in
  both rising and falling market regimes;
- the forward cohort agrees in direction once it reaches the pre-computed
  sample size.

**Explicitly excluded as evidence:** three consecutive graded days,
single-week streaks, blended-call method tags, in-sample lead-edge tables, and
any 30–40% monthly return target. A return target is never a tuning
objective.

## Trading-cost and drawdown test (separate)

Only a family that passes the timing test moves on to this stage. Simulate
next-available-session fills at the open, with quoted bid-ask spread, fees,
0.05% slippage per side, turnover, maximum drawdown, the longest time spent in
drawdown, and exposure. Report these results on their own; they do not change
the timing verdict. No brokerage orders are placed at any stage.

## Deliverables

1. The pre-registration file and its hash.
2. `research/timing_study.py`, which reuses `confirmed_turns` and `match`
   from `timing_review.py` unchanged.
3. A results report that lists every rule, control, variation and interval,
   including the null results.
4. Owner sign-off before any weight change reaches `analyze.py`.
