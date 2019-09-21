"""Creates sound wave functions."""

import enum
import math
import random
import wave_math
from typing import Any, Callable, Mapping, Optional, Text

_DEFAULT_DEBUG_MODE = False
_DEFAULT_VOLUME = 100
_DEFAULT_FREQUENCY = 440
_DEFAULT_SAMPLE_RATE = 44100  # Number of frames/samples per second (standard).

_MIN_INT16 = -32768
_MAX_INT16 = 32767


class SoundWaveOptions(enum.Enum):
  """Represents options to configure the waves."""
  DEBUG = 'debug'  # Debug mode allows printing formulas and others.
  FREQUENCY = 'frequency'
  VOLUME = 'volume'


class SoundWaveType(enum.Enum):
  """Represents a Sound Wave Type(equation)."""
  SIN_WAVE = 'sin'
  X2_WAVE = 'x**2'
  RANDOM_WAVE = 'random'
  SAWTOOTH_WAVE = 'sawtooth'


# Configuration of the wave options.
WaveOptions = Mapping[SoundWaveOptions, Any]

# A wave function takes the frame and outputs the sample for the frame.
WaveFunction = Callable[[int], int]


class WaveFunctionBuilder(object):
  """Generator of wave functions."""

  def __init__(self, wave_options: Optional[WaveOptions] = None):
    """Instantiates a WaveFunctionBuilder.

    Args:
      wave_options: Wave configuration.
    """
    # Make first, so other functions can rely on is self reference.
    self._wave_options = wave_options or {}

  def _get_merged_wave_options(
          self, wave_options: Optional[WaveOptions]) -> WaveOptions:
    """Combines wave builder and wave specific wave options.

    Args:
      wave_options: Wave configuration.
    """
    wave_options = wave_options or {}
    combined_wave_options = {}
    combined_wave_options.update(self._wave_options)
    combined_wave_options.update(wave_options)
    return combined_wave_options

  def _get_debug_mode(self, wave_options: WaveOptions) -> bool:
    """Gets whether to debug wave or not.

    Args:
      wave_options: Wave configuration.

    Returns:
      Whether to apply debug mode.
    """
    return wave_options.get(SoundWaveOptions.DEBUG, _DEFAULT_DEBUG_MODE)

  def _get_volume(self, wave_options: WaveOptions) -> float:
    """Gets the volume based on wave options.

    Args:
      wave_options: Wave configuration.

    Returns:
      Volume.
    """
    return float(wave_options.get(SoundWaveOptions.VOLUME, _DEFAULT_VOLUME))

  def _get_volume_adjustment(self, wave_options: WaveOptions) -> float:
    """Gets the volume adjustment based on wave options.

    Args:
      wave_options: Wave configuration.

    Returns:
      Volume adjustment.
    """
    return self._get_volume(wave_options) / 100

  def _get_wave_frequency(self, wave_options: WaveOptions) -> float:
    """Gets the wave frequency.

    Args:
      wave_options: Wave configuration.

    Returns:
      Wave frequency.
    """
    return wave_options.get(SoundWaveOptions.FREQUENCY, _DEFAULT_FREQUENCY)

  def _get_samples_per_cycle(self, wave_options: WaveOptions) -> int:
    """Gets number of samples that will be generated per wave cycle.

    Args:
      wave_options: Wave configuration.

    Returns:
      Samples per cycle.
    """
    wave_frequency = self._get_wave_frequency(wave_options)
    return int(_DEFAULT_SAMPLE_RATE / wave_frequency)

  def _get_sample_frame_frequency(
          self, sample_frame: int, wave_options: WaveOptions) -> float:
    """Gets the frequency for a given sample frame.

    Args:
      sample_frame: Frame for which to obtain frequency.

    Returns:
      Frequency for given sample frame and wave options.
    """
    samples_per_cycle = self._get_samples_per_cycle(wave_options)
    return (sample_frame % samples_per_cycle) / samples_per_cycle

  def get_wave_function(
          self, sound_wave_type: SoundWaveType,
          wave_specific_options: Optional[SoundWaveOptions] = None
  ) -> WaveFunction:
    """Gets a sound wave generator.

    Args:
      sound_wave_type: Type of sound wave to generate.
      wave_specific_options: Modifiers to the specific wave.

    Raises:
      ValueError: Unknown SoundWaveType.

    Returns:
      Function that generates requested sound wave.
    """
    wave_options = self._get_merged_wave_options(wave_specific_options)

    debug_mode = self._get_debug_mode(wave_options)

    volume_adjustment = self._get_volume_adjustment(wave_options)

    min_value = _MIN_INT16
    max_value = _MAX_INT16
    max_range = abs(min_value) + abs(max_value)

    samples_per_cycle = self._get_samples_per_cycle(wave_options)

    def _normalize_sample_value(sample_value: wave_math.Number) -> int:
      """Applies common normalization operations to sample value.

      Normalizations:
        - Adjust sample value by volume.
        - Limit value to a specific range.
        - Transform value to integer.

      Args:
        sample_value: Value of the sample.

      Returns:
        Value of the sample, after normalization opperations are applied.
      """
      sample_value = sample_value * volume_adjustment
      sample_value = wave_math.limit_value_to_range(
          sample_value, min_value, max_value)
      sample_value = int(sample_value)
      return sample_value

    if sound_wave_type == SoundWaveType.SIN_WAVE:
      def sin_sound_wave(sample_frame: int) -> int:
        """Sin wave function.

        A single-frequency sound wave with frequency f, maximum amplitude A,
        and phase θ is represented by the sine function:
          y = Asin(2πfx+θ)
        where x is time and y is the amplitude of the sound wave at time x.
        """
        sample_frequency = self._get_sample_frame_frequency(
            sample_frame, wave_options)
        sample_value = max_value * math.sin(2 * math.pi * sample_frequency)
        if debug_mode:
          print(
              f'{sample_frame}: {max_value} * sin(2π{sample_frequency})'
              f' = {sample_value}')
        return _normalize_sample_value(sample_value)
      return sin_sound_wave

    if sound_wave_type == SoundWaveType.SAWTOOTH_WAVE:
      def sawtooth_sound_wave(sample_frame: int) -> int:
        """Sawtooth wave function."""
        spike_cycle = int(sample_frame / max_range)
        sample_value = sample_frame + min_value - spike_cycle * max_range
        if debug_mode:
          print(
              f'{sample_frame}: {sample_frame} + {min_value} - {spike_cycle} '
              f'* {max_range} = {sample_value}')
        return _normalize_sample_value(sample_value)
      return sawtooth_sound_wave

    if sound_wave_type == SoundWaveType.RANDOM_WAVE:
      def random_sound_wave(sample_frame: int) -> int:
        """Gets a random value wave."""
        del sample_frame  # Unused, but intended to keep same fn signature.
        random_sample = random.randint(min_value, max_value)
        if debug_mode:
          print(f'{sample_frame}: {random_sample}')
        return _normalize_sample_value(random_sample)
      return random_sound_wave

    if sound_wave_type == SoundWaveType.X2_WAVE:
      def x2_sound_wave(sample_frame: int) -> int:
        """Creates a sound wave with x**2 function."""
        m = 4 * (min_value - max_value) / (samples_per_cycle ** 2)
        b = max_value
        x = sample_frame % samples_per_cycle
        sample_value = m * (x ** 2) + b
        if debug_mode:
          print(f'{sample_frame}: ({m} * {x}^2 + {b}) = {sample_value}')
        return _normalize_sample_value(sample_value)
      return x2_sound_wave

    raise ValueError(f'Unknown wave type: {sound_wave_type}')
