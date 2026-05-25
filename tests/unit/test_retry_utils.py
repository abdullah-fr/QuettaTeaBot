import asyncio

import pytest

from src.retry_utils import RetryError, retry_async


async def _succeed_after_one_retry(counter):
    if counter["attempts"] == 0:
        counter["attempts"] += 1
        raise asyncio.TimeoutError("temporary failure")
    return "success"


def test_retry_async_succeeds_after_retry():
    counter = {"attempts": 0}
    result = asyncio.run(
        retry_async(
            _succeed_after_one_retry, counter, retries=2, delay=0.01, backoff=1.0
        )
    )
    assert result == "success"
    assert counter["attempts"] == 1


def test_retry_async_exhausts_retries_and_raises():
    async def always_fail():
        raise asyncio.TimeoutError("still failing")

    with pytest.raises(RetryError):
        asyncio.run(retry_async(always_fail, retries=1, delay=0.01, backoff=1.0))


def test_retry_async_does_not_retry_non_retryable_exception():
    class CustomError(Exception):
        pass

    async def fail_once():
        raise CustomError("fatal")

    with pytest.raises(CustomError):
        asyncio.run(retry_async(fail_once, retries=2, delay=0.01, backoff=1.0))
