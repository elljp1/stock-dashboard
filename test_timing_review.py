import copy
from datetime import date, timedelta
import unittest

from timing_review import (timing_review, confirmed_turns, eastern_day, chance_rate,
                           use_verdict, MIN_SCORED)


class TimingReviewTests(unittest.TestCase):
    def setUp(self):
        day = date(2026, 9, 1)
        self.days = []
        while len(self.days) < 25:
            if day.weekday() < 5:
                self.days.append(day.isoformat())
            day += timedelta(days=1)
        # Exactly one strict closing high at index 8.
        self.closes = [100+i if i <= 8 else 116-i for i in range(25)]
        self.data = {'TEST': {'generated': '2026-10-20 11:00 AM ET',
                              'chart': {'dates': self.days, 'closes': self.closes}}}
        self.now = '2026-10-20T15:00:00+00:00'

    def row(self, target=8, logged=1, kind='high', key='first'):
        return {'id': key, 'ticker': 'TEST', 'recordedAt': self.days[logged]+'T12:00:00-04:00',
                'generated': self.days[logged]+' 12:00 PM ET', 'lastBar': self.days[logged],
                'predictions': [{'isoDate': self.days[target], 'type': kind,
                                 'price': 1, 'methods': ['Gann 30 days', 'full moon']} ]}

    def score(self, rows):
        return timing_review(self.data, rows, self.now)['tickers']['TEST']

    def test_exact_early_late_and_price_independence(self):
        for target, error in [(6,-2), (8,0), (10,2)]:
            row = self.row(target)
            a = self.score([row])
            self.assertEqual(a['results'][0]['errorSessions'], error)
            row['predictions'][0]['price'] = 9999999
            self.assertEqual(a, self.score([row]))

    def test_needs_entire_window_plus_confirmation(self):
        row = self.row()
        for length, hits in [(12,0),(13,1)]:
            self.data['TEST']['chart'] = {'dates': self.days[:length], 'closes': self.closes[:length]}
            result = self.score([row])
            self.assertEqual(result['summary']['hits'], hits)
            self.assertEqual(result['pending'], 1-hits)

    def test_partial_build_cannot_be_finalized_by_later_review_clock(self):
        row = self.row()
        self.data['TEST']['generated'] = self.days[12]+' 03:59 PM ET'
        self.assertEqual(self.score([row])['summary']['scored'], 0)
        self.data['TEST']['generated'] = self.days[13]+' 12:00 AM ET'
        self.assertEqual(self.score([row])['summary']['hits'], 1)

    def test_one_turn_cannot_reward_multiple_calls(self):
        result = self.score([self.row(6), self.row(8,2,key='later')])
        self.assertEqual(result['summary']['hits'], 1)
        self.assertEqual(result['summary']['falseAlarms'], 1)
        self.assertEqual(result['results'][0]['targetDate'], self.days[6])

    def test_revision_order_does_not_replace_first_and_inputs_unchanged(self):
        first = self.row()
        revision = self.row(logged=3,key='revision')
        revision['predictions'][0]['price'] = 500
        rows = [revision, first]
        backup = copy.deepcopy(rows)
        a = self.score(rows)
        self.assertEqual(a['summary']['scored'], 1)
        self.assertEqual(a['results'][0]['snapshotId'], 'first')
        self.assertEqual(a, self.score(list(reversed(rows))))
        self.assertEqual(rows, backup)

    def test_past_turn_same_day_call_and_observed_future_bar_do_not_earn_hits(self):
        self.assertEqual(self.score([self.row(10,8)])['summary']['hits'], 0)
        self.assertEqual(self.score([self.row(8,8)])['excludedCount'], 1)
        row = self.row()
        row['lastBar'] = self.days[8]
        self.assertEqual(self.score([row])['excludedCount'], 1)

    def test_wrong_direction_and_no_turn_are_false_alarms(self):
        self.assertEqual(self.score([self.row(kind='low')])['summary']['falseAlarms'], 1)
        self.data['TEST']['chart']['closes'] = list(range(100,125))
        self.assertEqual(self.score([self.row()])['summary']['falseAlarms'], 1)

    def test_missed_turns_require_mature_coverage_and_matching_call(self):
        result = self.score([self.row(16)])
        self.assertEqual(result['coverage']['turns'], 1)
        self.assertEqual(result['coverage']['missedTurns'], 1)
        self.assertEqual(self.score([self.row()])['coverage']['missedTurns'], 0)
        self.data['TEST']['chart'] = {'dates':self.days[:14], 'closes':self.closes[:14]}
        self.assertEqual(self.score([self.row(16)])['coverage']['turns'], 0)

    def test_non_session_target_is_not_silently_moved(self):
        row = self.row()
        row['predictions'][0]['isoDate'] = '2026-09-12'
        result = self.score([row])
        self.assertEqual(result['excludedCount'], 1)
        self.assertEqual(result['summary']['scored'], 0)

    def test_ties_are_not_unique_turns(self):
        self.assertEqual(confirmed_turns(self.days[:5], [1,2,3,3,2]), [])

    def test_future_call_is_pending_and_absent_history_excluded(self):
        self.data['TEST']['chart'] = {'dates':self.days[:10], 'closes':self.closes[:10]}
        self.assertEqual(self.score([self.row(20)])['pending'], 1)
        self.assertEqual(self.score([self.row(2,0)])['excludedCount'], 1)

    def test_forward_and_audit_are_separate(self):
        rows = [self.row(), self.row(22,17,key='forward')]
        result = self.score(rows)
        self.assertEqual(result['historicalAudit']['scored'], 1)
        # Last four available sessions are unripe, even in the forward cohort.
        self.assertEqual(result['forward']['scored'], 0)
        rows[1]['predictions'][0]['isoDate'] = self.days[19]
        result = self.score(rows)
        self.assertEqual(result['forward']['scored'], 1)
        self.assertEqual(result['forward']['falseAlarms'], 1)

    def test_eastern_timestamp_boundary_and_naive_rejection(self):
        self.assertEqual(eastern_day('2026-09-24T01:00:00+00:00'), '2026-09-23')
        with self.assertRaises(ValueError): eastern_day('2026-09-24T01:00:00')

    def test_method_groups_overlap_and_do_not_change_totals(self):
        result = self.score([self.row()])
        self.assertEqual(result['methodTags']['Gann']['hits'], 1)
        self.assertEqual(result['methodTags']['Astro / vibration']['hits'], 1)
        self.assertEqual(result['summary']['hits'], 1)

    def forward_fixture(self):
        # 30 sessions through 2026-10-12; one strict closing high at index 20
        # (2026-09-29), after the forward cohort starts on 2026-09-24 (index 17).
        day = date(2026, 9, 1)
        self.days = []
        while len(self.days) < 30:
            if day.weekday() < 5:
                self.days.append(day.isoformat())
            day += timedelta(days=1)
        self.closes = [100+i if i <= 20 else 140-i for i in range(30)]
        self.data['TEST']['chart'] = {'dates': self.days, 'closes': self.closes}

    def test_forward_call_is_not_blocked_by_historical_claim(self):
        self.forward_fixture()
        historical = self.row(20, 16, key='historical')
        forward = self.row(21, 17, key='forward')
        result = self.score([historical, forward])
        self.assertEqual(result['historicalAudit']['hits'], 1)
        self.assertEqual(result['forward']['hits'], 1)
        self.assertEqual(result['forward']['falseAlarms'], 0)
        # The combined figure still lets one turn credit only one call.
        self.assertEqual(result['summary']['hits'], 1)
        self.assertEqual(result['summary']['falseAlarms'], 1)
        by_id = {r['snapshotId']: r for r in result['results']}
        self.assertEqual(by_id['forward']['status'], 'hit')
        self.assertEqual(by_id['forward']['errorSessions'], 1)

    def test_cohort_coverage_is_partitioned_at_forward_start(self):
        self.forward_fixture()
        # Historical call far from the turn; forward call catches it.
        result = self.score([self.row(8, 1, key='historical'), self.row(21, 17, key='forward')])
        hist, fwd = result['historicalCoverage'], result['forwardCoverage']
        self.assertEqual(hist['through'], self.days[16])
        self.assertEqual(hist['turns'], 0)
        self.assertEqual((fwd['fromExclusive'], fwd['turns'], fwd['missedTurns']), (self.days[17], 1, 0))
        # Without a forward call the forward-period turn is not charged to
        # the historical audit, and forward coverage has not started.
        result = self.score([self.row(8, 1, key='historical')])
        self.assertEqual(result['historicalCoverage']['turns'], 0)
        self.assertEqual(result['forwardCoverage']['turns'], 0)
        self.assertEqual(result['coverage']['missedTurns'], 1)

    def test_forward_miss_is_counted_in_forward_coverage(self):
        self.forward_fixture()
        result = self.score([self.row(8, 1, key='historical'), self.row(24, 17, kind='low', key='forward')])
        self.assertEqual(result['forwardCoverage']['turns'], 1)
        self.assertEqual(result['forwardCoverage']['missedTurns'], 1)
        self.assertEqual(result['forward']['falseAlarms'], 1)

    def test_blind_baseline_is_reported_and_repeatable(self):
        result = self.score([self.row(8)])
        self.assertIn('chanceHitPct', result)
        self.assertEqual(result['chanceHitPct'], self.score([self.row(8)])['chanceHitPct'])
        self.assertEqual(result['useVerdict']['status'], 'unproven')

    def test_blind_baseline_uses_same_matching(self):
        turns = [{'date': self.days[8], 'type': 'high', 'index': 8, 'confirmedDate': self.days[10]}]
        base = {'type': 'high'}
        # A lone call anywhere in a 5-session span around the turn always hits.
        self.assertEqual(chance_rate([(base, 6, self.days[1])], turns), 100.0)
        # Two calls compete for one turn, so blind calls can score at most 50%.
        calls = [(base, 6, self.days[1]), (base, 10, self.days[1])]
        self.assertLessEqual(chance_rate(calls, turns), 50.0)
        self.assertIsNone(chance_rate([], turns))

    def test_verdict_needs_samples_and_must_clear_chance(self):
        few = {'scored': MIN_SCORED - 1, 'hits': MIN_SCORED - 1}
        self.assertEqual(use_verdict(few, 10.0)['status'], 'unproven')
        strong = {'scored': 40, 'hits': 30}
        self.assertEqual(use_verdict(strong, 33.0)['status'], 'beatsChance')
        at_chance = {'scored': 40, 'hits': 14}
        self.assertEqual(use_verdict(at_chance, 33.0)['status'], 'notAboveChance')
        self.assertEqual(use_verdict(strong, None)['status'], 'unproven')


if __name__ == '__main__':
    unittest.main()
