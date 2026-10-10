# Daily high/low forecast protocol (hilo-1)

The dashboard's primary output: for each stock and regular session, four
numbers with uncertainty. They are the high price, high time, low price and
low time.

## Records
- `hilo_ledger.jsonl` is append-only. Each line carries `issuedAt` (UTC),
  `dataCutoff` (end of the last bar used, Eastern) and `lastBar`. Each line
  also carries the hash of the previous line, so an edit anywhere breaks the
  chain (`hilo.verify_ledger`). Edits, deletions and reordering are caught.
  Dropping the newest lines, or rewriting the whole file with a fresh chain,
  is not caught by the chain itself. Only an external anchor catches that:
  today the Git history and its bot commit times, which are evidence but not
  tamper-proof.
- **Premarket**: a forecast issued before the target session opens, built from
  completed sessions only. Only the first one per stock and session is kept.
- **Intraday**: a revision of today's FINAL full-session high and low,
  including what has already traded. It is frozen at fixed bar-count
  checkpoints: 2, 4, 8, 13, 18 and 22 completed bars (data cutoffs 10:00,
  10:30, 11:30, 12:45, 14:00 and 15:00 on a full day). A checkpoint-N record
  uses exactly the first N bars, whenever the run happens.
  - Missed earlier checkpoints are never backfilled.
  - A record issued more than 20 minutes after its cutoff is flagged `late`.
    It stays in the ledger but is not scored.
  - Half-day sessions are kept out of the per-checkpoint comparison.
- `hilo_sessions.json` stores each completed session once. A completed session
  has closed and has every expected bar, per the NYSE calendar in
  `market_calendar.py`, including 1:00 PM half-days. Stored sessions are never
  rewritten. A later provider change is counted, not applied.
- Futures (GC=F) are excluded until a futures session calendar exists.
- Bars with non-finite, non-positive or inconsistent OHLC values are dropped.
  That leaves their session incomplete, so it is never stored or scored.
- Fail closed: if the chain or any record fails validation, nothing is
  appended and nothing is scored, and the page shows "unavailable". If the
  forecaster crashes, the workflow marks the old output as failed, so it is
  not shown as current. Output older than 3 hours is shown as STALE, with
  its session date.

## Time outputs (hilo-2)
- hilo-1 timed the high and the low independently. The opening bar is the most
  common bar for both, so both read 09:30 on 78% of forecasts in a walk-forward
  replay. In reality the two shared a bar on only 2.4% of days.
- hilo-2 uses `timing`. Each past session (or replayed intraday scenario)
  gives an ordered pair: (earlier bar, later bar) of its high and low.
  - The reported pair is the **most frequent ordered pair** actually seen
    (`pPair`). It always has support and is never reversed, and it can be one
    bar for both when that is what history shows.
  - `early`/`late` also carry each bar's own share (`pBar`, `p60`).
  - `pHighFirst` is the share of sessions with the high first; `pSameBar` is
    the share with both in one bar.
- The order is called (`resolved`) only when the pair has two different bars,
  `pHighFirst` is at least 0.6 either way, and `pPairHighFirst` (the same share
  among only the sessions behind the selected pair) is at least 0.6 the same
  way, so the high/low assignment was actually observed. Only then is it attached to the
  high and the low (`timeBasis: order-assigned`). Otherwise each side keeps
  its marginal modal bar (`timeBasis: marginal mode`), and the page shows only
  "1st ≈ early · 2nd ≈ late · order ?" (or "both ≈ bar").
- Walk-forward replay, 330 test sessions on 10 stocks (retrospective only):
  - Early bar exact 66–67%; within 60 minutes 86%.
  - Late bar exact 15–17%; within 60 minutes 38–40% (standalone replay and
    the engine's own retrospective).
  - Both within 60 minutes 32.4%, against 27.9% for separate early/late
    modes and 18.5% for hilo-1's independent modes.
  - Called by majority, the order was right only 47.9% of the time.
- hilo-1 records remain in the ledger, unchanged, and are scored separately (`forwardByModel`).
- `window.centre` (the best ±60-minute window) is still recorded and scored against the prior-60 fixed window.

## Periods on the page (D / W / M / Y)
- One function, `periodView()`, gives the chart and the result rows the same
  forecast points for the selected period. Those points are the day forecast
  for the target session plus the next projected turns that fall inside the
  period, at most five.
- These are **projected points over a partial horizon**, not a forecast of the
  full period's extremes. The page labels them "proj. pt" and says
  "partial: day + N turns".
- Highs and lows already traded in the period (from completed daily bars) are
  shown separately, as "so far". On the chart they are grey hollow circles.
  They never replace the forecast.

## Scoring
- A record is scored only after its session is complete.
- A record is excluded when its data cutoff is after its issue time.
- A premarket record is excluded when it was issued at or after the open.
- Paired baselines on the same rows:
  - Premarket price vs the prior session's extreme.
  - Premarket time vs the open.
  - Intraday vs "the extreme so far stands".
  - Legacy app calls, for reference.
- Uncertainty:
  - Price: an 80% band, with its realised coverage reported.
  - Time: the empirical chance of landing within ±60 minutes.
  - Paired differences: session-bootstrap 95% intervals.

## States
These are reported separately and never merged:
1. **Candidate**: code on a branch.
2. **Tested**: the unit gate passes (in CI before publication once merged).
3. **Committed / deployed**: merged to main and published by the refresh
   workflow (build commit shown on the page).
4. **Forward record**: an observational report per output. It gives the
   number of complete forward sessions, the model, the strongest comparator
   on the same rows, and a session-bootstrap interval. No sample size, by
   itself, establishes an edge, and the page never labels an output "proven".

The retrospective replay is labelled as such and is never proof. Model hilo-1
is a baseline to improve on, not a claimed edge. Legacy turning-point
sections on the page remain, labelled secondary. The refocus does not remove
them.
