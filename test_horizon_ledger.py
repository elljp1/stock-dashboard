from copy import deepcopy
from unittest import TestCase, main

from horizon_ledger import original_horizons, record_horizon


def row(ticker="QQQ", logged="2026-09-10", session="2026-09-11", price=700):
    return {"ticker": ticker, "logged": logged, "session": session,
            "h": {"daily": {"high": {"price": price},
                              "low": {"price": price - 10}}}}


class HorizonLedgerTests(TestCase):
    def test_duplicate_session_is_not_appended(self):
        first = row(logged="2026-09-09", price=701)
        entries = [first]
        self.assertFalse(record_horizon(entries, row(price=705)))
        self.assertEqual(entries, [first])

    def test_later_session_on_same_day_is_preserved_separately(self):
        entries = [row(session="2026-09-10")]
        later = row(session="2026-09-11")
        self.assertTrue(record_horizon(entries, later))
        self.assertEqual(entries, [row(session="2026-09-10"), later])

    def test_stale_same_day_run_cannot_move_session_backward(self):
        entries = [row(session="2026-09-11")]
        self.assertFalse(record_horizon(entries, row(session="2026-09-10")))
        self.assertEqual(len(entries), 1)

    def test_other_ticker_does_not_block_append(self):
        entries = [row(ticker="SPY")]
        self.assertTrue(record_horizon(entries, row(ticker="QQQ")))
        self.assertEqual(len(entries), 2)

    def test_grading_uses_earliest_forecast_per_session_without_mutation(self):
        entries = [row(logged="2026-09-10", price=705),
                   row(logged="2026-09-09", price=701),
                   row(logged="2026-09-08", session="2026-09-10", price=690)]
        before = deepcopy(entries)
        result = original_horizons(entries, "QQQ")
        self.assertEqual([x["session"] for x in result],
                         ["2026-09-10", "2026-09-11"])
        self.assertEqual(result[1]["h"]["daily"]["high"]["price"], 701)
        self.assertEqual(entries, before)


if __name__ == "__main__":
    main()
