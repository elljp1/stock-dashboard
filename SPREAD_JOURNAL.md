# Spread Journal (Agentic account ••••2831)

Human-readable view of `spread_journal.json`. Every trade gets a pre-trade card
with the fields below before anything is placed, then a result row when closed.

## Platform limit
Robinhood rejects multi-leg orders placed through the agent in agentic accounts (confirmed 2026-09-09). Spreads are entered by hand in the app; the agent scans, reviews, tracks positions, and keeps this journal.

## Rules
- **Method (user, 9/23 4:15pm ET): timing-led.** Trade the app's current leg: next projected turn a LOW = call credit spread, a HIGH = put credit spread. Expiry just after the turn; exit at the turn or 50%; stop 2x credit. Replaces the down-day/RSI triggers and the 28-50 DTE window.
- Risk per trade: 8% to 13% of account value (max loss, not collateral); raised from 5-8% by the user on 9/18. Usually 3-4 contracts on a $5-wide GOOGL/HOOD spread, 1-2 on a $10-wide TSLA/QQQ spread. Total open risk across spreads under 25%.
- Entry: limit orders only, never market; don't chase below the planned floor
- Short strike: 15 to 28 delta, 28 to 50 days to expiry, expiry before earnings
- Credit at least 20% of spread width
- Exit: buy back at 50% of credit received (GTC order placed right after fill)
- Loss rule: close if the spread costs 2x the credit to buy back, or short strike is breached

- **TSLA bias (9/14):** Stuart expects a TSLA drop in October. No TSLA put credit spreads. Call credit spreads only, sold into a bounce (up ≥1.5% or RSI ≥60), $10 wide, expiring before the Oct 21 earnings. The 9/14 TSLA 335/325 put spread alert ($2.33 mid) was declined for this reason.

## Pre-trade card (shown before every order)
Ticker, structure, expiry and DTE, spot, spread mid vs. limit, short delta and IV,
breakeven, max profit, max loss, collateral held, probability of profit,
return on risk at expiry and at target, % of account at risk, earnings date, fees.

