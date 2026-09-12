from asyncio import sleep
from collections.abc import Awaitable, Callable
from typing import TypeVar

from arc_v2_util.errors import RetryError

T = TypeVar("T")


async def retry(
    function: Callable[[], Awaitable[T]],
    attempts: int = 3,
    delay: float = 2.0,
) -> T:
    exceptions: list[Exception] = []

    for attempt in range(1, attempts + 1):
        try:
            return await function()
        except Exception as exc:
            exceptions.append(exc)

            if attempt >= attempts:
                raise RetryError(
                    f"Failed to execute {function.__name__} "  # pyright: ignore[reportImplicitStringConcatenation]
                    f"after {attempts} attempts: "
                    + "; ".join(str(error) for error in exceptions)
                ) from exc

            await sleep(delay)

    raise AssertionError("unreachable")
