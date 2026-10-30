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

- **TSLA bias (9/14):** Stuart expects a TSLA drop in October. No TSLA put credit spreads. Call credit spreads only, sold into a bounce (up ≥1.5% or RSI ≥60), $10 wide, expiring before the Oct 21 earnings. **10/15:** Stuart trades on technicals only; earnings no longer block a setup (flagged in the alert instead). The 9/14 TSLA 335/325 put spread alert ($2.33 mid) was declined for this reason.

## Pre-trade card (shown before every order)
Ticker, structure, expiry and DTE, spot, spread mid vs. limit, short delta and IV,
breakeven, max profit, max loss, collateral held, probability of profit,
return on risk at expiry and at target, % of account at risk, earnings date, fees.

## Executed trades (all accounts, numbered in fill order)
Only filled trades get a number. Old internal ids are in the Ref column.
| # | Date | Account | Trade | In | Out | Closed | Result |
|---|---|---|---|---|---|---|---|
| 1 | 9/16 | Agentic | HOOD 10/23 100/95 put credit spread x2 | $1.85 | $0.90 | 9/18 | **+$190** |
| 2 | 9/23 | Agentic | GOOGL 10/23 325/320 put credit spread x3 | $1.25 | $1.20 | 9/24 | **+$15** |
| 3 | 9/24 | Agentic | QQQ 10/23 770/780 call credit spread x2 | $2.00 | $1.48 | 10/8 | **+$104** |
| 4 | 9/30 | Individual | TSLA 10/30 330 put x2 (short) | $10.00 | $8.00 / $7.00 | 10/1 | **+$500** |
| 5 | 9/30 | Joint | TSLA 10/30 330 put x3 (short) | $10.00 | $8.00 x2 / $7.00 | 10/1 | **+$700** |
| 6 | 10/5 | Agentic | HOOD 10/30 101/96 put credit spread x3 | $1.05 | | | open (exit order $1.00 GTC resting since 10/15 10:38am; the $0.50 order was cancelled) |
| 7 | 10/8 | Individual | META 10/30 700 put x1 (short) | $24.43 | $19.00 | 10/9 | **+$543** |
| 8 | 10/8 | Joint | META 10/30 700 put x1 (short) | $24.00 | $19.00 | 10/9 | **+$500** |
| 9 | 10/16 | Agentic | META 11/20 670/660 put credit spread x2 | $2.50 | | | open (exit order $1.25 GTC resting since 10/16 11:13am) |
| 10 | 10/16 | Individual | QQQ 11/20 700 put x1 (short) | $12.50 | | | open |
| 11 | 10/16 | Joint | QQQ 11/20 700 put x1 (short) | $12.50 | | | open |
| 12 | 10/16 | Individual | TSLA 11/20 330 put x1 (short) | $10.00 | | | open |
| 13 | 10/16 | Joint | TSLA 11/20 330 put x1 (short) | $10.00 | | | open |
| 14 | 10/16 | Individual | QQQ 11/20 700 put x1 (short) | $16.03 | | | open |
| 15 | 10/16 | Joint | QQQ 11/20 700 put x1 (short) | $16.00 | | | open |

Closed: 7 trades, 7 wins, **+$2,552** (Agentic +$309, Individual +$1,043, Joint +$1,200).

## Orders that never filled (not counted)
| # | Date | Account | Order | Result |
|---|---|---|---|---|
| U1 | 9/10 | Agentic | GOOGL 10/23 305/300 put spread x1 @ $1.20 | cancelled 9/10 |
| U2 | 9/10 | Agentic | GOOGL 10/23 310/305 put spread x1 @ $1.20 | cancelled 9/12 (broker) |
| U3 | 9/10 | Individual | GOOGL 10/9 325 put x1 @ $10.00 | cancelled 9/14 |
| U4 | 9/10 | Joint | GOOGL 10/9 325 put x1 @ $10.00 | cancelled 9/14 |
| U5 | 9/16 | Agentic | HOOD 10/23 100/95 put spread x2 (second order) | cancelled 9/16 |
| U6 | 9/16 | Agentic | QQQ 10/23 685/680 put spread x2 @ $1.55 | cancelled 9/18 |
| U7 | 9/21 | Individual | HOOD 10/23 140 covered call x2 @ $5.00 | cancelled 9/28 |
| U8 | 10/8 | Individual | JPM 10/30 330 put x1 @ $10.00 | cancelled 10/13 2:21pm, never filled |
| U9 | 10/8 | Joint | JPM 10/30 330 put x1 @ $10.00 | cancelled 10/13 2:21pm, never filled |

