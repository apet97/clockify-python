"""Transport configuration validation tests."""

from typing import Any

import pytest

from clockify.config import ReadRetryPolicy


@pytest.mark.parametrize("value", [0, -1, True, 1.5])
def test_invalid_max_attempts_is_rejected(value: Any) -> None:
    with pytest.raises(ValueError, match="max_attempts"):
        ReadRetryPolicy(max_attempts=value)


@pytest.mark.parametrize("field", ["base_delay", "max_delay"])
@pytest.mark.parametrize("value", [-1.0, float("nan"), float("inf"), True])
def test_invalid_retry_delay_is_rejected(field: str, value: Any) -> None:
    with pytest.raises(ValueError, match=field):
        ReadRetryPolicy(**{field: value})


def test_zero_retry_delays_are_allowed() -> None:
    assert ReadRetryPolicy(base_delay=0.0, max_delay=0.0).max_delay == 0.0
