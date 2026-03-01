import pytest
from datetime import datetime
import pytz

from src.ramadan_features import RamadanBot

PKT = pytz.timezone("Asia/Karachi")


# ----------------------------
# Fake Providers
# ----------------------------


class FakeRandom:
    def randint(self, a, b):
        return a

    def choice(self, items):
        return items[0]


class FakeSession:
    """Prevents real HTTP calls"""

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        pass


# ----------------------------
# Test Helpers
# ----------------------------


def fake_now():
    """Simulate current time = 5:00 PM"""
    return PKT.localize(datetime(2026, 3, 1, 17, 0, 0))


@pytest.mark.asyncio
async def test_iftar_countdown_one_hour_remaining():
    """
    If Maghrib is at 18:00 and now is 17:00,
    countdown should be ~1 hour.
    """

    bot = RamadanBot(
        bot=None,
        http_session_factory=lambda: FakeSession(),
        now_provider=fake_now,
        random_provider=FakeRandom(),
    )

    # Mock prayer times cache directly
    bot.prayer_times_cache["Islamabad_01-03-2026"] = {
        "Fajr": "05:00",
        "Maghrib": "18:00",
    }

    countdown = await bot.get_iftar_countdown()

    assert countdown is not None
    assert countdown["hours"] == 1
    assert countdown["minutes"] == 0
