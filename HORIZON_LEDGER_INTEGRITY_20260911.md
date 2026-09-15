# Day-ahead horizon original-forecast integrity repair

Prepared September 11 and rebased September 14, 2026 against
`elljp1/stock-dashboard` main commit
`3892a38`.

## Problem

Commit `f31ac6b38558769475634ec7cf1768a9861d4d41` correctly removed 119
duplicate day-ahead rows, leaving 285 unique ticker/session records. Its new
append path, however, deletes the existing row for a ticker/session and stores
the latest refresh. Its grading path also explicitly selects the most recent
row. If a forecast changes before the target session, the original is lost and
the shorter-lead revision is graded. That can make forecast accuracy look
better without improving real prediction quality.

That risk materialized on September 13. All ten forecasts for the September 14
session had their September 12 `logged` timestamp replaced by September 13.
Five price ranges also changed (TSLA, HOOD, GOOGL, AMZN and GC=F), so these were
not merely identical re-logs. On September 14, every intraday refresh rewrote
that session again. The final stored ranges were generated after the market
closed and included already-observed session extremes, but would be graded as
forecasts on the next session under the live code.

The separate `forecast_ledger.json` remains intact: 560 snapshots, 560 unique
IDs. All 370 prior snapshots remain byte-for-byte as the ledger prefix.

## Bounded repair

- Keep the first day-ahead forecast for every ticker/session immutable.
- Ignore later refreshes for the same ticker/session instead of replacing it.
- Grade the earliest stored forecast if historical duplicates ever reappear.
- Use those same earliest forecasts for the new range-bias calibration.
- Recover each earliest available ticker/session row from Git history. This
  restores 116 overwritten first calls; 73 had materially different prices.
- Retain protection against stale same-day runs moving the target backward.
- Add five focused tests and include them in the required workflow test gate.

This repair does not re-add the 119 exact duplicate re-logs removed by
`f31ac6b`. It replaces the later row for each affected ticker/session with its
earliest recoverable version, keeping the ledger at 295 unique rows. It does
not change the forecasting algorithm, market input, trading rule, PIN behavior,
or deployment schedule. No brokerage action is performed.

## Evidence before publication

- Live analysis: September 14, 2026 at 6:20 PM Eastern; the review completed at
  6:21 PM. All ten tickers contain September 14 daily bars and actual quote
  timestamps between 6:08 PM and 6:20 PM Eastern.
- The requested premarket schedule remains incomplete: a 7:06 AM refresh ran,
  followed by no successful data refresh until 10:20 AM. Intraday dispatches
  then ran repeatedly through 5:38 PM, and the evening review ran at 6:19 PM.
- `daily_review.json` contains 18 original price scores with median absolute
  error 2.365% and mean 2.902%. This is price error only, not reversal accuracy
  or net trading profitability.
- On September 14, the pre-session calibrated revision reduced combined high
  and low price MAE from 2.287% to 1.777% versus the earlier uncalibrated call,
  but range coverage fell from 6/10 to 5/10. This is one session and ten
  instruments, with no costs, trading returns, or drawdown measurement; it is
  insufficient for strategy promotion.
- Scoring the latest overwritten rows instead of recovered first calls reduces
  apparent historical range MAE from 2.137% to 1.944%, quantifying the optimism
  introduced by the live overwrite behavior.

Publication requires the complete test suite, one fresh-data refresh, a
successful Pages deployment, and byte-level verification of the live files.
