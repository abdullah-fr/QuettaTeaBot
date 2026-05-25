import asyncio
import logging
import random
from typing import Any, Awaitable, Callable, Optional, Sequence, Type, TYPE_CHECKING

if TYPE_CHECKING:
    from aiohttp import ClientError
else:
    try:
        from aiohttp import ClientError
    except ImportError:  # pragma: no cover
        ClientError = Exception  # type: ignore[assignment]

logger = logging.getLogger(__name__)

HTTP_RETRY_STATUSES = (429, 500, 502, 503, 504)


class RetryError(Exception):
    """Raised when all retry attempts are exhausted."""


class HttpStatusError(Exception):
    def __init__(self, status: int, body: Any | None = None):
        self.status = status
        self.body = body
        super().__init__(f"HTTP status {status}")


async def retry_async(
    func: Callable[..., Awaitable[Any]],
    *args: Any,
    retries: int = 2,
    delay: float = 0.5,
    backoff: float = 2.0,
    retry_exceptions: Sequence[Type[BaseException]] = (
        asyncio.TimeoutError,
        ClientError,
        HttpStatusError,
    ),
    logger: Optional[logging.Logger] = None,
    log_message: str = "Transient error, retrying",
    **kwargs: Any,
) -> Any:
    """Retry an async operation with exponential backoff."""
    logger = logger or logging.getLogger(__name__)
    attempt = 0
    while True:
        try:
            result = await func(*args, **kwargs)
            return result
        except tuple(retry_exceptions) as exc:
            if attempt >= retries:
                logger.error(
                    "Retry attempts exhausted",
                    extra={"attempt": attempt, "error": str(exc)},
                )
                raise RetryError("Retry attempts exhausted") from exc

            delay_seconds = delay * (backoff**attempt) + random.uniform(0, 0.1)
            logger.warning(
                log_message,
                extra={
                    "attempt": attempt + 1,
                    "delay": round(delay_seconds, 2),
                    "error": str(exc),
                },
            )
            await asyncio.sleep(delay_seconds)
            attempt += 1
