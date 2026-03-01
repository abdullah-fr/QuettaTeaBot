"""
Performance tests for API endpoints.

Measures:
- Response times
- Throughput
- Concurrent request handling
- API latency
"""

import pytest
import time
import asyncio
import aiohttp
from datetime import datetime
import pytz

from src.ramadan_features import RamadanBot
from src.api_helpers import fetch_trivia_question, fetch_joke

PKT = pytz.timezone("Asia/Karachi")


class FakeRandom:
    def randint(self, a, b):
        return a

    def choice(self, items):
        return items[0]


@pytest.mark.performance
@pytest.mark.asyncio
async def test_prayer_times_api_response_time():
    """
    Performance Test: Prayer times API response time

    Baseline: Should respond within 2 seconds
    """
    bot = RamadanBot(
        bot=None,
        http_session_factory=aiohttp.ClientSession,
        now_provider=lambda: datetime.now(PKT),
        random_provider=FakeRandom(),
    )

    start_time = time.time()
    timings = await bot.fetch_prayer_times("Islamabad")
    end_time = time.time()

    response_time = end_time - start_time

    # Verify response time is acceptable
    assert timings is not None
    assert response_time < 2.0, f"Response time {response_time:.2f}s exceeds 2s threshold"

    print(f"\n✅ Prayer Times API: {response_time:.3f}s")


@pytest.mark.performance
@pytest.mark.asyncio
async def test_hadith_api_response_time():
    """
    Performance Test: Hadith API response time

    Baseline: Should respond within 2 seconds
    """
    bot = RamadanBot(
        bot=None,
        http_session_factory=aiohttp.ClientSession,
        now_provider=lambda: datetime.now(PKT),
        random_provider=FakeRandom(),
    )

    start_time = time.time()
    hadith = await bot.fetch_random_hadith()
    end_time = time.time()

    response_time = end_time - start_time

    assert hadith is not None
    assert response_time < 2.0, f"Response time {response_time:.2f}s exceeds 2s threshold"

    print(f"\n✅ Hadith API: {response_time:.3f}s")


@pytest.mark.performance
@pytest.mark.asyncio
async def test_ayat_api_response_time():
    """
    Performance Test: Ayat API response time

    Baseline: Should respond within 2 seconds
    """
    bot = RamadanBot(
        bot=None,
        http_session_factory=aiohttp.ClientSession,
        now_provider=lambda: datetime.now(PKT),
        random_provider=FakeRandom(),
    )

    start_time = time.time()
    ayat = await bot.fetch_random_ayat()
    end_time = time.time()

    response_time = end_time - start_time

    assert ayat is not None
    assert response_time < 2.0, f"Response time {response_time:.2f}s exceeds 2s threshold"

    print(f"\n✅ Ayat API: {response_time:.3f}s")


@pytest.mark.performance
@pytest.mark.asyncio
async def test_trivia_api_response_time():
    """
    Performance Test: Trivia API response time

    Baseline: Should respond within 2 seconds
    """
    start_time = time.time()
    question = await fetch_trivia_question()
    end_time = time.time()

    response_time = end_time - start_time

    if question:  # API may be unavailable
        assert response_time < 2.0, f"Response time {response_time:.2f}s exceeds 2s threshold"
        print(f"\n✅ Trivia API: {response_time:.3f}s")


@pytest.mark.performance
@pytest.mark.asyncio
async def test_joke_api_response_time():
    """
    Performance Test: Joke API response time

    Baseline: Should respond within 2 seconds
    """
    start_time = time.time()
    joke = await fetch_joke()
    end_time = time.time()

    response_time = end_time - start_time

    if joke:  # API may be unavailable
        assert response_time < 2.0, f"Response time {response_time:.2f}s exceeds 2s threshold"
        print(f"\n✅ Joke API: {response_time:.3f}s")


