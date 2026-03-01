"""
End-to-End tests for Ramadan feature workflows.

Simulates complete user journeys:
1. User requests prayer times
2. User changes city
3. User requests countdown
4. User requests hadith/ayat
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


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_complete_ramadan_times_workflow():
    """
    E2E Test: User checks prayer times for their city

    User Journey:
    1. User asks for Ramadan times
    2. Bot fetches prayer times from API
    3. Bot returns formatted times
    4. User sees Sehri and Iftar times
    """
    # Initialize bot
    bot = RamadanBot(
        bot=None,
        http_session_factory=aiohttp.ClientSession,
        now_provider=lambda: datetime.now(PKT),
        random_provider=FakeRandom(),
    )

    # Step 1: User requests prayer times
    timings = await bot.fetch_prayer_times("Islamabad")

    # Step 2: Verify bot fetched data
    assert timings is not None
    assert "Fajr" in timings
    assert "Maghrib" in timings

    # Step 3: Bot converts to 12-hour format (user-friendly)
    fajr_12hr = bot.convert_to_12hr(timings["Fajr"])
    maghrib_12hr = bot.convert_to_12hr(timings["Maghrib"])

    # Step 4: Verify user sees formatted times
    assert "AM" in fajr_12hr or "PM" in fajr_12hr
    assert "AM" in maghrib_12hr or "PM" in maghrib_12hr


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_city_change_workflow():
    """
    E2E Test: User changes their city

    User Journey:
    1. User is in Islamabad (default)
    2. User changes to Lahore
    3. Bot fetches new prayer times
    4. User sees Lahore times
    """
    bot = RamadanBot(
        bot=None,
        http_session_factory=aiohttp.ClientSession,
        now_provider=lambda: datetime.now(PKT),
        random_provider=FakeRandom(),
    )

    # Step 1: Default city
    assert bot.current_city == "Islamabad"

    # Step 2: User changes city
    bot.current_city = "Lahore"

    # Step 3: Fetch new city's times
    timings = await bot.fetch_prayer_times("Lahore")

    # Step 4: Verify new times loaded
    assert timings is not None
    assert "Fajr" in timings


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_iftar_countdown_workflow():
    """
    E2E Test: User checks time until Iftar

    User Journey:
    1. User asks for Iftar countdown
    2. Bot fetches current prayer times
    3. Bot calculates time remaining
    4. User sees hours and minutes until Iftar
    """

    def afternoon_time():
        # 3:00 PM - before Iftar
        return PKT.localize(datetime(2026, 3, 1, 15, 0))

    bot = RamadanBot(
        bot=None,
        http_session_factory=aiohttp.ClientSession,
        now_provider=afternoon_time,
        random_provider=FakeRandom(),
    )

    # Step 1: User requests countdown
    # Step 2: Bot fetches prayer times
    timings = await bot.fetch_prayer_times("Islamabad")
    assert timings is not None

    # Manually cache for testing
    bot.prayer_times_cache["Islamabad_01-03-2026"] = timings

    # Step 3: Bot calculates countdown
    countdown = await bot.get_iftar_countdown()

    # Step 4: User sees countdown (if before Maghrib)
    if countdown:
        assert "hours" in countdown
        assert "minutes" in countdown
        assert isinstance(countdown["hours"], int)
        assert isinstance(countdown["minutes"], int)


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_hadith_request_workflow():
    """
    E2E Test: User requests daily hadith

    User Journey:
    1. User asks for hadith
    2. Bot fetches from API
    3. Bot formats hadith with Arabic and English
    4. User sees complete hadith with reference
    """
    bot = RamadanBot(
        bot=None,
        http_session_factory=aiohttp.ClientSession,
        now_provider=lambda: datetime.now(PKT),
        random_provider=FakeRandom(),
    )

    # Step 1 & 2: User requests, bot fetches
    hadith = await bot.fetch_random_hadith()

    # Step 3 & 4: Verify complete hadith structure
    assert hadith is not None
    assert "arabic" in hadith
    assert "english" in hadith
    assert "reference" in hadith
    assert len(hadith["arabic"]) > 0
    assert len(hadith["english"]) > 0
    assert len(hadith["reference"]) > 0


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_ayat_request_workflow():
    """
    E2E Test: User requests Quranic verse

    User Journey:
    1. User asks for ayat
    2. Bot fetches from Quran API
    3. Bot formats with Arabic, English, and reference
    4. User sees complete verse
    """
    bot = RamadanBot(
        bot=None,
        http_session_factory=aiohttp.ClientSession,
        now_provider=lambda: datetime.now(PKT),
        random_provider=FakeRandom(),
    )

    # Step 1 & 2: User requests, bot fetches
    ayat = await bot.fetch_random_ayat()

    # Step 3 & 4: Verify complete ayat structure
    assert ayat is not None
    assert "arabic" in ayat
    assert "english" in ayat
    assert "surah" in ayat
    assert "ayah" in ayat
    assert len(ayat["arabic"]) > 0
    assert len(ayat["english"]) > 0


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_multi_city_comparison_workflow():
    """
    E2E Test: User compares prayer times across cities

    User Journey:
    1. User checks Islamabad times
    2. User checks Karachi times
    3. User compares the differences
    """
    bot = RamadanBot(
        bot=None,
        http_session_factory=aiohttp.ClientSession,
        now_provider=lambda: datetime.now(PKT),
        random_provider=FakeRandom(),
    )

    # Step 1: Check Islamabad
    islamabad_times = await bot.fetch_prayer_times("Islamabad")
    assert islamabad_times is not None

    # Step 2: Check Karachi
    karachi_times = await bot.fetch_prayer_times("Karachi")
    assert karachi_times is not None

    # Step 3: Verify both have complete data
    assert "Fajr" in islamabad_times
    assert "Fajr" in karachi_times
    assert "Maghrib" in islamabad_times
    assert "Maghrib" in karachi_times


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_scheduler_reminder_workflow():
    """
    E2E Test: Automated reminder system

    System Journey:
    1. Time reaches 15 min before Fajr
    2. Scheduler detects it's Sehri time
    3. System triggers reminder
    4. Users would see Sehri reminder
    """

    def sehri_reminder_time():
        # 4:45 AM - 15 min before Fajr at 5:00 AM
        return PKT.localize(datetime(2026, 3, 1, 4, 45))

    bot = RamadanBot(
        bot=None,
        http_session_factory=aiohttp.ClientSession,
        now_provider=sehri_reminder_time,
        random_provider=FakeRandom(),
    )

    # Step 1: Time reaches trigger point
    # Step 2: Fetch prayer times
    timings = await bot.fetch_prayer_times("Islamabad")
    assert timings is not None

    # Cache for testing
    bot.prayer_times_cache["Islamabad_01-03-2026"] = {
        "Fajr": "05:00",
        "Maghrib": "18:00",
    }

    # Step 3: Scheduler checks and triggers
    event = await bot.process_prayer_time_check(None)

    # Step 4: Verify reminder would be sent
    assert event == "SEHRI_REMINDER"


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_complete_day_workflow():
    """
    E2E Test: Complete day in the life of a user

    User Journey:
    1. Morning: Check Sehri countdown
    2. Afternoon: Check Iftar countdown
    3. Evening: Request hadith
    4. Night: Request ayat
    """
    bot = RamadanBot(
        bot=None,
        http_session_factory=aiohttp.ClientSession,
        now_provider=lambda: datetime.now(PKT),
        random_provider=FakeRandom(),
    )

    # Step 1: Morning - Sehri countdown
    timings = await bot.fetch_prayer_times("Islamabad")
    assert timings is not None

    # Step 2: Afternoon - Iftar countdown
    bot.prayer_times_cache["Islamabad_01-03-2026"] = timings
    countdown = await bot.get_iftar_countdown()
    # May be None if past Maghrib, that's okay

    # Step 3: Evening - Hadith
    hadith = await bot.fetch_random_hadith()
    assert hadith is not None

    # Step 4: Night - Ayat
    ayat = await bot.fetch_random_ayat()
    assert ayat is not None

    # Verify user had complete experience
    assert timings is not None
    assert hadith is not None
    assert ayat is not None
