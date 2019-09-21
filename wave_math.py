"""Math helpers for wave operations."""

from typing import Union

Number = Union[int, float]


def get_max_value_from_bytes(bytes_size: int, signed=True) -> int:
  """Gets the max value that a number can be given the bytes.

  Args:
    bytes_size: Bytes size.
    signed: Whether number is signed or not.

  Returns:
    Max number for given bytes.
  """
  bits_size = bytes_size * 8
  if signed:
    bits_size = bits_size - 1  # Remove one bit for sign.
  return 2 ** bits_size


def get_min_value_from_bytes(bytes_size: int, signed=True) -> int:
  """Gets the min value that a number can be given the bytes.

  Args:
    bytes_size: Bytes size.
    signed: Whether number is signed or not.

  Returns:
    Min number for given bytes.
  """
  if not signed:
    return 0

  max_size = get_max_value_from_bytes(bytes_size, signed)
  return -max_size


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
