import unittest
from datetime import datetime
from unittest.mock import patch
from zoneinfo import ZoneInfo

from config.settings import settings
from main import is_scheduled_send_allowed


class ScheduledSendWindowTests(unittest.TestCase):
    def setUp(self):
        self.settings_patches = [
            patch.object(settings, "schedule_time", "08:00"),
            patch.object(settings, "schedule_timezone", "Asia/Shanghai"),
            patch.object(settings, "send_window_minutes", 60),
        ]
        for settings_patch in self.settings_patches:
            settings_patch.start()

    def tearDown(self):
        for settings_patch in reversed(self.settings_patches):
            settings_patch.stop()

    def test_allows_beijing_morning_window(self):
        now = datetime(2026, 6, 13, 8, 30, tzinfo=ZoneInfo("Asia/Shanghai"))
        self.assertTrue(is_scheduled_send_allowed(now))

    def test_rejects_delayed_evening_run(self):
        now = datetime(2026, 6, 13, 20, 40, tzinfo=ZoneInfo("Asia/Shanghai"))
        self.assertFalse(is_scheduled_send_allowed(now))

    def test_rejects_just_after_window(self):
        now = datetime(2026, 6, 13, 9, 0, tzinfo=ZoneInfo("Asia/Shanghai"))
        self.assertFalse(is_scheduled_send_allowed(now))


if __name__ == "__main__":
    unittest.main()
