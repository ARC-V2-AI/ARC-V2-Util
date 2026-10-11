from collections.abc import Awaitable, Callable
from typing import TypeVar

T = TypeVar("T")

async def retry(
    function: Callable[[], Awaitable[T]],
    attempts: int = 3,
    delay: float = 2.0,
) -> T: ...
