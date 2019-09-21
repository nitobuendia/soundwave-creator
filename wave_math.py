"""Math helpers for wave operations."""

from typing import Union

Number = Union[int, float]


def limit_value_to_range(
        value: Number, min_value: Number, max_value: Number) -> Number:
  """Limits a number to a range.

  Args:
    value: Number to limit.
    min_value: Min value that value can take.
    max_value: Max value that value can take.

  Returns:
    Value within/limited by value range provided.
  """
  if value >= max_value:
    return max_value
  if value <= min_value:
    return min_value
  return value
