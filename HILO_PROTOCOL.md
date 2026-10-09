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

## Time outputs
- `time` is the **modal 15-minute bar**, the single most likely bar (ties go to
  the earliest), with its probability `pBar`. This is the primary time output.
- `window.centre` is a **separate output**. It is the centre of the
  ±60-minute window that holds the most probability, with `window.p60` (and
  `p30` around the same centre). It is a window centre, not the most likely
  time. It equals the prior-60-session best fixed clock.
- Both are scored separately:
  - modal bar exactly right (`timeBar`)
  - modal bar within ±60 minutes (`timeNear`), against the opening bar, the
    open ±60, the prior-60-session best fixed window, and the legacy app
  - window centre within ±60 minutes (`timeWindow`)
- Intraday times come from the whole distribution. In each replayed scenario
  the final extreme is either the one already traded (at its observed bar) or
  a later one, so every window sums all of that probability.

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
