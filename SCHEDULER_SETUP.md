# Independent refresh scheduler — prepared, not activated

Cloudflare supplies the clock; the existing GitHub Actions workflow still downloads,
analyzes, tests and publishes. Keep GitHub cron as a fallback. This reduces reliance
on GitHub cron but still depends on GitHub runners, Pages and the quote provider.
Dispatch times are targets, not guaranteed publication times: a build takes time.

## Schedule

America/New_York weekdays: 06:00, 07:00, 08:00, 09:00, 09:15, 09:20, 09:25,
09:30, 09:35, 09:45, 10:00, then every half hour through 17:00.
Review daily at 18:00, including weekends. Daylight saving adjusts automatically.
Each minute checks the latest due slot against the live `daily_review.json`.
Overdue slots retry through 19:00 ET; a missed slot catches up to the latest due
slot rather than replaying old prices. Weekday holidays retain the requested
refresh cadence; price timestamps may properly remain at the prior market session.

## Required connection (owner action)

1. A Cloudflare account with Workers deployment access.
2. A GitHub credential authorized for **elljp1/stock-dashboard only**, with
   **Actions: read and write**. An owner-created fine-grained token can be used.
   Store it as the Cloudflare Worker secret `GITHUB_TOKEN`, never in chat or git.
   No repository contents-write permission is needed by this scheduler.
   Expiry or revocation must be handled before claiming unattended reliability.

## Activate after connecting

From this repository, using an authenticated Wrangler CLI:

```sh
node --test scheduler_test.mjs
npx wrangler deploy --config scheduler.wrangler.jsonc
npx wrangler secret put GITHUB_TOKEN --config scheduler.wrangler.jsonc
```

Then change `vars.ENABLED` to `"true"` in `scheduler.wrangler.jsonc` and deploy again.
The committed default is disabled, so uploading this code does not activate a
scheduler or claim that the schedule works. Do not remove the original refresh workflow.

## Required live acceptance

- Verify Cloudflare cron events execute at the next requested Eastern slot.
- Verify the corresponding GitHub workflow_dispatch run succeeds, including tests
  and Pages deployment. An accepted dispatch alone is not success.
- Verify the live daily_review.json and chart quote timestamps actually advance.
- Request the deployed Worker's `/health`: stale or unconfigured service returns
  HTTP 503; current/outside-schedule returns HTTP 200. Health is read-only.
- Observe successive slots, plus the next morning and 18:00 review, before calling
  scheduled operation proven. Check logs for authorization failures or stuck runs.
- Cloudflare trigger changes can require propagation time; verify events rather
  than assuming immediate activation.

Active runs suppress duplicate dispatches. A recent dispatch has a three-minute
cooldown. A run stuck for over 45 minutes fails visibly for operator review.
GitHub's existing concurrency group serializes runs; overlapping provider events
can still cause an extra rebuild. This is not exactly-once execution.
The health check measures analysis publication, not quote freshness or trading returns.

References:
- https://developers.cloudflare.com/workers/configuration/cron-triggers/
- https://docs.github.com/en/rest/actions/workflows#create-a-workflow-dispatch-event