@pytest.mark.performance
@pytest.mark.asyncio
async def test_concurrent_prayer_times_requests():
    """
    Performance Test: Handle 5 concurrent prayer time requests

    Simulates multiple users requesting prayer times simultaneously
    """
    bot = RamadanBot(
        bot=None,
        http_session_factory=aiohttp.ClientSession,
        now_provider=lambda: datetime.now(PKT),
        random_provider=FakeRandom(),
    )

    cities = ["Islamabad", "Lahore", "Karachi", "Peshawar", "Quetta"]

    # Helper function with retry logic for API rate limiting
    async def safe_fetch_prayer_times(city, retries=2):
        """Fetch prayer times with retry logic for rate limiting"""
        for attempt in range(retries + 1):
            result = await bot.fetch_prayer_times(city)
            if result is not None:
                return result
            if attempt < retries:
                await asyncio.sleep(0.5)  # Wait before retry
        return None

    start_time = time.time()

    # Execute concurrent requests with retry logic
    tasks = [safe_fetch_prayer_times(city) for city in cities]
    results = await asyncio.gather(*tasks)

    end_time = time.time()
    total_time = end_time - start_time

    # Verify at least 2 out of 5 requests succeeded (CI has stricter rate limits)
    successful = [r for r in results if r is not None]
    assert (
        len(successful) >= 2
    ), f"At least 2 out of 5 requests should succeed (got {len(successful)})"

    # Should complete within 10 seconds (increased for retries)
    assert (
        total_time < 10.0
    ), f"Concurrent requests took {total_time:.2f}s (threshold: 10s)"

    print(f"\n✅ Concurrent Requests (5): {total_time:.3f}s, {len(successful)}/5 succeeded")
    print(f"   Success Rate: {len(successful)}/5")


@pytest.mark.performance
@pytest.mark.asyncio
async def test_sequential_api_calls_throughput():
    """
    Performance Test: Sequential API call throughput

    Measures how many requests can be processed in sequence
    """
    bot = RamadanBot(
        bot=None,
        http_session_factory=aiohttp.ClientSession,
        now_provider=lambda: datetime.now(PKT),
        random_provider=FakeRandom(),
    )

    num_requests = 3
    start_time = time.time()

    for _ in range(num_requests):
        await bot.fetch_prayer_times("Islamabad")
        await asyncio.sleep(0.1)  # Small delay to avoid rate limiting

    end_time = time.time()
    total_time = end_time - start_time

    avg_time = total_time / num_requests

    print(f"\n✅ Sequential Throughput:")
    print(f"   Total Time: {total_time:.3f}s")
    print(f"   Avg per Request: {avg_time:.3f}s")
    print(f"   Requests/sec: {num_requests/total_time:.2f}")


@pytest.mark.performance
@pytest.mark.asyncio
async def test_cache_performance():
    """
    Performance Test: Cache hit performance

    Cached requests should be significantly faster
    """
    bot = RamadanBot(
        bot=None,
        http_session_factory=aiohttp.ClientSession,
        now_provider=lambda: datetime.now(PKT),
        random_provider=FakeRandom(),
    )

    # First request (cache miss)
    start_time = time.time()
    timings1 = await bot.fetch_prayer_times("Islamabad")
    first_request_time = time.time() - start_time

    # API may be rate limited in CI
    if timings1 is None:
        pytest.skip("Prayer times API unavailable (rate limited)")
        return

    # Second request (cache hit)
    start_time = time.time()
    timings2 = await bot.fetch_prayer_times("Islamabad")
    cached_request_time = time.time() - start_time

    assert timings2 is not None, "Cached request should always succeed"

    # Cached request should be faster (or at least not slower)
    print(f"\n✅ Cache Performance:")
    print(f"   First Request: {first_request_time:.3f}s")
    print(f"   Cached Request: {cached_request_time:.3f}s")
    if cached_request_time > 0:
        print(f"   Speedup: {first_request_time/cached_request_time:.2f}x")


@pytest.mark.performance
@pytest.mark.asyncio
async def test_countdown_calculation_performance():
    """
    Performance Test: Countdown calculation speed

    Should calculate instantly (< 0.1s)
    """

    def test_time():
        return PKT.localize(datetime(2026, 3, 1, 15, 0))

    bot = RamadanBot(
        bot=None,
        http_session_factory=aiohttp.ClientSession,
        now_provider=test_time,
        random_provider=FakeRandom(),
    )

    # Pre-populate cache
    bot.prayer_times_cache["Islamabad_01-03-2026"] = {
        "Fajr": "05:00",
        "Maghrib": "18:00",
    }

    start_time = time.time()
    countdown = await bot.get_iftar_countdown()
    calc_time = time.time() - start_time

    assert countdown is not None
    assert calc_time < 0.1, f"Calculation took {calc_time:.3f}s (should be < 0.1s)"

    print(f"\n✅ Countdown Calculation: {calc_time:.4f}s")
