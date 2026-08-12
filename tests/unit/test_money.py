"""Unit-explicit money helper tests."""

from clockify.money import (
    major_to_minor,
    major_to_minor_times_100,
    minor_times_100_to_major,
    minor_to_major,
)


def test_minor_round_trip() -> None:
    assert minor_to_major(12345) == 123.45
    assert major_to_minor(123.45) == 12345


def test_minor_times_100_round_trip() -> None:
    assert minor_times_100_to_major(2_550_000) == 255.0
    assert major_to_minor_times_100(255.0) == 2_550_000


def test_rounding_is_nearest_cent() -> None:
    assert major_to_minor(0.005) == 0  # banker's rounding on the exact half
    assert major_to_minor(0.015) == 2
