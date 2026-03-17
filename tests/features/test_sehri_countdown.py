"""
Unit tests for the Sehri countdown calculation in RamadanBot.
"""

import pytest
from datetime import datetime
import pytz

from src.ramadan_features import RamadanBot

PKT = pytz.timezone("Asia/Karachi")


class FakeSession:
    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        pass


class FakeRandom:
    def randint(self, a, b):
        return a

    def choice(self, items):
        return items[0]


def fake_now_before_fajr():
    """Simulate 03:00 AM — 2 hours before Fajr at 05:00."""
    return PKT.localize(datetime(2026, 3, 1, 3, 0, 0))


def fake_now_after_fajr():
    """Simulate 06:00 AM — after Fajr at 05:00 (should show tomorrow)."""
    return PKT.localize(datetime(2026, 3, 1, 6, 0, 0))


@pytest.mark.asyncio
@pytest.mark.unit
async def test_sehri_countdown_two_hours_remaining():
    """When current time is 03:00 and Fajr is 05:00, countdown should be 2h 0m."""
    bot = RamadanBot(
        bot=None,
        http_session_factory=lambda: FakeSession(),
        now_provider=fake_now_before_fajr,
        random_provider=FakeRandom(),
    )

    bot.prayer_times_cache["Islamabad_01-03-2026"] = {
        "Fajr": "05:00",
        "Maghrib": "18:00",
    }

    countdown = await bot.get_sehri_countdown()

    assert countdown is not None
    assert countdown["hours"] == 2
    assert countdown["minutes"] == 0


@pytest.mark.asyncio
@pytest.mark.unit
async def test_sehri_countdown_after_fajr_shows_next_day():
    """When current time is past Fajr, countdown should wrap to next day."""
    bot = RamadanBot(
        bot=None,
        http_session_factory=lambda: FakeSession(),
        now_provider=fake_now_after_fajr,
        random_provider=FakeRandom(),
    )

    bot.prayer_times_cache["Islamabad_01-03-2026"] = {
        "Fajr": "05:00",
        "Maghrib": "18:00",
    }

    countdown = await bot.get_sehri_countdown()

    assert countdown is not None
    # Should be ~23 hours until next day's Fajr
    assert countdown["hours"] == 23
    assert countdown["minutes"] == 0
