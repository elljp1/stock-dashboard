# Spread Journal (Agentic account ••••2831)

Human-readable view of `spread_journal.json`. Every trade gets a pre-trade card
with the fields below before anything is placed, then a result row when closed.

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
| 1 | planned | GOOGL | 10/23 $305/$300 put credit spread x1 | $1.20 limit (mid $0.93) | $380 | $303.80 | 81% | 38% of $1k / 3.5% of $11k | $0.60 | | |

## Monthly results
| Month | Start | Deposits | Realized P&L | Growth | Trades | W/L |
|---|---|---|---|---|---|---|
| 2026-09 | $1,000 | $0 | $0 | 0% | 0 | 0/0 |