## Trades
| # | Opened | Ticker | Structure | Credit | Max loss | BE | POP | % acct | Exit target | Closed | P&L |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | cancelled 9/10 2:13pm, never filled | GOOGL | 10/23 $305/$300 put credit spread x1 | $1.20 limit (mid $0.93) | $380 | $303.80 | 81% | 3.5% | $0.60 | | |
| 2 | cancelled 9/12 5:34am ET (broker-side, never filled; placed 9/10 2:19pm) | GOOGL | 10/23 $310/$305 put credit spread x1 | $1.20 limit (mid $1.03) | $380 | $308.80 | 79% | 3.5% | $0.60 | | |
| 3 | 9/16 11:34am | HOOD | 10/23 $100/$95 put credit spread x2 | $1.85 | $630 | $98.15 | 72% | 5.7% | $0.90 | 9/18 10:20am at $0.90 | **+$190** (30% on risk, 2 days) |
| 6 | 9/23 11:27am | GOOGL | 10/23 $325/$320 put credit spread x3 | $1.25 | $1,125 | $323.75 | 76% | 10.2% | $1.20 GTC (replaced $0.60 9/24) | 9/24 12:41pm at $1.20 | **+$15** (break-even; exited against the app's leg) |
| 7 | resting since 9/24 3:18pm (GTC, not filled) | QQQ | 10/23 $770/$780 call credit spread x2 | $2.00 limit (mid $1.92) | $1,600 | $772.00 | ~82% | 14.5% (user accepted) | $1.00, or at the 10/15 projected low (stop $4.00 / QQQ above $770) | | resting |

## Monthly results
| Month | Start | Deposits | Realized P&L | Growth | Trades | W/L |
|---|---|---|---|---|---|---|
| 2026-09 | $11,000 (incl. $10k deposit 9/9) | $10,000 | +$205 | +1.9% | 2 | 2/0 |

## Other-account orders (read-only, not part of the spread P&L)
| Account | Order | Limit | Status | Collateral | Placed |
|---|---|---|---|---|---|
| Individual | Sell GOOGL $325 put 10/9 x1 | $10.00 GTC | cancelled 9/14 8:33pm ET, never filled | $32,500 | 9/10 2:27pm |
| Joint | Sell GOOGL $325 put 10/9 x1 | $10.00 GTC | cancelled 9/14 8:33pm ET, never filled | $32,500 | 9/10 2:26pm |
| Individual | Sell to open HOOD $140 call 10/23 x2 (covered call) | $5.00 GTC | open, unfilled (mark $3.90) | 200 of 700 HOOD shares | 9/21 9:44am |

## Alert log (graded at expiry, taken or not)

| # | Date | Setup | Mid at alert | Taken | Outcome |
|---|---|---|---|---|---|
| 1 | 9/14 | TSLA 10/16 335/325 put | $2.33 | No (user bearish) | pending |
| 2 | 9/14 | GOOGL 10/23 370/375 call | $1.03 (later $1.18) | No | pending |
| 3 | 9/14 | GOOGL 10/23 375/380 call | $1.05 | No | pending |
| 4 | 9/15 9:36am | HOOD 10/23 95/90 put | $1.15 (10:34am $0.98) | No | pending |
| 5 | 9/15 10:34am | HOOD 10/23 100/95 put | $1.41 (limit $1.45) | Yes, 2x at $1.85 GTC (trade 3) | FILLED 9/16 at $1.85, CLOSED 9/18 10:20am at $0.90, +$190 |
| 6 | 9/15 11:46am | GOOGL 10/23 325/320 put | $1.23 (limit $1.25) | Pushed, open | pending |
| 7 | 9/16 9:35am | HOOD 10/23 95/90 put | $1.14 (limit $1.15) | Pushed, open | pending |
| 8 | 9/16 10:35am | HOOD 10/23 95/90 put | $1.29 (limit $1.45 GTC, app low $100.21 on 9/17) | Pushed, open (re-alert of #7) | pending |
| 9 | 9/16 3:04pm | HOOD 10/23 90/85 put | $1.02 (limit $1.15 GTC, app low $100.21 on 9/17) | Pushed, open | pending |
| 10 | 9/18 9:46am | GOOGL 10/23 385/390 call | $1.18 (limit $1.20; quotes wide, app high $372.21 on 9/25) | Pushed, open | pending |
| 11 | 9/21 | QQQ 10/23 765/775 call | $2.09 | No | pending |
| 12 | 9/23 | GOOGL 10/23 325/320 put | $1.20 | Yes (trade 6, $1.25) | closed 9/24 at $1.20, +$15 |
| 13 | 9/23 11:46am | GOOGL 10/23 320/315 put | $1.00 | No | pending |
| 14 | 9/23 3:33pm | GOOGL 10/23 320/315 put (re-alert) | $1.10 | No | pending |
| 15 | 9/24 9:37am | QQQ 10/23 760/770 call (timing: leg down to 10/15 low) | $2.40 (limit $2.60 GTC) | No | pending |
| 16 | 9/24 3:09pm | QQQ 10/23 770/780 call (timing: leg down to 10/15 low; answer to user question) | $1.92 (limit $2.00 GTC) | Yes, 2x at $2.00 GTC (trade 7) | pending |

## Trade 3 (CLOSED 10:20am ET 9/18 at $0.90, +$190)

**PUT CREDIT SPREAD, HOOD Oct 23, sell $100 put / buy $95 put, 2 contracts, limit $1.85 credit, GTC.** First placed at $1.50 10:54am ET, replaced at $1.85 11:19am ET, then re-placed as GTC 11:22am ET (order 6aa962a6) to rest above the day's $1.60 high; the app projects a HOOD low near $103.51 on 9/16. Max loss $630, collateral $1,000, 5.7% of account. Exit if filled: buy to close at $0.90, or at $3.70 debit / HOOD below $100.

**Filled 11:34am ET 9/16: 2 contracts at $1.85 credit ($370), sold $100 put at $5.65 / bought $95 put at $3.80, HOOD $104.80, 37 DTE.** Exit: buy to close at $0.90 (50% of credit), or at $3.70 debit / HOOD under $100.  Take-profit order placed 11:42am ET: buy to close 2x at $0.90 GTC (order 6aaab8f4).

**Closed 10:20am ET 9/18: the $0.90 GTC take-profit filled (bought $100 put at $2.34, sold $95 put at $1.44) with HOOD at $117.08, up 6.6% on the day. P&L +$190 (51% of credit, 30% on the $630 at risk) in 2 days.** The mark showed $0.90 from about 10:19 but a buy-to-close fills against the ask side, so it needed the mid to dip to about $0.85.

## Trade 4 (cancelled 10:45am ET 9/16, unfilled)

**PUT CREDIT SPREAD, HOOD Oct 23, sell $100 put / buy $95 put, 2 contracts, limit $2.70 credit, GTC.** Placed 9:48am ET 9/16 (order 6aaa9e35) with HOOD at $107.25 and the spread mid at $1.68, resting for the app's projected low of $100.21 on Thu 9/17 at the open. Agent suggested 1x; user chose 2x. Max loss $460 per contract; if both trade 3 and trade 4 fill, 4 contracts and $1,090 at risk (9.9% of account, above the 8% cap; user accepted). Exit if filled: buy to close at $1.35, or at $5.40 debit / HOOD below $97.

## Trade 5 (cancelled 9:29am ET 9/18, unfilled)

**PUT CREDIT SPREAD, QQQ Oct 23, sell $685 put / buy $680 put, 2 contracts, limit $1.55 credit, GTC.** Placed 3:33pm ET 9/16 (order 6aaaef01) with QQQ at $701.77 and the spread mid at $1.21, resting for the app's projected low of $690.31 on Thu 9/17. User-initiated; agent advised the $1.55 rest and 1 contract, user chose 2. Short strike sits 0.8% under the projected low (no cushion). Max loss $690 (6.3%); with trade 3 open, $1,320 at risk (12%). Exit if filled: buy to close at $0.75, or at $3.10 debit / QQQ under $685. Cancelled by user 9:29am ET 9/18 with QQQ at $718.60 and the spread mid at $0.73; QQQ gapped over the projected low and the order never came close to filling.