## Agentic order log (internal ids; see numbered list above)
| # | Opened | Ticker | Structure | Credit | Max loss | BE | POP | % acct | Exit target | Closed | P&L |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | cancelled 9/10 2:13pm, never filled | GOOGL | 10/23 $305/$300 put credit spread x1 | $1.20 limit (mid $0.93) | $380 | $303.80 | 81% | 3.5% | $0.60 | | |
| 2 | cancelled 9/12 5:34am ET (broker-side, never filled; placed 9/10 2:19pm) | GOOGL | 10/23 $310/$305 put credit spread x1 | $1.20 limit (mid $1.03) | $380 | $308.80 | 79% | 3.5% | $0.60 | | |
| 3 | 9/16 11:34am | HOOD | 10/23 $100/$95 put credit spread x2 | $1.85 | $630 | $98.15 | 72% | 5.7% | $0.90 | 9/18 10:20am at $0.90 | **+$190** (30% on risk, 2 days) |
| 6 | 9/23 11:27am | GOOGL | 10/23 $325/$320 put credit spread x3 | $1.25 | $1,125 | $323.75 | 76% | 10.2% | $1.20 GTC (replaced $0.60 9/24) | 9/24 12:41pm at $1.20 | **+$15** (break-even; exited against the app's leg) |
| 7 | 9/24 3:53pm | QQQ | 10/23 $770/$780 call credit spread x2 | $2.00 | $1,600 | $772.00 | ~82% | 14.5% (user accepted) | $1.00 GTC, replaced by user with $1.50 GTC 10/8 | 10/8 1:04pm at $1.48 | **+$104** (26% of max) |
| 8 | 10/5 2:45pm | HOOD | 10/30 $101/$96 put credit spread x3 | $1.05 | $1,185 | $99.95 | ~78% | 10.8% (25.3% total with #7, user accepted) | $0.53 or the 10/19 projected high (~121; app turn moved 10/22 → 10/09 → 10/19 → 10/15 → 10/19 on 10/8, low 10/09 ~104 first); stop $2.10 / HOOD close below $101 | | closed 10/30: 2 by early assignment/exercise + last at $5.10; **-$1,195** |
| 9 | 10/16 10:16am | META | 11/20 $670/$660 put credit spread x2 | $2.50 | $1,500 | $667.50 | ~76% | 13.6% (24.4% total with #8) | $1.25 or the 11/16 projected high (~837); entered before the 10/19 low (~710), against the app's leg until then; stop $5.00 / 670 breached; exit order $1.25 GTC placed 10/16 11:13am | | open |

## Monthly results
| Month | Start | Deposits | Realized P&L | Growth | Trades | W/L |
|---|---|---|---|---|---|---|
| 2026-09 | $11,000 (incl. $10k deposit 9/9) | $10,000 | +$205 | +1.9% | 2 | 2/0 |
| 2026-10 | $11,205 | $0 | +$104 | +0.9% | 1 | 1/0 |

## Other-account orders (read-only, not part of the spread P&L)
| Account | Order | Limit | Status | Collateral | Placed |
|---|---|---|---|---|---|
| Individual | Sell GOOGL $325 put 10/9 x1 | $10.00 GTC | cancelled 9/14 8:33pm ET, never filled | $32,500 | 9/10 2:27pm |
| Joint | Sell GOOGL $325 put 10/9 x1 | $10.00 GTC | cancelled 9/14 8:33pm ET, never filled | $32,500 | 9/10 2:26pm |
| Individual | Sell to open HOOD $140 call 10/23 x2 (covered call) | $5.00 GTC | cancelled 9/28 2:35pm ET, never filled | 200 of 700 HOOD shares | 9/21 9:44am |

| Individual | Sell to open TSLA $330 put 10/30 x2 | $10.00 GTC | filled 9/30 9:44am at $10.00 ($2,000); closed: 1 at $8.00 on 9/30 1:41pm (+$200), 1 at $7.00 on 10/1 9:30am (+$300); +$500 total | $66,000 | 9/30 9:43am |
| Joint | Sell to open TSLA $330 put 10/30 x3 | $10.00 GTC | filled 9/30 9:44am at $10.00 ($3,000); closed: 2 at $8.00 on 9/30 1:41pm (+$400), 1 at $7.00 on 10/1 9:30am (+$300); +$700 total | $99,000 | 9/30 9:43am |
| Individual | Sell to open META $700 put 10/30 x1 | $24.00 GTC | filled 10/8 1:07pm at $24.43 ($2,443); closed 10/9 12:45pm: bought back at $19.00, **+$543** | $70,000 | 10/8 1:07pm |
| Joint | Sell to open META $700 put 10/30 x1 | $24.00 GTC | filled 10/8 1:08pm at $24.00 ($2,400); closed 10/9 12:45pm: bought back at $19.00, **+$500** | $70,000 | 10/8 1:08pm |
| Individual | Sell to open JPM $330 put 10/30 x1 | $10.00 GTC | cancelled by user 10/13 2:21pm, never filled | $33,000 | 10/8 2:53pm |
| Joint | Sell to open JPM $330 put 10/30 x1 | $10.00 GTC | cancelled by user 10/13 2:21pm, never filled | $33,000 | 10/8 2:53pm |
| Individual | Sell to open QQQ $700 put 11/20 x2 (two orders) | $13.15 + $13.40 GFD | filled 10/15 9:54am at $13.15 and 9:55am at $13.40 (avg $13.275, $2,655); closed 10/15 10:58am: both bought back at $10.00, **+$655** | $140,000 | 10/15 9:54am |
| Individual | Sell to open QQQ $700 put 11/20 x1 (third) | $13.40 GTC | cancelled 10/16 11:17am (replaced at $12.50) | $70,000 | 10/15 10:01am |
| Joint | Sell to open QQQ $700 put 11/20 x1 | $13.40 GTC | cancelled 10/16 11:16am (replaced at $12.50) | $70,000 | 10/15 11:27am |
| Individual | Sell to open QQQ $700 put 11/20 x1 | $12.50 GTC | filled 10/16 12:02pm at $12.50; closed 10/19 10:18am at $10.00, **+$250** | $70,000 | 10/16 11:17am |
| Joint | Sell to open QQQ $700 put 11/20 x1 | $12.50 GTC | filled 10/16 12:02pm at $12.50; closed 10/19 10:18am at $10.00, **+$250** | $70,000 | 10/16 11:16am |
| Individual | Sell to open QQQ $700 put 11/20 x1 | $16.00 GFD | filled 10/16 1:22pm at $16.03; closed 10/19 10:18am at $10.00, **+$603** ($6.50/$8.00 close orders cancelled) | $70,000 | 10/16 1:22pm |
| Joint | Sell to open QQQ $700 put 11/20 x1 | $16.00 GFD | filled 10/16 1:22pm at $16.00; closed 10/19 10:18am at $10.00, **+$600** ($6.50/$8.00 close orders cancelled) | $70,000 | 10/16 1:22pm |
| Individual | Sell to open TSLA $330 put 11/20 x1 | $10.00 GTC | filled 10/16 1:03pm at $10.00; closed 10/19 9:50am at $7.30, **+$270** ($5.00 GTC cancelled) | $33,000 | 10/15 3:11pm |
| Joint | Sell to open TSLA $330 put 11/20 x1 | $10.00 GTC | filled 10/16 1:03pm at $10.00; closed 10/19 9:50am at $7.30, **+$270** ($5.00 GTC cancelled) | $33,000 | 10/15 3:12pm |
| Individual | Sell to open META $670 put 11/20 x1 | $25.00 GTC | filled 10/20 9:30am at $25.00; closed 10/21 9:40am at $20.00 (buy to close placed 10/20 9:32am), +$500 | $67,000 | 10/19 1:29pm |
| Joint | Sell to open META $670 put 11/20 x1 | $25.00 GTC | filled 10/20 9:30am at $25.00; closed 10/21 9:40am at $20.00 (buy to close placed 10/20 9:32am), +$500 | $67,000 | 10/19 1:28pm |
| Individual | Sell to open META $650 put 11/20 x1 | $25.00 GTC | filled 10/22 9:36am at $25.00; buy to close $20.00 GTC resting (placed 10:00am) | $65,000 | 10/22 9:32am |
| Joint | Sell to open META $650 put 11/20 x1 | $25.00 GTC | filled 10/22 9:36am at $25.00; buy to close $20.00 GTC resting (placed 10:00am) | $65,000 | 10/22 9:33am |
| Individual | Sell to open QQQ $685 put 11/20 x1 | $12.50 GTC | filled 10/22 12:50pm at $12.50; bought to close 10/27 11:02am at $6.25, +$625 (+50%) | $68,500 | 10/22 10:40am |
| Joint | Sell to open QQQ $685 put 11/20 x1 | $12.50 GTC | filled 10/22 12:50pm at $12.50; bought to close 10/27 11:02am at $6.25, +$625 (+50%) | $68,500 | 10/22 10:40am |

## Alert log (graded at expiry, taken or not)

| # | Date | Setup | Mid at alert | Taken | Outcome |
|---|---|---|---|---|---|
| 1 | 9/14 | TSLA 10/16 335/325 put | $2.33 | No (user bearish) | void (user retired spread alerts 10/30) |
| 2 | 9/14 | GOOGL 10/23 370/375 call | $1.03 (later $1.18) | No | void (user retired spread alerts 10/30) |
| 3 | 9/14 | GOOGL 10/23 375/380 call | $1.05 | No | void (user retired spread alerts 10/30) |
| 4 | 9/15 9:36am | HOOD 10/23 95/90 put | $1.15 (10:34am $0.98) | No | void (user retired spread alerts 10/30) |
| 5 | 9/15 10:34am | HOOD 10/23 100/95 put | $1.41 (limit $1.45) | Yes, 2x at $1.85 GTC (trade 3) | FILLED 9/16 at $1.85, CLOSED 9/18 10:20am at $0.90, +$190 |
| 6 | 9/15 11:46am | GOOGL 10/23 325/320 put | $1.23 (limit $1.25) | Pushed, open | void (user retired spread alerts 10/30) |
| 7 | 9/16 9:35am | HOOD 10/23 95/90 put | $1.14 (limit $1.15) | Pushed, open | void (user retired spread alerts 10/30) |
| 8 | 9/16 10:35am | HOOD 10/23 95/90 put | $1.29 (limit $1.45 GTC, app low $100.21 on 9/17) | Pushed, open (re-alert of #7) | void (user retired spread alerts 10/30) |
| 9 | 9/16 3:04pm | HOOD 10/23 90/85 put | $1.02 (limit $1.15 GTC, app low $100.21 on 9/17) | Pushed, open | void (user retired spread alerts 10/30) |
| 10 | 9/18 9:46am | GOOGL 10/23 385/390 call | $1.18 (limit $1.20; quotes wide, app high $372.21 on 9/25) | Pushed, open | void (user retired spread alerts 10/30) |
| 11 | 9/21 | QQQ 10/23 765/775 call | $2.09 | No | void (user retired spread alerts 10/30) |
| 12 | 9/23 | GOOGL 10/23 325/320 put | $1.20 | Yes (trade 6, $1.25) | closed 9/24 at $1.20, +$15 |
| 13 | 9/23 11:46am | GOOGL 10/23 320/315 put | $1.00 | No | void (user retired spread alerts 10/30) |
| 14 | 9/23 3:33pm | GOOGL 10/23 320/315 put (re-alert) | $1.10 | No | void (user retired spread alerts 10/30) |
| 15 | 9/24 9:37am | QQQ 10/23 760/770 call (timing: leg down to 10/15 low) | $2.40 (limit $2.60 GTC) | No | void (user retired spread alerts 10/30) |
| 16 | 9/24 3:09pm | QQQ 10/23 770/780 call (timing: leg down to 10/15 low; answer to user question) | $1.92 (limit $2.00 GTC) | Yes, 2x at $2.00 GTC (trade 7) | closed 10/8 1:04pm at $1.48, +$104 |
| 17 | 9/25 9:34am | GOOGL 10/09 360/365 call (timing: leg down to 10/07 low) | $1.05 (limit $1.05, 2x) | Pushed, open | void (user retired spread alerts 10/30) |
| 18 | 9/28 3:06pm | GOOGL 10/09 355/360 call (timing: leg down to 10/07 low) | $1.02 (limit $1.00, 2x) | Pushed, open | void (user retired spread alerts 10/30) |
| 19 | 9/29 3:05pm | META 10/23 790/800 call (timing: leg down to 10/19 low) | $2.00 (limit $2.00, 1x) | Pushed, open | void (user retired spread alerts 10/30) |
| 20 | 9/30 9:35am | QQQ 10/16 760/770 call (timing: place at the 10/01 high, leg down to 10/14 low) | $2.24 (limit $2.20, 1x) | Pushed, open | void (10/01 high removed by 10/1 refresh) |
| 21 | 10/1 9:47am | HOOD 10/23 103/98 put (timing: place at the 10/02 low, leg up to 10/19 high) | $1.03 (limit $1.00, 3x) | Pushed, open | void (10/02 low cut to $104, 3% rule fails) |
| 22 | 10/1 12:17pm | HOOD 10/23 103/98 put (re-alert of 21, mid +$0.16; place at the 10/02 low) | $1.19 (limit $1.15, 3x) | Pushed, open | void (10/2: low back to $103.97, HOOD gapped to $117) |
| 23 | 10/1 2:34pm | QQQ 10/16 760/770 call (timing: place at the 10/02 high, leg down to 10/14 low) | $2.28 (limit $2.25, 1x) | Pushed, open | void (10/2: QQQ gapped to $750, 760 delta 0.37) |
| 24 | 10/2 9:35am | META 10/23 790/800 call (timing: leg down to 10/19 low) | $2.10 (limit $2.05, 1x) | Pushed, open | void (10/2 3:33pm: superseded by 27, 790/800 down to $1.30) |
| 25 | 10/2 2:34pm | HOOD 10/23 104/99 put (timing: place at the 10/05 low, leg up to 10/19 high) | $1.025 (limit $1.00, 3x) | Pushed, open | void (10/2 3:05pm: 10/05 low back to $106.28, 104 fails the 3% rule) |
| 26 | 10/2 2:34pm | QQQ 10/16 765/775 call (timing: 10/02 high passed, leg down to 10/14 low) | $2.055 (limit $2.05, 1x) | Pushed, open | void (user retired spread alerts 10/30) |
| 27 | 10/2 3:33pm | META 10/23 770/780 call (timing: leg down to 10/19 low) | $2.10 (limit $2.05, 1x) | Pushed, open | void (10/5 9:47am: superseded by 29, 770 delta 0.32) |
| 28 | 10/5 9:35am | HOOD 10/30 100/95 put (timing: place at the 10/05 low, leg up to 10/22 high) | $1.015 (limit $1.00, 3x) | Pushed, open | void (10/5 10:34am: superseded by 30) |
| 29 | 10/5 9:47am | META 10/23 780/790 call (timing: leg down to 10/19 low) | $2.075 (limit $2.05, 1x) | Pushed, open | void (10/5 11:46am: superseded by 31, 780 delta 0.31) |
| 30 | 10/5 10:34am | HOOD 10/30 102/97 put (timing: place at the 10/05 low, leg up to 10/22 high) | $1.17 (limit $1.15, 3x) | Pushed, open | void (10/5 2:35pm: superseded by 33) |
| 31 | 10/5 11:46am | META 10/23 790/800 call (timing: leg down to 10/19 low) | $2.00 (limit $2.00, 1x) | Pushed, open | void (user retired spread alerts 10/30) |
| 32 | 10/5 2:35pm | QQQ 10/16 770/780 call (timing: place at the 10/05 high, leg down to 10/14 low) | $2.05 (limit $2.05, 1x) | Pushed, open | void (user retired spread alerts 10/30) |
| 33 | 10/5 2:35pm | HOOD 10/30 101/96 put (timing: place at the 10/05 low, leg up to 10/22 high) | $1.015 (limit $1.00, 3x) | Taken (trade 8, 3x at $1.05) | pending |
| 34 | 10/6 3:46pm | HOOD 10/23 104/99 put (timing: place at the 10/07 low, leg up to 10/19 high; over 25% risk cap, duplicates trade 8) | $1.01 (limit $1.00, 3x) | Pushed, open | void (10/7: app low moved to 99.47, 104 short fails 3% rule) |
| 35 | 10/7 9:35am | META 10/23 770/780 call (timing: leg down to 10/19 low ~653; over 25% risk cap) | $2.025 (limit $2.00, 1x) | Pushed, open | void (10/7 10:34am: superseded by 36) |
| 36 | 10/7 10:34am | META 10/23 760/770 call (timing: leg down to 10/19 low ~642; over 25% risk cap) | $2.00 (limit $2.00, 1x); re-pushed 11:47am at $2.125 (limit $2.10) | Pushed, open | void (user retired spread alerts 10/30) |
| 37 | 10/7 2:34pm | QQQ 10/23 775/785 call (timing: place at the 10/07 high ~763, leg down to 10/21 low ~735; stacks on trade 7, over 25% risk cap) | $2.035 (limit $2.00, 1x) | Pushed, open | void (10/8: turns moved, superseded by 39) |
| 38 | 10/8 9:35am | HOOD 10/23 100/95 put (timing: place at the 10/09 low ~104, leg up to 10/19 high ~121; doubles trade 8, over 25% risk cap) | $1.015 (limit $1.00, 3x) | Pushed, open | void (user retired spread alerts 10/30) |
| 39 | 10/8 9:35am | QQQ 10/30 775/785 call (timing: place at the 10/09 high ~764, leg down to 10/22 low ~735; stacks on trade 7, over 25% risk cap) | $2.425 (limit $2.40, 1x) | Pushed, open | void (10/8 10:34am: superseded by 40) |
| 40 | 10/8 10:34am | QQQ 10/30 780/790 call (timing: place at the 10/09 high ~764, leg down to 10/22 low ~735; stacks on trade 7, over 25% risk cap) | $2.04 (limit $2.00, 1x) | Pushed, void 10/8 2:34pm (app dropped the 10/09 high; next QQQ turn is a 10/16 low) | void |
| 41 | 10/15 9:58am | META 11/06 675/665 put (timing: place at today's low ~710, leg up to 10/30 high ~801; spans META 10/21 report) | $2.275 (limit $2.25, 1x) | Pushed, void 10/16 9:47am (app moved the META high to 11/16; superseded by #44) | void |
| 42 | 10/15 9:58am | HOOD 11/06 85/80 put (timing: place at today's low ~94, leg up to 11/02 high ~118; spans HOOD 10/27 report; stacks on trade 8; with #41 over 25% risk cap) | $1.115 (limit $1.10, 3x) | Pushed, void 10/16 9:47am (app now projects a HOOD high 10/23; superseded by #43) | void |
| 43 | 10/16 9:47am | HOOD 10/30 94/89 put (timing: current leg up to 10/23 high ~120; spans HOOD 10/27 report; same expiry and bet as trade 8) | $1.02 (limit $1.00, 3x) | Pushed, open | void (user retired spread alerts 10/30) |
| 44 | 10/16 9:47am | META 11/20 670/660 put (timing: place at the 10/19 low ~710, leg up to 11/16 high ~837; spans META 10/21 report; with #43 and trade 8 over 25% risk cap) | $2.375 (limit $2.35, 1x) | Taken: trade 9 (user 2x at $2.50, filled 10/16 10:16am) | void (user retired spread alerts 10/30) |
| 45 | 10/16 2:35pm | GOOGL 10/30 320/315 put (timing: place at today's low ~335, leg up to 10/26 high ~353; spans GOOGL 10/28 report; over 25% risk cap with trades 8 and 9) | $1.05 (limit $1.05, 3x) | Pushed, open; re-pushed 3:46pm at $1.15 (limit $1.15) | void (user retired spread alerts 10/30) |
| 46 | 10/16 2:35pm | META 11/20 640/630 put (timing: place at the 10/19 low ~687, leg up to 11/16 high ~815; spans META 10/21 report; stacks on trade 9; over 25% risk cap) | $2.15 (limit $2.15, 1x) | Pushed; re-pushed 3:46pm at $2.275 (limit $2.25); superseded 10/19 by #47 | void |
| 47 | 10/19 9:35am | META 10/30 650/640 put (timing: place at today's low ~685, leg up to 10/26 high ~743; spans META 10/21 report; over 25% risk cap with trades 8 and 9) | $2.10 (limit $2.10, 1x) | Pushed; superseded 10/19 10:38am by #48 | void |
| 48 | 10/19 10:38am | META 10/30 645/635 put (timing: place at today's low ~685, leg up to 10/26 high ~744; spans META 10/21 report; over 25% risk cap with trades 8 and 9) | $2.00 (limit $2.00, 1x) | Pushed; superseded 10/19 11:47am by #49 | void |
| 49 | 10/19 11:47am | META 11/06 645/635 put (timing: place at today's low ~685, leg up to 10/30 high ~768; spans META 10/21 report; over 25% risk cap with trades 8 and 9) | $2.125 (limit $2.10, 1x) | Pushed, open | void (user retired spread alerts 10/30) |
| 50 | 10/20 9:40am | HOOD 11/06 93/88 put (timing: place at today's low ~93.89 2:29-3:24pm, leg up to 11/02 high ~114; strike from the app's low; credit 35% of width; spans HOOD 10/27 report) | $1.75 (limit $1.75, 4x) | Pushed, void 10/20 10:38am (app dropped today's HOOD low; next turn is a 10/23 high ~109) | void |
| 51 | 10/20 9:48am | GOOGL 10/30 332.5/327.5 put (timing: place at the 10/21 low ~334.84, leg up to 10/26 high ~349; strike from the app's low; credit 33% of width; spans GOOGL 10/28 report) | $1.65 (limit $1.65, 4x) | Pushed; re-pushed 2:39pm at $1.80 and 3:38pm at $1.925; superseded 10/21 by #52 (app moved the exit high to 11/02, low to ~326.10) | superseded |
| 52 | 10/21 9:39am | GOOGL 11/04 325/320 put (timing: place at today's low ~326.10 9:56-10:51am or 11:45am-12:40pm, leg up to 11/02 high ~346; strike from the app's low; credit 38.5% of width; spans GOOGL 10/28 report) | $1.925 (limit $1.90, 4x) | Pushed; superseded 9:47am by #53 (app moved the exit high to 11/04) | superseded |
| 53 | 10/21 9:47am | GOOGL 11/06 325/320 put (timing: place at today's low ~326.10, leg up to 11/04 high ~349; strike from the app's low; credit 36% of width; spans GOOGL 10/28 report; replaces #52) | $1.80 (limit $1.80, 4x) | Pushed; superseded 10/22 by #60 (app moved the low to 10/23 ~323.44) | superseded |
| 54 | 10/21 9:47am | TSLA 11/04 390/400 call (timing: place at today's high ~389.34, leg down to 10/30 low ~360; strike from the app's high; credit 40% of width; spans TSLA 10/21 report) | $4.025 (limit $4.00, 2x) | Pushed, void 10/21 10:38am (app raised today's TSLA high to ~397.30; 397.5/407.5 pays 32%) | void |
| 55 | 10/21 9:47am | META 11/13 675/665 put (timing: place at today's low ~679.69, leg up to 11/09 high ~781; strike from the app's low; credit 33% of width; spans META 10/21 report) | $3.325 (limit $3.30, 2x) | Pushed; 10:38am entry moved to 10/22; void 11:46am (app dropped the META low; next turn is an 11/04 high ~808) | void |
| 56 | 10/21 12:16pm | TSLA 11/04 397.5/407.5 call (timing: place at today's high ~397.30 2:29-4:00pm, leg down to 10/30 low ~367; strike from the app's high; credit 34% of width; spans TSLA 10/21 report) | $3.375 (limit $3.35, 2x) | Pushed; superseded 3:38pm by #58, restored 3:46pm; void 10/22 (high moved to 10/23; credit 26%) | void |
| 57 | 10/21 3:10pm | META 11/13 675/665 put (timing: place at the 10/22 low ~679.69 9:57-10:51am or 12:40-1:34pm, leg up to 11/09 high ~780; strike from the app's low; credit 36% of width; spans META 10/21 report; app restored the low after #55 was voided) | $3.55 (limit $3.50, 2x) | Pushed; void 10/22 (META fell to ~656; app low now 10/23 ~635; 630/620 pays 29%) | void |
| 58 | 10/21 3:38pm | TSLA 11/04 390/400 call (timing: place at today's high ~389.62 3:23-4:00pm, leg down to 10/30 low ~363; strike from the app's high; credit 41% of width; spans TSLA 10/21 report; replaces #56) | $4.125 (limit $4.10, 2x) | Pushed; superseded 3:46pm (app moved the high back to ~397.30, so #56 applies) | superseded |
| 59 | 10/22 11:18am | QQQ 11/03 705/695 put (timing: place at the 10/23 low ~705.82 9:57-10:51am, leg up to 10/30 high ~732; strike from the app's low; credit 34% of width) | $3.36 (limit $3.35, 2x) | Pushed; superseded 10/22 2:38pm by #65 (app lowered the low to ~703.06) | superseded |
| 60 | 10/22 11:18am | GOOGL 11/06 322.5/317.5 put (timing: place at the 10/23 low ~323.44 10:51-11:46am or 12:40-1:34pm, leg up to 11/04 high ~348; strike from the app's low; credit 41% of width; spans GOOGL 10/28 report; replaces #53) | $2.05 (limit $2.05, 4x) | Pushed; superseded 10/22 2:38pm by #64 (app lowered the low to ~316.40) | superseded |
| 61 | 10/22 11:50am | TSLA 11/04 390/400 call (timing: place at the 10/23 high ~389.64 9:30-10:51am or 3:22-4:00pm, leg down to 10/30 low ~363; strike from the app's high; credit 34% of width) | $3.40 (limit $3.40, 2x) | Pushed; void 10/22 2:38pm (TSLA fell to ~376; credit 26%) | void |
| 62 | 10/22 11:50am | HOOD 11/06 93/88 put (timing: place at the 10/23 low ~93.89 12:40-1:34pm, leg up to 11/02 high ~110; strike from the app's low; credit 33% of width; spans HOOD 10/27 report) | $1.665 (limit $1.65, 4x) | Pushed; re-pushed 10/22 2:38pm at $1.87; superseded 10/26 by #67 | superseded |
| 63 | 10/22 2:38pm | META 11/13 630/620 put (timing: place at the 10/23 low ~634.84 1:34-2:28pm, leg up to 11/09 high ~736; strike from the app's low; credit 39% of width) | $3.875 (limit $3.85, 2x) | Pushed; superseded 10/26 by #69 (low moved to 10/26 ~620) | superseded |
| 64 | 10/22 2:38pm | GOOGL 11/06 315/310 put (timing: place at the 10/23 low ~316.40 10:51-11:46am or 12:40-1:34pm, leg up to 11/04 high ~337; strike from the app's low; credit 34.5% of width; spans GOOGL 10/28 report; replaces #60) | $1.725 (limit $1.70, 4x) | Pushed; re-pushed 10/23 at $1.85 and $1.95; superseded 10/26 by #66 (low moved to 10/26) | superseded |
| 65 | 10/22 2:38pm | QQQ 11/03 700/690 put (timing: place at the 10/23 low ~703.06 9:57-10:51am, leg up to 10/30 high ~728; 693P not listed, so 700/690; credit 34% of width; replaces #59) | $3.37 (limit $3.35, 2x) | Pushed; void 10/26 (low ~699.76; 695/685 pays 21%) | void |
| 66 | 10/26 9:39am | GOOGL 11/06 315/310 put (timing: place at the 10/26 low ~316.40 9:30-9:59am, 10:52-11:46am or 3:19-4:00pm, leg up to 11/04 high ~337; credit 39.5% of width; spans GOOGL 10/28 report; replaces #64) | $1.975 (limit $1.95, 4x) | Pushed; re-pushed 10:03am at $2.075, 2:38pm at $2.275 (limit $2.25); superseded 10/27 by #71 (low moved to 10/28) | superseded |
| 67 | 10/26 9:39am | HOOD 11/06 91/86 put (timing: place at the 10/26 low ~91.36 10:52-11:46am, leg up to 11/02 high ~105; credit 36% of width; spans HOOD 10/27 report; replaces #62) | $1.81 (limit $1.80, 4x) | Pushed; re-pushed 10:03am at $2.065; void 10/28 (HOOD fell through 91 after earnings; replaced by #74) | void |
| 68 | 10/26 9:39am | TSLA 11/06 397.5/407.5 call (timing: place at the 10/27 high ~397.30 10:53am-12:39pm, leg down to 11/04 low ~363; credit 34% of width) | $3.425 (limit $3.40, 2x) | Pushed; superseded 10:03am by #70 (exit low moved to 11/05; expiry 11/13) | superseded |
| 69 | 10/26 9:39am | META 11/13 620/610 put (timing: place at the 10/26 low ~620.17 11:46am-12:39pm, leg up to 11/09 high ~707; credit 34% of width; replaces #63) | $3.40 (limit $3.40, 2x) | Pushed; re-pushed 10:03am at $3.85; superseded 10/27 by #72 (low moved to 10/28) | superseded |
| 70 | 10/26 10:03am | TSLA 11/13 400/410 call (timing: place at the 10/27 high ~397.30 10:53am-12:39pm, leg down to 11/05 low ~364; 11/13 has no 397.5 strike; credit 38% of width; replaces #68) | $3.80 (limit $3.80, 2x); re-pushed 11:46am $4.025 (limit $4.00) | Pushed; void 10/27 (high moved to ~406.89, TSLA above 400; replaced by #73) | void |
| 71 | 10/27 9:46am | GOOGL 11/06 310/305 put (timing: place at the 10/28 low ~311.76 10:00-10:53am or 11:46am-12:39pm, leg up to 11/04 high ~333; credit 33% of width; spans GOOGL 10/28 report; replaces #66) | $1.65 (limit $1.65, 4x); re-pushed 10:04am $1.825 (limit $1.80) | Pushed; void 10/28 (app dropped the 10/28 low) | void |
| 72 | 10/27 9:46am | META 11/13 615/605 put (timing: place at the 10/28 low ~616.30 12:39-1:32pm, leg up to 11/09 high ~697; credit 41% of width; replaces #69) | $4.125 (limit $4.10, 2x); re-pushed 4:04pm $4.225 (limit $4.20); re-pushed 10/28 9:48am $4.425 (limit $4.40) | Pushed; void 10/28 10:44am (low moved to ~594.85, below the 615 short) | void |
| 73 | 10/27 11:46am | TSLA 11/13 410/420 call (timing: place at today's high ~406.89 11:46am-12:39pm, leg down to 11/05 low ~379; credit 40% of width; replaces #70) | $3.975 (limit $3.95, 2x) | Pushed; void 10/28 (high moved to 10/29 ~411.67, above the 410 short) | void |
| 74 | 10/28 9:48am | HOOD 11/13 88/83 put (timing: place at today's low ~88.33 10:00-10:53am or 11:46am-12:39pm, leg up to 11/09 high ~105.54; credit 37% of width; replaces #67) | $1.84 (limit $1.80, 4x) | Pushed, open | void (user retired spread alerts 10/30) |
| 75 | 10/28 2:38pm | TSLA 11/13 412.5/422.5 call (timing: place at the 10/29 high ~411.67 11:46am-1:32pm, leg down to 11/05 low ~382; credit 35% of width) | $3.50 (limit $3.50, 2x) | Pushed; void 10/29 (exit low moved to 11/16, after the 11/13 expiry; replaced by #76) | void |
| 76 | 10/29 10:09am | TSLA 11/20 415/425 call (timing: place at today's high ~411.67 11:46am-1:32pm, leg down to 11/16 low ~368; credit 33% of width; replaces #75) | $3.325 (limit $3.30, 2x); re-pushed 10:48am $3.525 (limit $3.50) | Pushed; void 10/29 12:08pm (high moved to ~418.34, above the 415 short); reinstated 2:39pm (high back to ~411.67; mid $3.50) | void (user retired spread alerts 10/30) |
| 77 | 10/30 11:42am | QQQ 11/12 690/680 put (timing: place at today's low ~692.66 10:01-11:46am, leg up to 11/10 high ~707.71; credit 33.5% of width) | $3.35 (limit $3.35, 2x) | Pushed, open | void (user retired spread alerts 10/30) |
| 78 | 10/30 12:17pm | SELL PUT HOOD 11/20 80P (timing: today's low ~82.18, leg up to 11/16 high ~103.70; premium 4.0% of strike; collateral $8,000) | $3.175 (limit $3.15, 1x) | Pushed, open; re-pushed 2:38pm $3.95 | void (exit turn moved to 11/09; see #84) |
| 79 | 10/30 12:17pm | SELL CALL TSLA 11/20 415C, uncovered (timing: Mon 11/02 high ~411.67, leg down to 11/16 low ~369; premium 2.3% of strike) | $9.70 (limit $9.70, 1x) | Pushed, open; re-pushed 3:38pm $10.00, 4:05pm $10.30 | pending |
| 80 | 10/30 12:17pm | SELL PUT QQQ 11/12 690P (timing: today's low ~690.41, leg up to 11/10 high ~707.71; premium 1.8% of strike; collateral $69,000) | $12.675 (limit $12.65, 1x) | Pushed, open | void (strike moved to 685, see #82) |
| 81 | 10/30 2:38pm | SELL PUT META 11/13 592.5P (timing: today's low ~594.85, leg up to 11/09 high ~658.42; premium 2.0%; collateral $59,250) | $11.70 (1x) | Pushed, open | pending |
| 82 | 10/30 2:38pm | SELL PUT QQQ 11/12 685P (timing: today's low ~685.72, leg up to 11/10 high ~707.71; premium 2.3%; collateral $68,500; replaces #80) | $15.73 (limit $15.70, 1x) | Pushed, open | pending |
| 83 | 10/30 2:38pm | SELL PUT GOOGL 11/09 272.5P (timing: today's low ~274.96, leg up to 11/05 high ~293.99; premium 1.3%; collateral $27,250) | $3.65 (1x) | Pushed, open; re-pushed 3:04pm $3.90 | pending |
| 84 | 10/30 3:38pm | SELL PUT HOOD 11/13 80P (timing: today's low ~80.78, leg up to 11/09 high ~96.17; premium 3.4%; collateral $8,000; replaces #78) | $2.755 (limit $2.75, 1x) | Pushed, open | pending |

## Trade 3 (CLOSED 10:20am ET 9/18 at $0.90, +$190)

**PUT CREDIT SPREAD, HOOD Oct 23, sell $100 put / buy $95 put, 2 contracts, limit $1.85 credit, GTC.** First placed at $1.50 10:54am ET, replaced at $1.85 11:19am ET, then re-placed as GTC 11:22am ET (order 6aa962a6) to rest above the day's $1.60 high; the app projects a HOOD low near $103.51 on 9/16. Max loss $630, collateral $1,000, 5.7% of account. Exit if filled: buy to close at $0.90, or at $3.70 debit / HOOD below $100.

**Filled 11:34am ET 9/16: 2 contracts at $1.85 credit ($370), sold $100 put at $5.65 / bought $95 put at $3.80, HOOD $104.80, 37 DTE.** Exit: buy to close at $0.90 (50% of credit), or at $3.70 debit / HOOD under $100.  Take-profit order placed 11:42am ET: buy to close 2x at $0.90 GTC (order 6aaab8f4).

**Closed 10:20am ET 9/18: the $0.90 GTC take-profit filled (bought $100 put at $2.34, sold $95 put at $1.44) with HOOD at $117.08, up 6.6% on the day. P&L +$190 (51% of credit, 30% on the $630 at risk) in 2 days.** The mark showed $0.90 from about 10:19 but a buy-to-close fills against the ask side, so it needed the mid to dip to about $0.85.

## Trade 4 (cancelled 10:45am ET 9/16, unfilled)

**PUT CREDIT SPREAD, HOOD Oct 23, sell $100 put / buy $95 put, 2 contracts, limit $2.70 credit, GTC.** Placed 9:48am ET 9/16 (order 6aaa9e35) with HOOD at $107.25 and the spread mid at $1.68, resting for the app's projected low of $100.21 on Thu 9/17 at the open. Agent suggested 1x; user chose 2x. Max loss $460 per contract; if both trade 3 and trade 4 fill, 4 contracts and $1,090 at risk (9.9% of account, above the 8% cap; user accepted). Exit if filled: buy to close at $1.35, or at $5.40 debit / HOOD below $97.

## Trade 5 (cancelled 9:29am ET 9/18, unfilled)

**PUT CREDIT SPREAD, QQQ Oct 23, sell $685 put / buy $680 put, 2 contracts, limit $1.55 credit, GTC.** Placed 3:33pm ET 9/16 (order 6aaaef01) with QQQ at $701.77 and the spread mid at $1.21, resting for the app's projected low of $690.31 on Thu 9/17. User-initiated; agent advised the $1.55 rest and 1 contract, user chose 2. Short strike sits 0.8% under the projected low (no cushion). Max loss $690 (6.3%); with trade 3 open, $1,320 at risk (12%). Exit if filled: buy to close at $0.75, or at $3.10 debit / QQQ under $685. Cancelled by user 9:29am ET 9/18 with QQQ at $718.60 and the spread mid at $0.73; QQQ gapped over the projected low and the order never came close to filling.
