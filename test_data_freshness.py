from datetime import datetime
from unittest import TestCase, main
from unittest.mock import Mock
import pandas as pd
from data_freshness import reconcile_daily, recover_session, cached_session, remember_completed, ET
import copy


def bars(*dates):
    return pd.DataFrame({'Close': range(100, 100 + len(dates))},
                        index=pd.DatetimeIndex(dates, tz=ET, name='Datetime'))


class DailyFreshnessTests(TestCase):
    def cache(self):
        return {'version': 1, 'tickers': {'TSLA': {'2026-09-22': {
            'Open':100.,'High':104.,'Low':98.,'Close':103.,'Volume':260.,
            'source':'recovered_15m_complete_session','storedAt':'2026-09-23T08:00:00-04:00'}}}}

    def test_exact_cached_close_survives_disappearing_closing_observation(self):
        intraday = self.complete_session().iloc[:-1]
        daily = bars('2026-09-21 09:30')
        result = reconcile_daily(daily, bars('2026-09-22 15:30'), 'TSLA',
                    datetime(2026,9,23,10,tzinfo=ET), lambda: daily, intraday, self.cache())
        self.assertEqual(result.Close.iloc[-1],103.)
        self.assertNotEqual(result.Close.iloc[-1],intraday.Close.iloc[-1])
        self.assertEqual(result.Source.iloc[-1],'cached_validated_completed_session')

    def test_cache_cannot_substitute_wrong_date_symbol_or_unknown_source(self):
        cache = self.cache(); now=datetime(2026,9,23,10,tzinfo=ET)
        self.assertIsNone(cached_session(cache,'SPY',now.date(),now))
        self.assertIsNone(cached_session(cache,'TSLA',now.date(),now))
        cache['tickers']['TSLA']['2026-09-22']['source']='unverified'
        self.assertIsNone(cached_session(cache,'TSLA',datetime(2026,9,22).date(),now))

    def test_cache_rejects_bad_ohlcv_and_unsettled_or_future_timestamps(self):
        for k,v in [('Close',float('nan')),('High',80),('Volume',-1),
                    ('storedAt','2026-09-22T15:59:00-04:00'),
                    ('storedAt','2026-09-24T08:00:00-04:00'),
                    ('storedAt','2026-09-23T08:00:00')]:
            c=self.cache();c['tickers']['TSLA']['2026-09-22'][k]=v
            self.assertIsNone(cached_session(c,'TSLA',datetime(2026,9,22).date(),
                                             datetime(2026,9,23,10,tzinfo=ET)))

    def test_fresh_daily_data_takes_precedence_over_cache(self):
        daily=bars('2026-09-22 09:30')
        result=reconcile_daily(daily,bars('2026-09-22 15:30'),'TSLA',
                datetime(2026,9,23,10,tzinfo=ET),Mock(),cache=self.cache())
        self.assertIs(result,daily)

    def test_cache_records_completed_sessions_only_and_retains_source(self):
        c={'version':1,'tickers':{}};now=datetime(2026,9,23,10,tzinfo=ET)
        daily=recover_session(self.complete_session(),datetime(2026,9,22).date(),now)
        current=daily.copy();current.index=pd.DatetimeIndex(['2026-09-23 09:30'],tz=ET)
        remember_completed(c,'TSLA',pd.concat([daily,current]),now)
        self.assertEqual(list(c['tickers']['TSLA']),['2026-09-22'])
        self.assertEqual(c['tickers']['TSLA']['2026-09-22']['source'],'recovered_15m_complete_session')
        old=copy.deepcopy(c)
        cached=cached_session(c,'TSLA',datetime(2026,9,22).date(),now)
        remember_completed(c,'TSLA',cached,now)
        self.assertEqual(c,old)

    def complete_session(self):
        index = pd.date_range('2026-09-22 09:30', '2026-09-22 16:00', freq='15min', tz=ET)
        frame = pd.DataFrame({'Open': 100., 'High': 104., 'Low': 98.,
                              'Close': 102., 'Volume': 10.}, index=index)
        frame.loc[index[-1], ['Open', 'High', 'Low', 'Close', 'Volume']] = [103., 103., 103., 103., 0.]
        return frame

    def test_complete_intraday_recovery_uses_explicit_close_and_preserves_history(self):
        daily = bars('2000-01-03 09:30', '2026-09-21 09:30')
        before = daily.copy(deep=True)
        frame = self.complete_session()
        result = reconcile_daily(daily, bars('2026-09-22 15:30'), 'TSLA',
                                 datetime(2026, 9, 23, 8, tzinfo=ET), lambda: daily,
                                 intraday=frame)
        self.assertEqual(result.iloc[-1]['Close'], 103.)
        self.assertEqual(result.iloc[-1]['Open'], 100.)
        self.assertEqual(result.iloc[-1]['High'], 104.)
        self.assertEqual(result.iloc[-1]['Low'], 98.)
        self.assertEqual(result.iloc[-1]['Volume'], 260.)
        self.assertEqual(result.iloc[-1]['Source'], 'recovered_15m_complete_session')
        self.assertEqual(result.iloc[0]['Close'], 100.)
        pd.testing.assert_frame_equal(daily, before)

    def test_recovery_refuses_gaps_duplicates_and_missing_closing_point(self):
        frame = self.complete_session()
        for bad in [frame.iloc[:-1], frame.drop(frame.index[7]),
                    pd.concat([frame, frame.iloc[[5]]]).sort_index(), frame.iloc[:15]]:
            with self.subTest(length=len(bad)):
                self.assertIsNone(recover_session(bad, datetime(2026,9,22).date(),
                                                 datetime(2026,9,23,8,tzinfo=ET)))

    def test_recovery_refuses_invalid_ohlcv(self):
        for column, value in [('Close', float('nan')), ('High', 90), ('Low', 110),
                              ('Open', float('inf')), ('Volume', -1)]:
            bad = self.complete_session()
            bad.loc[bad.index[3], column] = value
            self.assertIsNone(recover_session(bad, datetime(2026,9,22).date(),
                                             datetime(2026,9,23,8,tzinfo=ET)))

    def test_recovery_waits_for_close_and_excludes_extended_hours(self):
        frame = self.complete_session()
        day = datetime(2026,9,22).date()
        self.assertIsNone(recover_session(frame, day, datetime(2026,9,22,16,14,tzinfo=ET)))
        after = frame.iloc[[0]].copy()
        after.index = pd.DatetimeIndex(['2026-09-22 16:15'], tz=ET)
        after['High'] = 1000
        result = recover_session(pd.concat([frame, after]), day,
                                 datetime(2026,9,22,16,15,tzinfo=ET))
        self.assertEqual(result.iloc[0]['High'], 104.)

    def test_real_daily_bar_wins_over_intraday_fallback(self):
        daily = bars('2026-09-22 09:30')
        result = reconcile_daily(daily, bars('2026-09-22 15:30'), 'TSLA',
                                 datetime(2026,9,23,8,tzinfo=ET), Mock(), self.complete_session())
        self.assertIs(result, daily)

    def test_recover_missing_september_9_and_preserve_long_history(self):
        daily = bars('2000-01-03 09:30', '2026-09-08 09:30')
        old = daily.copy(deep=True)
        recent = bars('2026-09-08 09:30', '2026-09-09 09:30')
        fetch = Mock(return_value=recent)
        result = reconcile_daily(daily, bars('2026-09-09 15:30'), 'GOOGL',
                                 datetime(2026, 9, 10, 8, tzinfo=ET), fetch)
        self.assertEqual(len(result), 3)
        self.assertEqual(result.index[-1].date().isoformat(), '2026-09-09')
        self.assertEqual(result.iloc[0]['Close'], 100)
        pd.testing.assert_frame_equal(daily, old)
        fetch.assert_called_once_with()

    def test_stale_recovery_is_rejected(self):
        daily = bars('2026-09-08 09:30')
        with self.assertRaisesRegex(ValueError, 'missing daily bar'):
            reconcile_daily(daily, bars('2026-09-09 15:30'), 'QQQ',
                            datetime(2026, 9, 10, 8, tzinfo=ET), lambda: daily)

    def test_current_session_not_required_before_close(self):
        daily = bars('2026-09-08 09:30')
        fetch = Mock(side_effect=AssertionError('Unexpected recovery'))
        result = reconcile_daily(daily, bars('2026-09-08 15:30','2026-09-09 12:30'),
                                 'TSLA', datetime(2026, 9, 9, 13, tzinfo=ET), fetch)
        self.assertIs(result, daily)

    def test_same_day_required_after_settlement_buffer(self):
        with self.assertRaisesRegex(ValueError, 'missing daily bar'):
            reconcile_daily(bars('2026-09-08 09:30'), bars('2026-09-09 15:30'),
                            'SPY', datetime(2026, 9, 9, 16, 15, tzinfo=ET),
                            lambda: bars('2026-09-08 09:30'))

    def test_holiday_does_not_require_nonexistent_bar(self):
        daily = bars('2026-09-04 09:30')
        result = reconcile_daily(daily, bars('2026-09-04 15:30'), 'SPY',
                                 datetime(2026, 9, 8, 6, tzinfo=ET), Mock())
        self.assertIs(result, daily)

    def test_futures_do_not_use_equity_session_rule(self):
        daily = bars('2026-09-08 00:00')
        self.assertIs(reconcile_daily(daily, bars('2026-09-09 23:00'), 'GC=F',
                      datetime(2026, 9, 10, 8, tzinfo=ET), Mock()), daily)

    def test_same_date_with_different_timestamp_is_not_duplicated(self):
        result = reconcile_daily(bars('2026-09-08 00:00'), bars('2026-09-09 15:30'),
                    'JPM', datetime(2026, 9, 10, 8, tzinfo=ET),
                    lambda: bars('2026-09-08 09:30', '2026-09-09 09:30'))
        self.assertEqual(len(result), 2)


if __name__ == '__main__':
    main()
