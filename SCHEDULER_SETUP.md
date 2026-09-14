# GitHub-only refresh scheduling

The active scheduler is .github/workflows/refresh.yml. No Vercel or Cloudflare
service, new account, or external dispatch credential is required or activated.
The earlier external-worker prototype files are inactive and are not called by
the refresh workflow. Forecast history and existing dashboard features remain.

## Requested schedule (America/New_York)

Weekdays: 06:00, 07:00, 08:00, 09:00, 09:15, 09:20, 09:25, 09:30, 09:35,
09:45, 10:00, then every half hour through 17:00. Daily review: 18:00,
including weekends. Weekday holidays keep this cadence; quote timestamps may
properly remain at the last market session.

## How it runs

One native Eastern-time GitHub cron checks every five minutes from 06:00
through the 19:00 recovery window. schedule_gate.py compares the latest due
slot with daily_review.json on the LIVE site. It runs the existing validated
refresh/deploy pipeline only when needed. There is no extra ten-minute grace
period. A delayed event catches up to the most recent due slot; it cannot
recreate past live quotes. Missing or invalid freshness data permits a rebuild.
Code pushes and manual workflow dispatch still trigger immediate rebuilds.
GitHub concurrency serializes refreshes. Each gate records its actual Eastern
check time, reason and decision in the run summary.

## Verification and limits

Run: python -m unittest test_schedule_gate.py
Tests cover every requested summer/winter slot, DST weekends, exact due times,
duplicate suppression, delayed events, missing data and evening cutoff.
After publishing, verify a run whose event is schedule, its successful refresh
and deployment, and the live data timestamps. A successful push/manual run
alone does not prove automatic scheduling is working.

GitHub documents that cron events may be delayed or dropped during high load.
This configuration simplifies scheduling and recovery; it cannot guarantee
exact starts or publications. The app's five-minute browser check only reads
finished analysis; it does not start server analysis.

Reference: https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#schedule

## Sept 14, 2026 update: GitHub cron is not delivering the schedule

Measured from the Actions run history (Aug 25 to Sep 14): the `*/5 6-19` cron
fired only 4 to 7 times per weekday, at irregular times two to three hours
apart, and zero times on Mon Sep 14 before 10:00 ET. GitHub queues and drops
high-frequency schedule events under load, so the gate only ever saw a handful
of the 30 requested weekday slots. Push and manual dispatch runs were fine.

Interim fix: Claude Code routines now call `workflow_dispatch` on refresh.yml
at every requested slot (6:00 to 17:00 on the hour and half hour, 9:15, 9:20,
9:25, 9:35, 9:45 weekdays, and 18:00 daily). Dispatch bypasses the gate and
always rebuilds. The GitHub cron stays in place as a fallback. Those routines
run on UTC cron and need a one-hour shift at each DST change; the Nov 1 DST
reminder covers them. The Cloudflare worker (`scheduler-worker.mjs`, currently
`ENABLED=false`) remains the better long-term clock if a Cloudflare account
and a GitHub token with `actions:write` are provisioned.
