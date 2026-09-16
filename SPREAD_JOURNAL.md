# Spread Journal (Agentic account ••••2831)

Human-readable view of `spread_journal.json`. Every trade gets a pre-trade card
with the fields below before anything is placed, then a result row when closed.

## Platform limit
Robinhood rejects multi-leg orders placed through the agent in agentic accounts (confirmed 2026-09-09). Spreads are entered by hand in the app; the agent scans, reviews, tracks positions, and keeps this journal.

## Rules
- Risk per trade: 5% to 8% of account value (max loss, not collateral)
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

## Monthly results
| Month | Start | Deposits | Realized P&L | Growth | Trades | W/L |
|---|---|---|---|---|---|---|
| 2026-09 | $11,000 (incl. $10k deposit 9/9) | $10,000 | $0 | 0% | 0 | 0/0 |

## Other-account orders (read-only, not part of the spread P&L)
| Account | Order | Limit | Status | Collateral | Placed |
|---|---|---|---|---|---|
| Individual | Sell GOOGL $325 put 10/9 x1 | $10.00 GTC | cancelled 9/14 8:33pm ET, never filled | $32,500 | 9/10 2:27pm |
| Joint | Sell GOOGL $325 put 10/9 x1 | $10.00 GTC | cancelled 9/14 8:33pm ET, never filled | $32,500 | 9/10 2:26pm |

## Alert log (graded at expiry, taken or not)

| # | Date | Setup | Mid at alert | Taken | Outcome |
|---|---|---|---|---|---|
| 1 | 9/14 | TSLA 10/16 335/325 put | $2.33 | No (user bearish) | pending |
| 2 | 9/14 | GOOGL 10/23 370/375 call | $1.03 (later $1.18) | No | pending |
| 3 | 9/14 | GOOGL 10/23 375/380 call | $1.05 | No | pending |
| 4 | 9/15 9:36am | HOOD 10/23 95/90 put | $1.15 (10:34am $0.98) | No | pending |
| 5 | 9/15 10:34am | HOOD 10/23 100/95 put | $1.41 (limit $1.45) | Yes, 2x at $1.85 GTC (trade 3) | FILLED 9/16 11:34am at $1.85 |
| 6 | 9/15 11:46am | GOOGL 10/23 325/320 put | $1.23 (limit $1.25) | Pushed, open | pending |
| 7 | 9/16 9:35am | HOOD 10/23 95/90 put | $1.14 (limit $1.15) | Pushed, open | pending |
| 8 | 9/16 10:35am | HOOD 10/23 95/90 put | $1.29 (limit $1.45 GTC, app low $100.21 on 9/17) | Pushed, open (re-alert of #7) | pending |

## Trade 3 (OPEN, filled 11:34am ET 9/16 at $1.85)

**PUT CREDIT SPREAD, HOOD Oct 23, sell $100 put / buy $95 put, 2 contracts, limit $1.85 credit, GTC.** First placed at $1.50 10:54am ET, replaced at $1.85 11:19am ET, then re-placed as GTC 11:22am ET (order 6aa962a6) to rest above the day's $1.60 high; the app projects a HOOD low near $103.51 on 9/16. Max loss $630, collateral $1,000, 5.7% of account. Exit if filled: buy to close at $0.90, or at $3.70 debit / HOOD below $100.

**Filled 11:34am ET 9/16: 2 contracts at $1.85 credit ($370), sold $100 put at $5.65 / bought $95 put at $3.80, HOOD $104.80, 37 DTE.** Exit: buy to close at $0.90 (50% of credit), or at $3.70 debit / HOOD under $100.  Take-profit order placed 11:42am ET: buy to close 2x at $0.90 GTC (order 6aaab8f4).

## Trade 4 (cancelled 10:45am ET 9/16, unfilled)

**PUT CREDIT SPREAD, HOOD Oct 23, sell $100 put / buy $95 put, 2 contracts, limit $2.70 credit, GTC.** Placed 9:48am ET 9/16 (order 6aaa9e35) with HOOD at $107.25 and the spread mid at $1.68, resting for the app's projected low of $100.21 on Thu 9/17 at the open. Agent suggested 1x; user chose 2x. Max loss $460 per contract; if both trade 3 and trade 4 fill, 4 contracts and $1,090 at risk (9.9% of account, above the 8% cap; user accepted). Exit if filled: buy to close at $1.35, or at $5.40 debit / HOOD below $97.
