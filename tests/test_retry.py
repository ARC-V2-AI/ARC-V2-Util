import pytest

from arc_v2_util.errors import RetryError
from arc_v2_util.retry import retry


@pytest.mark.asyncio
async def test_retry_succeeds_first_attempt() -> None:
    calls = 0

    async def function() -> str:
        nonlocal calls
        calls += 1
        return "success"

    result = await retry(function)

    assert result == "success"
    assert calls == 1


@pytest.mark.asyncio
async def test_retry_succeeds_after_failures() -> None:
    calls = 0

    async def function() -> str:
        nonlocal calls
        calls += 1

        if calls < 3:
            raise RuntimeError(f"failure {calls}")

        return "success"

    result = await retry(
        function,
        attempts=3,
        delay=0,
    )

    assert result == "success"
    assert calls == 3


@pytest.mark.asyncio
async def test_retry_raises_after_attempts_exhausted() -> None:
    calls = 0

    async def function() -> None:
        nonlocal calls
        calls += 1
        raise RuntimeError(f"failure {calls}")

    with pytest.raises(RetryError, match="after 3 attempts"):
        await retry(
            function,
            attempts=3,
            delay=0,
        )

    assert calls == 3


@pytest.mark.asyncio
async def test_retry_preserves_original_exception() -> None:
    async def function() -> None:
        raise ValueError("test error")

    with pytest.raises(RetryError) as exc_info:
        await retry(function, attempts=1, delay=0)

    assert isinstance(exc_info.value.__cause__, ValueError)
    assert str(exc_info.value.__cause__) == "test error"


@pytest.mark.asyncio
async def test_retry_attempts_once() -> None:
    calls = 0

    async def function() -> None:
        nonlocal calls
        calls += 1
        raise RuntimeError("failure")

    with pytest.raises(RetryError):
        await retry(function, attempts=1, delay=0)

    assert calls == 1
