"""Unit-explicit money conversion helpers.

Clockify money fields use several incompatible scales; values always stay in
their documented wire unit. These helpers exist so conversions are named, never
implicit:

- rates and expense TOTALS arrive in MINOR units (cents);
- expense `amount` on create/update is sent in MAJOR units;
- invoice-item `unitPrice` and invoice tax/discount percentages use
  minor-units-times-100: wire value 2_550_000 means 255.00 major units.
  Always check the operation's manifest note before converting.
"""


def minor_to_major(minor_units: int) -> float:
    """Cents -> major currency units (e.g. 12345 -> 123.45)."""
    return minor_units / 100


def major_to_minor(major_units: float) -> int:
    """Major currency units -> cents, rounded to the nearest cent."""
    return round(major_units * 100)


def minor_times_100_to_major(value: int) -> float:
    """Minor-units-times-100 wire values (invoice unitPrice/percentages) -> major units."""
    return value / 10_000


def major_to_minor_times_100(major_units: float) -> int:
    """Major units -> the minor-times-100 wire scale used by invoice fields."""
    return round(major_units * 10_000)
