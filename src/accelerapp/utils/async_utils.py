"""
Async utility functions for Accelerapp.
Provides helpers for async operations and concurrency management.
"""

import asyncio
from typing import Any, Awaitable, Callable, List, TypeVar

T = TypeVar("T")


async def run_async(func: Callable[..., T], *args, **kwargs) -> T:
    """
    Run a synchronous function in an async context.

    Args:
        func: Function to run
        *args: Positional arguments
        **kwargs: Keyword arguments

    Returns:
        Function result
    """
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, lambda: func(*args, **kwargs))


async def gather_with_concurrency(n: int, *tasks: Awaitable[T]) -> List[T]:
    """
    Run tasks with limited concurrency.

    Args:
        n: Maximum number of concurrent tasks
        *tasks: Tasks to run

    Returns:
        List of task results
    """
    semaphore = asyncio.Semaphore(n)

    async def bounded_task(task: Awaitable[T]) -> T:
        async with semaphore:
            return await task

    return await asyncio.gather(*[bounded_task(task) for task in tasks])


async def retry_async(
    func: Callable[..., Awaitable[T]],
    max_attempts: int = 3,
    backoff: float = 1.0,
    *args,
    **kwargs,
) -> T:
    """
    Retry an async function with exponential backoff.

    Args:
        func: Async function to retry
        max_attempts: Maximum number of attempts
        backoff: Initial backoff time in seconds
        *args: Positional arguments for func
        **kwargs: Keyword arguments for func

    Returns:
        Function result

    Raises:
        Exception: If all attempts fail
    """
    last_exception = None

    for attempt in range(max_attempts):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            last_exception = e
            if attempt < max_attempts - 1:
                wait_time = backoff * (2**attempt)
                await asyncio.sleep(wait_time)

    raise last_exception


async def timeout_async(coro: Awaitable[T], timeout_seconds: float) -> T:
    """
    Run a coroutine with a timeout.

    Args:
        coro: Coroutine to run
        timeout_seconds: Timeout in seconds

    Returns:
        Coroutine result

    Raises:
        asyncio.TimeoutError: If timeout is exceeded
    """
    return await asyncio.wait_for(coro, timeout=timeout_seconds)


class AsyncBatchProcessor:
    """Process items in batches asynchronously."""

    def __init__(self, batch_size: int = 10, max_concurrency: int = 5):
        """
        Initialize batch processor.

        Args:
            batch_size: Number of items per batch
            max_concurrency: Maximum concurrent batches
        """
        self.batch_size = batch_size
        self.max_concurrency = max_concurrency

    async def process(
        self, items: List[Any], processor: Callable[[Any], Awaitable[Any]]
    ) -> List[Any]:
        """
        Process items in batches.

        Args:
            items: Items to process
            processor: Async function to process each item

        Returns:
            List of processed results
        """
        results = []

        # Split into batches
        batches = [items[i : i + self.batch_size] for i in range(0, len(items), self.batch_size)]

        # Process batches with concurrency limit
        for batch in batches:
            batch_tasks = [processor(item) for item in batch]
            batch_results = await gather_with_concurrency(self.max_concurrency, *batch_tasks)
            results.extend(batch_results)

        return results
