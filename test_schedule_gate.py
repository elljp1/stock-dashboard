import unittest
from datetime import datetime, timedelta
from schedule_gate import due_slot, decision, EASTERN


class ScheduleTests(unittest.TestCase):
    def test_every_requested_slot_in_summer_and_winter(self):
        expected = [360,420,480,540,555,560,565,570,575,585]
        expected += list(range(600,1021,30)) + [1080]
        for day in ("2026-09-09", "2026-12-09"):
            start = datetime.fromisoformat(day).replace(tzinfo=EASTERN)
            previous, observed = None, []
            for m in range(1440):
                slot = due_slot(start + timedelta(minutes=m))
                if slot and slot != previous:
                    observed.append(m)
                previous = slot
            self.assertEqual(observed, expected)

    def test_weekends_and_dst(self):
        for stamp in ("2026-03-08T18:00:00-04:00", "2026-11-01T18:00:00-05:00"):
            now = datetime.fromisoformat(stamp)
            self.assertEqual(due_slot(now), now)
            self.assertIsNone(due_slot(now.replace(hour=9)))

    def test_no_grace_delay_and_no_duplicate_current_slot(self):
        now = datetime.fromisoformat("2026-09-09T09:20:00-04:00")
        self.assertTrue(decision(now, "2026-09-09T09:15:30-04:00")[0])
        self.assertFalse(decision(now, now.isoformat())[0])
        self.assertFalse(decision(now + timedelta(minutes=4), now.isoformat())[0])

    def test_delayed_event_catches_latest_slot(self):
        now = datetime.fromisoformat("2026-09-09T14:42:00-04:00")
        self.assertEqual(due_slot(now).strftime("%H:%M"), "14:30")
        self.assertTrue(decision(now, "2026-09-09T13:00:00-04:00")[0])

    def test_unavailable_invalid_and_future_publication_recovers(self):
        now = datetime.fromisoformat("2026-09-09T09:20:00-04:00")
        for value in (None, "broken", "2026-09-09T09:20:00", "2026-09-10T09:20:00-04:00"):
            self.assertTrue(decision(now, value)[0])

    def test_manual_refresh_and_evening_cutoff(self):
        now = datetime.fromisoformat("2026-09-09T23:20:00-04:00")
        self.assertTrue(decision(now, event="workflow_dispatch")[0])
        self.assertFalse(decision(now)[0])
        self.assertTrue(decision(now.replace(hour=18), "2026-09-09T17:00:00-04:00")[0])


if __name__ == "__main__":
    unittest.main()
