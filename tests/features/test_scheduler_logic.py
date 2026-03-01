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


# -------------------------
# Fake Times
# -------------------------


def sehri_time():
    # 04:45 when Fajr = 05:00 (15 min before)
    return PKT.localize(datetime(2026, 3, 1, 4, 45))


def iftar_time():
    return PKT.localize(datetime(2026, 3, 1, 18, 0))


def random_time():
    # 10:00 AM - not a special time
    return PKT.localize(datetime(2026, 3, 1, 10, 0))


@pytest.mark.asyncio
async def test_sehri_reminder_trigger():
    """Test that Sehri reminder triggers 15 minutes before Fajr"""
    bot = RamadanBot(
        bot=None,
        http_session_factory=lambda: FakeSession(),
        now_provider=sehri_time,
        random_provider=FakeRandom(),
    )

    bot.prayer_times_cache["Islamabad_01-03-2026"] = {
        "Fajr": "05:00",
        "Maghrib": "18:00",
    }

    event = await bot.process_prayer_time_check(None)

    assert event == "SEHRI_REMINDER"


@pytest.mark.asyncio
async def test_iftar_trigger():
    """Test that Iftar reminder triggers at Maghrib time"""
    bot = RamadanBot(
        bot=None,
        http_session_factory=lambda: FakeSession(),
        now_provider=iftar_time,
        random_provider=FakeRandom(),
    )

    bot.prayer_times_cache["Islamabad_01-03-2026"] = {
        "Fajr": "05:00",
        "Maghrib": "18:00",
    }

    event = await bot.process_prayer_time_check(None)

    assert event == "IFTAR_TIME"


@pytest.mark.asyncio
async def test_no_event_at_random_time():
    """Test that no event triggers at random times"""
    bot = RamadanBot(
        bot=None,
        http_session_factory=lambda: FakeSession(),
        now_provider=random_time,
        random_provider=FakeRandom(),
    )

    bot.prayer_times_cache["Islamabad_01-03-2026"] = {
        "Fajr": "05:00",
        "Maghrib": "18:00",
    }

    event = await bot.process_prayer_time_check(None)

    assert event is None
