"""Creates sound wave functions."""

import enum
import math
import random
from typing import Any, Callable, Mapping, Optional, Text

_DEFAULT_VOLUME = 100
_DEFAULT_FREQUENCY = 440
_DEFAULT_SAMPLE_RATE = 44100  # Number of frames/samples per second (standard).

_MIN_INT16 = -32768
_MAX_INT16 = 32767


class SoundWaveOptions(enum.Enum):
  """Represents options to configure the waves."""
  FREQUENCY = 'frequency'
  VOLUME = 'volume'


# Configuration of the wave options.
WaveOptions = Mapping[SoundWaveOptions, Any]

# A wave function takes the frame and outputs the sample for the frame.
WaveFunction = Callable[[int], int]


def _get_sample_frame_frequency(
        sample_frame: int,
        wave_options: Optional[WaveOptions] = None) -> float:
  """Gets the frequency for a given sample frame.

  Args:
    sample_frame: Frame for which to obtain frequency.
    wave_options: Wave function configuration.

  Returns:
    Frequency for given sample frame and wave options.
  """
  wave_options = wave_options or {}
  wave_frequency = wave_options.get(
      SoundWaveOptions.FREQUENCY, _DEFAULT_FREQUENCY)
  samples_per_cycle = int(_DEFAULT_SAMPLE_RATE / wave_frequency)
  return (sample_frame % samples_per_cycle) / samples_per_cycle


def _get_volume_adjustment(
        wave_options: Optional[WaveOptions] = None) -> float:
  """Gets the volume adjustment based on wave options.

  Args:
    wave_options: Wave function configuration.

  Returns:
    Volume adjustment.
  """
  wave_options = wave_options or {}
  wave_volume = wave_options.get(SoundWaveOptions.VOLUME, _DEFAULT_VOLUME)
  return float(wave_volume) / 100


def get_sin_wave(wave_options: Optional[WaveOptions] = None) -> WaveFunction:
  """Creates a sound wave with sin function."""
  volume_adjustment = _get_volume_adjustment(wave_options)

  def sin_sound_wave(sample_frame: int) -> int:
    """Sin wave function.

    A single-frequency sound wave with frequency f, maximum amplitude A, and
    phase θ is represented by the sine function:
      y = Asin(2πfx+θ)
    where x is time and y is the amplitude of the sound wave at time x.
    """
    sample_frequency = _get_sample_frame_frequency(sample_frame, wave_options)
    frame_sample = (_MAX_INT16 * math.sin(2 * math.pi * sample_frequency) *
                    volume_adjustment)
    return int(frame_sample)

  return sin_sound_wave


def get_x2_wave(wave_options: Optional[WaveOptions] = None) -> WaveFunction:
  """Creates a sound wave with x**2 function."""
  def x2_sound_wave(sample_frame: int) -> int:
    sample_frequency = _get_sample_frame_frequency(sample_frame, wave_options)
    return int((sample_frequency ** 2) % _MIN_INT16)
  return x2_sound_wave


def get_random_wave(
        wave_options: Optional[WaveOptions] = None) -> WaveFunction:
  """Gets a random value wave."""
  def random_sound_wave(sample_frame: int) -> int:
    del sample_frame
    random_sample = random.randint(_MIN_INT16, _MAX_INT16)
    return int(random_sample)
  return random_sound_wave


def get_sawtooth_function(
        wave_options: Optional[WaveOptions] = None) -> WaveFunction:
  """Gets a wave function that works in spikes."""
  max_range = abs(_MIN_INT16) + abs(_MAX_INT16)

  def sawtooth_sound_wave(sample_frame: int) -> int:
    spike_round = int(sample_frame / max_range)
    sample_value = sample_frame + _MIN_INT16 - spike_round * max_range
    return int(sample_value)

  return sawtooth_sound_wave


class SoundWaveType(enum.Enum):
  """Represents a Sound Wave Type(equation)."""
  SIN_WAVE = 'sin'
  X2_WAVE = 'x**2'
  RANDOM_WAVE = 'random'
  SAWTOOTH_WAVE = 'sawtooth'


SOUND_WAVE_FUNCTION_MAP = {
    SoundWaveType.SIN_WAVE: get_sin_wave,
    SoundWaveType.X2_WAVE: get_x2_wave,
    SoundWaveType.RANDOM_WAVE: get_random_wave,
    SoundWaveType.SAWTOOTH_WAVE: get_sawtooth_function,
}
