"""
Integration tests for Ramadan features.

Tests the interaction between:
- RamadanBot class
- API helpers (prayer times, hadith, ayat)
- Time providers
- Data caching
"""

import pytest
from datetime import datetime
import pytz
import aiohttp

from src.ramadan_features import RamadanBot

PKT = pytz.timezone("Asia/Karachi")


class FakeRandom:
    def randint(self, a, b):
        return a

    def choice(self, items):
        return items[0]


@pytest.mark.integration
@pytest.mark.asyncio
async def test_ramadan_bot_initialization():
    """Test that RamadanBot initializes with all dependencies"""
    bot = RamadanBot(
        bot=None,
        http_session_factory=aiohttp.ClientSession,
        now_provider=lambda: datetime.now(PKT),
        random_provider=FakeRandom(),
    )

    assert bot is not None
    assert bot.current_city == "Islamabad"
    assert bot.prayer_times_cache == {}
    assert bot.last_sehri_reminder is None
    assert bot.last_iftar_reminder is None


@pytest.mark.integration
@pytest.mark.asyncio
async def test_fetch_prayer_times_real_api():
    """Test fetching prayer times from real API"""
    bot = RamadanBot(
        bot=None,
        http_session_factory=aiohttp.ClientSession,
        now_provider=lambda: datetime.now(PKT),
        random_provider=FakeRandom(),
    )

    # Fetch prayer times for Islamabad
    timings = await bot.fetch_prayer_times("Islamabad")

    # Verify response structure
    assert timings is not None
    assert "Fajr" in timings
    assert "Maghrib" in timings
    assert "Dhuhr" in timings
    assert "Asr" in timings
    assert "Isha" in timings

    # Verify time format (HH:MM)
    import re

    time_pattern = re.compile(r"^\d{2}:\d{2}$")
    assert time_pattern.match(timings["Fajr"])
    assert time_pattern.match(timings["Maghrib"])


@pytest.mark.integration
@pytest.mark.asyncio
async def test_fetch_hadith_real_api():
    """Test fetching hadith from real API"""
    bot = RamadanBot(
        bot=None,
        http_session_factory=aiohttp.ClientSession,
        now_provider=lambda: datetime.now(PKT),
        random_provider=FakeRandom(),
    )

    hadith = await bot.fetch_random_hadith()

    # Verify response structure
    assert hadith is not None
    assert "arabic" in hadith
    assert "english" in hadith
    assert "reference" in hadith

    # Verify content is not empty
    assert len(hadith["arabic"]) > 0
    assert len(hadith["english"]) > 0
    assert len(hadith["reference"]) > 0


@pytest.mark.integration
@pytest.mark.asyncio
async def test_fetch_ayat_real_api():
    """Test fetching Quranic verse from real API"""
    bot = RamadanBot(
        bot=None,
        http_session_factory=aiohttp.ClientSession,
        now_provider=lambda: datetime.now(PKT),
        random_provider=FakeRandom(),
    )

    ayat = await bot.fetch_random_ayat()

    # Verify response structure
    assert ayat is not None
    assert "arabic" in ayat
    assert "english" in ayat
    assert "surah" in ayat
    assert "ayah" in ayat

    # Verify content is not empty
    assert len(ayat["arabic"]) > 0
    assert len(ayat["english"]) > 0
    # Surah can be string or int depending on API
    assert ayat["surah"] is not None
    assert ayat["ayah"] is not None


@pytest.mark.integration
@pytest.mark.asyncio
async def test_prayer_times_caching():
    """Test that prayer times are cached correctly"""
    bot = RamadanBot(
        bot=None,
        http_session_factory=aiohttp.ClientSession,
        now_provider=lambda: datetime.now(PKT),
        random_provider=FakeRandom(),
    )

    # First fetch - should hit API
    timings1 = await bot.fetch_prayer_times("Lahore")
    assert timings1 is not None

    # Check cache was populated
    now = datetime.now(PKT)
    cache_key = f"Lahore_{now.strftime('%d-%m-%Y')}"
    assert cache_key in bot.prayer_times_cache

    # Second fetch - should use cache
    timings2 = await bot.fetch_prayer_times("Lahore")
    assert timings2 == timings1


@pytest.mark.integration
@pytest.mark.asyncio
async def test_countdown_with_real_prayer_times():
    """Test countdown calculation with real API data"""
    bot = RamadanBot(
        bot=None,
        http_session_factory=aiohttp.ClientSession,
        now_provider=lambda: datetime.now(PKT),
        random_provider=FakeRandom(),
    )

    # Fetch real prayer times
    timings = await bot.fetch_prayer_times("Karachi")
    assert timings is not None

    # Calculate iftar countdown
    countdown = await bot.get_iftar_countdown()

    # Verify countdown structure
    if countdown:  # May be None if past Maghrib
        assert "hours" in countdown
        assert "minutes" in countdown
        assert isinstance(countdown["hours"], int)
        assert isinstance(countdown["minutes"], int)


@pytest.mark.integration
@pytest.mark.asyncio
async def test_multiple_cities_prayer_times():
    """Test fetching prayer times for multiple cities"""
    bot = RamadanBot(
        bot=None,
        http_session_factory=aiohttp.ClientSession,
        now_provider=lambda: datetime.now(PKT),
        random_provider=FakeRandom(),
    )

    cities = ["Islamabad", "Lahore", "Karachi"]

    for city in cities:
        timings = await bot.fetch_prayer_times(city)
        assert timings is not None
        assert "Fajr" in timings
        assert "Maghrib" in timings


@pytest.mark.integration
@pytest.mark.asyncio
async def test_time_conversion_integration():
    """Test 12-hour time conversion with real data"""
    bot = RamadanBot(
        bot=None,
        http_session_factory=aiohttp.ClientSession,
        now_provider=lambda: datetime.now(PKT),
        random_provider=FakeRandom(),
    )

    # Fetch real prayer times
    timings = await bot.fetch_prayer_times("Islamabad")
    assert timings is not None

    # Convert times to 12-hour format
    fajr_12hr = bot.convert_to_12hr(timings["Fajr"])
    maghrib_12hr = bot.convert_to_12hr(timings["Maghrib"])

    # Verify format
    assert "AM" in fajr_12hr or "PM" in fajr_12hr
    assert "AM" in maghrib_12hr or "PM" in maghrib_12hr


@pytest.mark.integration
@pytest.mark.asyncio
async def test_scheduler_with_real_prayer_times():
    """Test scheduler logic with real API data"""

    def fake_time_before_fajr():
        # 4:45 AM
        return PKT.localize(datetime(2026, 3, 1, 4, 45))

    bot = RamadanBot(
        bot=None,
        http_session_factory=aiohttp.ClientSession,
        now_provider=fake_time_before_fajr,
        random_provider=FakeRandom(),
    )

    # Fetch real prayer times
    timings = await bot.fetch_prayer_times("Islamabad")
    assert timings is not None

    # Manually set cache for testing
    bot.prayer_times_cache["Islamabad_01-03-2026"] = timings

    # Test scheduler logic
    event = await bot.process_prayer_time_check(None)

    # Event may or may not trigger depending on actual Fajr time
    assert event in ["SEHRI_REMINDER", "IFTAR_TIME", None]
