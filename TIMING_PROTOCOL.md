# Timing scorecard v1

The primary research objective is the date of a reversal. Price-target error is
reported separately and is not evidence of timing skill or trading profit.

## Fixed scoring rules

- Protocol: `daily-close-turns-v1`. Forward cohort starts at midnight Eastern
  September 24, 2026. Earlier original calls are a **historical audit** because
  this scoring definition was selected after those outcomes existed.
- A reference turn is a strict closing high or low relative to two available
  daily sessions on either side. Equal extremes are excluded. Confirmation
  occurs only after the two later sessions complete. This reference is a small
  daily-close turn, not necessarily a major swing or an intraday extreme.
- Use the first timestamped original per ticker, target date and direction.
  Require its target date and any matched turn to be later than the date of
  logging, generation and last observed bar. Never improve a call by replacing
  it with a revision. Changing the target date creates another call and can
  increase false alarms, rather than erase the old call.
- Match only the same turn direction within two sessions. Process calls in
  earliest-issued order, then claim the nearest unclaimed turn (earlier turn
  breaks a tie). One turn earns at most one hit. This is a fixed assignment
  rule, not a hindsight search for the best pairing.
- Wait until the full window and both confirmation sessions are closed.
  Both the analysis build and review must be on a later Eastern date than any
  bar used. Do not shift an absent target date to a more convenient session.
- Timing error = predicted session index minus actual session index. Negative
  is early; positive is late. Show false alarms separately, so the median error
  among matched calls cannot hide failures.
- Missed-turn coverage begins after the first logged snapshot and ends six
  sessions before the latest closed bar: even a call two sessions after a turn
  must have time to complete its window and confirmation. The coverage period
  therefore differs from the set of scored calls; display its end explicitly.
- No strategy weights, trading rules, brokerage orders or originals are changed.
  `daily_review.json` carries the full audit; `data.js` includes a compact
  per-ticker scorecard refreshed by the existing GitHub workflow.

The current daily feed may be revised by the provider. This audit is recomputed
against its latest completed bars and is not an immutable market-data archive.
Intraday timing is not inferred from daily closes, astronomy event times, or
planetary-hour labels. Gold futures use provider session labels and must be
evaluated separately from regular-hours equities.

## Gann / cycle / astronomy research gate

Gann's *The Tunnel Thru the Air* can supply research hypotheses; its narrative
and claims do not establish reproducible timing accuracy for this app.
Source: https://www.gutenberg.org/ebooks/74988

The method-tag table describes methods present in blended forecasts. Its
groups overlap. It cannot establish which method caused a hit, and must not
be used to promote Gann or astrology weights.

Next experiment (not yet implemented): predeclare a small set of standalone
rules, their anchor selection, maximum forecast count and lead times. Compare
(1) simple calendar/swing-spacing controls, (2) Gann calendar counts, (3) Hurst/
Fibonacci cycles, and (4) explicit astronomy-event rules, then evaluate adding
each family to the same baseline. Store predictions before their windows open.
Keep the final test period untouched by selection, and record every variation
tried. Previously inspected data must not be relabeled unseen.

Promotion requires evidence across independent time blocks and market regimes,
with uncertainty intervals that account for correlated tickers and overlapping
forecasts. The required sample should follow a predeclared power/effect-size
analysis, not an arbitrary number of profitable days. Compare both hit rate and
missed turns at comparable signal frequency and window width.

Run a separate executable trade simulation with next-available fills, spread,
fees, slippage, turnover and drawdown. No return target is a tuning objective.
Research background: https://scholarworks.wmich.edu/math_pubs/42/

## Verification

Run the Python regression suite including `test_timing_review.py`, then
`python reliability.py`, `python coherence_check.py`, `python anomaly_audit.py`,
`node smoke_test.js`, and `node reliability_test.js`.

Compare every existing forecast snapshot and horizon row before/after replay.
Only code, the template and tests are submitted in the PR; the cloud refresh
generates and publishes data. Verify live HTML/data/review bytes against the
successful bot commit before claiming publication.
