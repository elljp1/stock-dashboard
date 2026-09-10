import copy
import json
import os
from pathlib import Path
import tempfile
import unittest
import reliability

class ReliabilityTests(unittest.TestCase):
    def setUp(self):
        self.previous=os.getcwd()
        self.tmp=tempfile.TemporaryDirectory()
        os.chdir(self.tmp.name)
        Path('tickers.txt').write_text('TEST\n')
        self.data={'TEST': {'price':100,'generated':'2026-09-07 11:00 AM ET',
            'chart':{'dates':['2026-09-04'],'closes':[100]},
            'predictions':[{'isoDate':'2026-09-09','price':110,'type':'high'}]}}
    def tearDown(self):
        os.chdir(self.previous)
        self.tmp.cleanup()
    def test_missing_ticker_rejected(self):
        with self.assertRaises(ValueError): reliability.validate({})
    def test_revision_preserves_original_and_retry_dedupes(self):
        reliability.review(self.data,'2026-09-07T15:00:00+00:00')
        original=json.loads(Path('forecast_ledger.json').read_text())['snapshots'][0]
        self.data['TEST']['predictions'][0]['price']=120
        reliability.review(self.data,'2026-09-07T16:00:00+00:00')
        reliability.review(self.data,'2026-09-07T16:01:00+00:00')
        rows=json.loads(Path('forecast_ledger.json').read_text())['snapshots']
        self.assertEqual(len(rows),2)
        self.assertEqual(rows[0],original)
        self.data['TEST']['chart']={'dates':['2026-09-04','2026-09-09'],'closes':[100,111]}
        self.data['TEST']['generated']='2026-09-10 11:00 AM ET'
        report=reliability.review(self.data,'2026-09-10T15:00:00+00:00')
        self.assertEqual(report['results'][0]['predictedPrice'],110)
    def test_invalid_price_rejected(self):
        self.data['TEST']['price']=float('nan')
        with self.assertRaises(AssertionError): reliability.validate(self.data)

    def test_partial_target_day_not_scored_until_next_eastern_date(self):
        reliability.review(self.data, '2026-09-07T15:00:00+00:00')
        original=json.loads(Path('forecast_ledger.json').read_text())['snapshots'][0]
        self.data['TEST']['chart']={'dates':['2026-09-04','2026-09-09'], 'closes':[100,108]}
        for now in ['2026-09-09T19:58:27+00:00', '2026-09-09T22:00:00+00:00',
                    '2026-09-10T01:00:00+00:00']:
            self.data['TEST']['generated']='2026-09-09 03:58 PM ET'
            self.assertEqual(reliability.review(self.data,now)['scoredOriginals'],0)
        self.assertEqual(reliability.review(self.data,'2026-09-10T15:00:00+00:00')['scoredOriginals'],0)
        self.data['TEST']['chart']['closes'][-1]=111
        self.data['TEST']['generated']='2026-09-10 12:00 AM ET'
        report=reliability.review(self.data,'2026-09-10T04:00:00+00:00')
        self.assertEqual(report['scoredOriginals'],1)
        self.assertEqual(report['results'][0]['actualClose'],111)
        self.assertEqual(json.loads(Path('forecast_ledger.json').read_text())['snapshots'][0],original)

    def test_prospective_log_day_uses_eastern_not_utc(self):
        # 9 PM Eastern Sep 7: Sep 8 is still a future-day forecast.
        self.data['TEST']['predictions'][0]['isoDate']='2026-09-08'
        reliability.review(self.data,'2026-09-08T01:00:00+00:00')
        self.data['TEST']['chart']={'dates':['2026-09-08'],'closes':[109]}
        self.data['TEST']['generated']='2026-09-09 11:00 AM ET'
        self.assertEqual(reliability.review(self.data,'2026-09-09T15:00:00+00:00')['scoredOriginals'],1)

    def test_delayed_first_bar_must_also_be_complete(self):
        reliability.review(self.data,'2026-09-07T15:00:00+00:00')
        self.data['TEST']['chart']={'dates':['2026-09-10'],'closes':[109]}
        self.data['TEST']['generated']='2026-09-10 03:00 PM ET'
        self.assertEqual(reliability.review(self.data,'2026-09-10T19:00:00+00:00')['scoredOriginals'],0)
        self.data['TEST']['generated']='2026-09-11 11:00 AM ET'
        self.assertEqual(reliability.review(self.data,'2026-09-11T15:00:00+00:00')['scoredOriginals'],1)

if __name__=='__main__': unittest.main()
