"""Shared utilities: retry decorator and async rate limiter."""

import asyncio
import logging

from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

logger = logging.getLogger(__name__)


retry_with_backoff = retry(
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=1, min=2, max=30),
    retry=retry_if_exception_type((ConnectionError, TimeoutError)),
    before_sleep=lambda retry_state: logger.warning(
        "Retry attempt %s after error: %s",
        retry_state.attempt_number,
        retry_state.outcome.exception() if retry_state.outcome else "unknown",
    ),
)


async def async_rate_limiter(calls_per_second: float = 3.0) -> None:
    """Sleep to enforce a maximum request rate."""
    await asyncio.sleep(1.0 / calls_per_second)
