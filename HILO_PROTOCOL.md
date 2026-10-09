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
- **Intraday**: a revision for the rest of today's session. It uses only
  15-minute bars that have finished before the issue time, plus earlier
  sessions. It is frozen at six checkpoints per session (10:00, 10:30, 11:30,
  12:45, 14:00 and 15:00 on a full day).
- `hilo_sessions.json` stores each completed session once. A completed session
  has closed and has every expected bar, per the NYSE calendar in
  `market_calendar.py`, including 1:00 PM half-days. Stored sessions are never
  rewritten. A later provider change is counted, not applied.
- Futures (GC=F) are excluded until a futures session calendar exists.

## Time outputs
- `time` is the **centre of the best ±60-minute window**. It is the point
  that maximises the chance the extreme falls within an hour either side
  (`p60`). It is not the most likely exact bar.
- `topBins[0]` is the **likeliest single 15-minute bar** (the mode), with its
  own probability. The panel shows the mode as the headline and the window
  centre beside it.
- The window centre is the prior-60-session best fixed clock, so on time
  `hilo-1` equals that comparator by construction. Retrospective and forward
  results compare it against the open, and against the legacy app where its
  calls exist. A model that changes timing must also be reported against
  this fixed-clock comparator.

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
2. **Tested**: the unit gate passes in CI before publication.
3. **Committed / deployed**: merged to main and published by the refresh
   workflow (build commit shown on the page).
4. **Forward-proven**: assessed per output. It needs at least 20 complete
   forward sessions of premarket records, and a paired interval that beats
   its baseline and excludes zero.

The retrospective replay is labelled as such and is never proof. Model hilo-1
is a baseline to improve on, not a claimed edge.
