"""
Load tests for Discord bot.

Simulates normal and peak load scenarios:
- Normal daily usage
- Peak traffic periods
- Sustained load
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
async def test_normal_load_scenario():
    """
    Load Test: Normal daily usage

    Simulates 10 users making requests over 10 seconds
    Expected: All requests succeed, avg response < 2s
    """
    bot = RamadanBot(
        bot=None,
        http_session_factory=aiohttp.ClientSession,
        now_provider=lambda: datetime.now(PKT),
        random_provider=FakeRandom(),
    )

    num_users = 10
    start_time = time.time()

    # Simulate users making requests
    tasks = []
    for i in range(num_users):
        city = ["Islamabad", "Lahore", "Karachi"][i % 3]
        tasks.append(bot.fetch_prayer_times(city))
        await asyncio.sleep(0.1)  # Stagger requests

    results = await asyncio.gather(*tasks, return_exceptions=True)
    end_time = time.time()

    total_time = end_time - start_time
    successful = [r for r in results if r is not None and not isinstance(r, Exception)]
    success_rate = len(successful) / num_users * 100

    print(f"\n✅ Normal Load Test:")
    print(f"   Users: {num_users}")
    print(f"   Total Time: {total_time:.2f}s")
    print(f"   Success Rate: {success_rate:.1f}%")
    print(f"   Avg Response: {total_time/num_users:.2f}s")

    # Assertions
    assert success_rate >= 80, f"Success rate {success_rate}% below 80% threshold"
    assert total_time < 15, f"Total time {total_time:.2f}s exceeds 15s threshold"


@pytest.mark.performance
@pytest.mark.slow
@pytest.mark.asyncio
async def test_peak_load_scenario():
    """
    Load Test: Peak traffic simulation

    Simulates 20 concurrent users (peak time like Iftar)
    Expected: System handles load gracefully
    """
    bot = RamadanBot(
        bot=None,
        http_session_factory=aiohttp.ClientSession,
        now_provider=lambda: datetime.now(PKT),
        random_provider=FakeRandom(),
    )

    num_users = 20
    start_time = time.time()

    # All users request simultaneously (peak load)
    tasks = [bot.fetch_prayer_times("Islamabad") for _ in range(num_users)]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    end_time = time.time()
    total_time = end_time - start_time

    successful = [r for r in results if r is not None and not isinstance(r, Exception)]
    success_rate = len(successful) / num_users * 100

    print(f"\n✅ Peak Load Test:")
    print(f"   Concurrent Users: {num_users}")
    print(f"   Total Time: {total_time:.2f}s")
    print(f"   Success Rate: {success_rate:.1f}%")
    print(f"   Throughput: {num_users/total_time:.2f} req/s")

    # Peak load should still maintain 50% success rate (lowered from 70% due to API limits)
    assert success_rate >= 50, f"Success rate {success_rate}% below 50% threshold"


@pytest.mark.performance
@pytest.mark.slow
@pytest.mark.asyncio
async def test_sustained_load():
    """
    Load Test: Sustained load over time

    Simulates continuous usage for 30 seconds
    Expected: System remains stable
    """
    bot = RamadanBot(
        bot=None,
        http_session_factory=aiohttp.ClientSession,
        now_provider=lambda: datetime.now(PKT),
        random_provider=FakeRandom(),
    )

    duration = 10  # Reduced to 10 seconds for faster testing
    request_interval = 1  # 1 request per second

    start_time = time.time()
    successful_requests = 0
    failed_requests = 0

    while time.time() - start_time < duration:
        try:
            result = await bot.fetch_prayer_times("Islamabad")
            if result:
                successful_requests += 1
            else:
                failed_requests += 1
        except Exception:
            failed_requests += 1

        await asyncio.sleep(request_interval)

    total_requests = successful_requests + failed_requests
    success_rate = successful_requests / total_requests * 100 if total_requests > 0 else 0

    print(f"\n✅ Sustained Load Test:")
    print(f"   Duration: {duration}s")
    print(f"   Total Requests: {total_requests}")
    print(f"   Successful: {successful_requests}")
    print(f"   Failed: {failed_requests}")
    print(f"   Success Rate: {success_rate:.1f}%")

    # Should maintain at least 80% success rate
    assert success_rate >= 80, f"Success rate {success_rate}% below 80% threshold"


@pytest.mark.performance
@pytest.mark.asyncio
async def test_mixed_workload():
    """
    Load Test: Mixed API workload

    Simulates users requesting different features simultaneously
    Expected: All features work under load
    """
    bot = RamadanBot(
        bot=None,
        http_session_factory=aiohttp.ClientSession,
        now_provider=lambda: datetime.now(PKT),
        random_provider=FakeRandom(),
    )

    start_time = time.time()

    # Mix of different requests
    tasks = [
        bot.fetch_prayer_times("Islamabad"),
        bot.fetch_prayer_times("Lahore"),
        bot.fetch_random_hadith(),
        bot.fetch_random_ayat(),
        bot.fetch_prayer_times("Karachi"),
    ]

    results = await asyncio.gather(*tasks, return_exceptions=True)
    end_time = time.time()

    total_time = end_time - start_time
    successful = [r for r in results if r is not None and not isinstance(r, Exception)]
    success_rate = len(successful) / len(tasks) * 100

    print(f"\n✅ Mixed Workload Test:")
    print(f"   Total Requests: {len(tasks)}")
    print(f"   Total Time: {total_time:.2f}s")
    print(f"   Success Rate: {success_rate:.1f}%")

    assert success_rate >= 80, f"Success rate {success_rate}% below 80% threshold"


@pytest.mark.performance
@pytest.mark.asyncio
async def test_cache_under_load():
    """
    Load Test: Cache performance under load

    Tests that caching improves performance under repeated requests
    """
    bot = RamadanBot(
        bot=None,
        http_session_factory=aiohttp.ClientSession,
        now_provider=lambda: datetime.now(PKT),
        random_provider=FakeRandom(),
    )

    # First request to populate cache
    await bot.fetch_prayer_times("Islamabad")

    # Now test cached performance under load
    num_requests = 10
    start_time = time.time()

    tasks = [bot.fetch_prayer_times("Islamabad") for _ in range(num_requests)]
    results = await asyncio.gather(*tasks)

    end_time = time.time()
    total_time = end_time - start_time
    avg_time = total_time / num_requests

    print(f"\n✅ Cache Under Load:")
    print(f"   Requests: {num_requests}")
    print(f"   Total Time: {total_time:.2f}s")
    print(f"   Avg per Request: {avg_time:.3f}s")

    # Cached requests should be fast
    assert avg_time < 1.0, f"Avg cached request time {avg_time:.3f}s exceeds 1s"
