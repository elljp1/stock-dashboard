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
        report=reliability.review(self.data,'2026-09-10T15:00:00+00:00')
        self.assertEqual(report['results'][0]['predictedPrice'],110)
    def test_invalid_price_rejected(self):
        self.data['TEST']['price']=float('nan')
        with self.assertRaises(AssertionError): reliability.validate(self.data)

if __name__=='__main__': unittest.main()
