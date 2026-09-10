from datetime import datetime
from unittest import TestCase, main
from unittest.mock import Mock
import pandas as pd
from data_freshness import reconcile_daily, ET


def bars(*dates):
    return pd.DataFrame({'Close': range(100, 100 + len(dates))},
                        index=pd.DatetimeIndex(dates, tz=ET, name='Datetime'))


class DailyFreshnessTests(TestCase):
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
