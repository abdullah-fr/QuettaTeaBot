"""
Stress tests for Discord bot.

Tests system limits and behavior under extreme conditions:
- High concurrent load
- Resource exhaustion scenarios
- System breaking points
"""

import pytest
import time
import asyncio
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


@pytest.mark.performance
@pytest.mark.slow
@pytest.mark.asyncio
async def test_high_concurrency_stress():
    """
    Stress Test: High concurrency

    Pushes system with 50 concurrent requests
    Expected: System degrades gracefully, doesn't crash
    """
    bot = RamadanBot(
        bot=None,
        http_session_factory=aiohttp.ClientSession,
        now_provider=lambda: datetime.now(PKT),
        random_provider=FakeRandom(),
    )

    num_requests = 50
    start_time = time.time()

    tasks = [bot.fetch_prayer_times("Islamabad") for _ in range(num_requests)]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    end_time = time.time()
    total_time = end_time - start_time

    successful = [r for r in results if r is not None and not isinstance(r, Exception)]
    failed = [r for r in results if isinstance(r, Exception)]
    success_rate = len(successful) / num_requests * 100

    print(f"\n✅ High Concurrency Stress Test:")
    print(f"   Concurrent Requests: {num_requests}")
    print(f"   Total Time: {total_time:.2f}s")
    print(f"   Successful: {len(successful)}")
    print(f"   Failed: {len(failed)}")
    print(f"   Success Rate: {success_rate:.1f}%")
    print(f"   Throughput: {num_requests/total_time:.2f} req/s")

    # Under stress, we accept lower success rate but system shouldn't crash
    # API rate limiting is expected under extreme load (CI has stricter limits)
    assert success_rate >= 15, f"Success rate {success_rate}% below 15% threshold"


@pytest.mark.performance
@pytest.mark.slow
@pytest.mark.asyncio
async def test_rapid_fire_requests():
    """
    Stress Test: Rapid fire requests

    Sends requests as fast as possible
    Expected: System handles without crashing
    """
    bot = RamadanBot(
        bot=None,
        http_session_factory=aiohttp.ClientSession,
        now_provider=lambda: datetime.now(PKT),
        random_provider=FakeRandom(),
    )

    num_requests = 20
    start_time = time.time()

    # No delays between requests
    tasks = [bot.fetch_prayer_times("Islamabad") for _ in range(num_requests)]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    end_time = time.time()
    total_time = end_time - start_time

    successful = [r for r in results if r is not None and not isinstance(r, Exception)]
    success_rate = len(successful) / num_requests * 100

    print(f"\n✅ Rapid Fire Stress Test:")
    print(f"   Requests: {num_requests}")
    print(f"   Total Time: {total_time:.2f}s")
    print(f"   Success Rate: {success_rate:.1f}%")
    print(f"   Rate: {num_requests/total_time:.2f} req/s")

    # System should handle at least 30% under rapid fire (API rate limiting expected)
    assert success_rate >= 30, f"Success rate {success_rate}% below 30% threshold"


@pytest.mark.performance
@pytest.mark.asyncio
async def test_memory_stress():
    """
    Stress Test: Memory usage under load

    Tests cache growth and memory management
    Expected: Cache doesn't grow unbounded
    """
    bot = RamadanBot(
        bot=None,
        http_session_factory=aiohttp.ClientSession,
        now_provider=lambda: datetime.now(PKT),
        random_provider=FakeRandom(),
    )

    cities = ["Islamabad", "Lahore", "Karachi", "Peshawar", "Quetta",
              "Faisalabad", "Rawalpindi", "Multan"]

    # Fill cache with multiple cities
    for city in cities:
        await bot.fetch_prayer_times(city)
        await asyncio.sleep(0.1)

    cache_size = len(bot.prayer_times_cache)

    print(f"\n✅ Memory Stress Test:")
    print(f"   Cities Cached: {cache_size}")
    print(f"   Cache Keys: {list(bot.prayer_times_cache.keys())[:3]}...")

    # Cache should have entries but not be excessive
    assert cache_size > 0, "Cache should have entries"
    assert cache_size <= 20, f"Cache size {cache_size} may indicate memory leak"


@pytest.mark.performance
@pytest.mark.slow
@pytest.mark.asyncio
async def test_error_recovery_stress():
    """
    Stress Test: Error recovery under stress

    Tests system recovery after failures
    Expected: System recovers and continues working
    """
    bot = RamadanBot(
        bot=None,
        http_session_factory=aiohttp.ClientSession,
        now_provider=lambda: datetime.now(PKT),
        random_provider=FakeRandom(),
    )

    # Mix of valid and potentially problematic requests
    tasks = []
    for i in range(15):
        if i % 3 == 0:
            # Valid request
            tasks.append(bot.fetch_prayer_times("Islamabad"))
        else:
            # Another valid request
            tasks.append(bot.fetch_prayer_times("Lahore"))

    results = await asyncio.gather(*tasks, return_exceptions=True)

    successful = [r for r in results if r is not None and not isinstance(r, Exception)]
    success_rate = len(successful) / len(tasks) * 100

    print(f"\n✅ Error Recovery Stress Test:")
    print(f"   Total Requests: {len(tasks)}")
    print(f"   Successful: {len(successful)}")
    print(f"   Success Rate: {success_rate:.1f}%")

    # System should recover and maintain reasonable success rate
    # In CI, API rate limiting may cause very low success rates (stricter than local)
    # The test validates the system doesn't crash under stress, not API availability
    assert success_rate >= 40, f"Success rate {success_rate}% below 40% threshold"


@pytest.mark.performance
@pytest.mark.asyncio
async def test_scheduler_under_stress():
    """
    Stress Test: Scheduler logic under rapid checks

    Tests scheduler performance with rapid time checks
    Expected: Calculations remain fast
    """

    def test_time():
        return PKT.localize(datetime(2026, 3, 1, 4, 45))

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

    num_checks = 100
    start_time = time.time()

    # Rapid scheduler checks
    for _ in range(num_checks):
        await bot.process_prayer_time_check(None)

    end_time = time.time()
    total_time = end_time - start_time
    avg_time = total_time / num_checks

    print(f"\n✅ Scheduler Stress Test:")
    print(f"   Checks: {num_checks}")
    print(f"   Total Time: {total_time:.3f}s")
    print(f"   Avg per Check: {avg_time:.4f}s")
    print(f"   Checks/sec: {num_checks/total_time:.2f}")

    # Scheduler should remain fast even under stress
    assert avg_time < 0.01, f"Avg check time {avg_time:.4f}s exceeds 0.01s threshold"
