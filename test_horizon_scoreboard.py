import unittest

import horizon_scoreboard as hs


def ext(high, low, hi_t='09:30', lo_t='15:30', close=None):
    return [high, low, close if close is not None else (high + low) / 2, hi_t, lo_t]


class HorizonScoreboardTests(unittest.TestCase):
    def setUp(self):
        # Mon 9/21 - Fri 9/25 and Mon 9/28 (so the week of 9/21 is complete).
        self.days = {'2026-09-18': ext(100, 90),
                     '2026-09-21': ext(101, 95, '10:00', '15:00'),
                     '2026-09-22': ext(104, 96, '13:00', '09:30'),
                     '2026-09-23': ext(102, 93, '11:00', '14:00'),
                     '2026-09-24': ext(103, 97),
                     '2026-09-25': ext(100, 94),
                     '2026-09-28': ext(99, 92)}

    def call(self, price, when='Tue 09/22', time='Jupiter 12:30-1:30 PM'):
        return {'price': price, 'date': when, 'time': time, 'src': 'chain'}

    def entry(self, logged, session, **h):
        return {'ticker': 'T', 'logged': logged, 'session': session, 'h': h}

    def test_parsers(self):
        self.assertEqual(hs.clock_minutes('Jupiter 12:30-1:30 PM'), 13 * 60)
        self.assertEqual(hs.clock_minutes('Mercury hour 10:40-11:50 AM ET'), 11 * 60 + 15)
        self.assertEqual(hs.clock_minutes('at 9:45 AM ET'), 9 * 60 + 45)
        self.assertEqual(hs.clock_minutes('Saturn 11:47-12:48 PM'), 12 * 60 + 17)
        self.assertEqual(hs.called_day('Mon 08-31 (statistical est.)', '2026-08-05'), '2026-08-31')
        self.assertIsNone(hs.called_day('May 2027', '2026-08-05'))

    def test_first_call_counts_and_already_set_is_ignored(self):
        entries = [
            self.entry('2026-09-20', '2026-09-21', weekly={
                'high': {'price': 104, 'date': 'already set Mon 09/21', 'time': 'at 9:45 AM', 'src': 'actual'}}),
            self.entry('2026-09-20', '2026-09-21', weekly={'high': self.call(105)}),
            self.entry('2026-09-21', '2026-09-22', weekly={'high': self.call(200, 'Fri 09/25')}),
        ]
        rows = [r for r in hs.grade(entries, {'T': self.days}) if r['horizon'] == 'weekly']
        self.assertEqual(len(rows), 1)
        r = rows[0]
        self.assertEqual((r['predPrice'], r['actualPrice'], r['actualDay']), (105, 104, '2026-09-22'))
        self.assertTrue(r['dayHit'])
        self.assertEqual(r['timeErrMin'], 0)          # 1:00 PM called, 13:00 bar
        self.assertEqual(r['naiveErrPct'], round(100 * (100 - 104) / 104, 2))

    def test_time_only_graded_on_the_right_day_and_open_baseline(self):
        entries = [self.entry('2026-09-20', '2026-09-21', weekly={'low': self.call(92, 'Mon 09/21')})]
        r = [r for r in hs.grade(entries, {'T': self.days}) if r['horizon'] == 'weekly'][0]
        self.assertFalse(r['dayHit'])                  # low came Wed 9/23
        self.assertNotIn('timeErrMin', r)
        daily = [self.entry('2026-09-21', '2026-09-22', daily={'low': self.call(95, time='at 10:00 AM')})]
        d = hs.grade(daily, {'T': self.days})[0]
        self.assertEqual(d['timeErrMin'], 30)          # low bar at 9:30
        self.assertTrue(d['openWithin'])

    def test_incomplete_period_is_not_graded(self):
        entries = [self.entry('2026-09-27', '2026-09-28', daily={'high': self.call(99)})]
        self.assertEqual(hs.grade(entries, {'T': self.days}), [])

    def test_summary_and_table(self):
        entries = [self.entry('2026-09-20', '2026-09-21', weekly={'high': self.call(105)}),
                   self.entry('2026-09-21', '2026-09-22', daily={'high': self.call(103, time='at 1:15 PM')})]
        board = hs.scoreboard(entries, {'T': self.days})
        wk = board['table']['ALL']['weekly']['high']
        self.assertEqual((wk['n'], wk['dayHitPct'], wk['randomDayPct']), (1, 100.0, 20.0))
        self.assertEqual(board['table']['T']['monthly']['low'], {'n': 0})
        self.assertEqual(hs.random_time_chance(hs.OPEN_MIN), 60 / 390)


if __name__ == '__main__':
    unittest.main()
