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

## Pre-trade card (shown before every order)
Ticker, structure, expiry and DTE, spot, spread mid vs. limit, short delta and IV,
breakeven, max profit, max loss, collateral held, probability of profit,
return on risk at expiry and at target, % of account at risk, earnings date, fees.

## Trades
| # | Opened | Ticker | Structure | Credit | Max loss | BE | POP | % acct | Exit target | Closed | P&L |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | cancelled 9/10 2:13pm, never filled | GOOGL | 10/23 $305/$300 put credit spread x1 | $1.20 limit (mid $0.93) | $380 | $303.80 | 81% | 3.5% | $0.60 | | |
| 2 | working (GTC, placed 9/10 2:19pm) | GOOGL | 10/23 $310/$305 put credit spread x1 | $1.20 limit (mid $1.03) | $380 | $308.80 | 79% | 3.5% | $0.60 | | |

## Monthly results
| Month | Start | Deposits | Realized P&L | Growth | Trades | W/L |
|---|---|---|---|---|---|---|
| 2026-09 | $11,000 (incl. $10k deposit 9/9) | $10,000 | $0 | 0% | 0 | 0/0 |

## Other-account orders (read-only, not part of the spread P&L)
| Account | Order | Limit | Status | Collateral | Placed |
|---|---|---|---|---|---|
| Individual | Sell GOOGL $325 put 10/9 x1 | $10.00 GTC | working | $32,500 | 9/10 2:27pm |
| Joint | Sell GOOGL $325 put 10/9 x1 | $10.00 GTC | working | $32,500 | 9/10 2:26pm |
