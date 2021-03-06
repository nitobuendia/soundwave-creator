"""Generates sound wave functions and values."""

import array
import enum
import math
import random
import wave_math
import wave_settings
from typing import Any, Callable, Mapping, Optional, Text, Tuple


class SoundWaveOption(enum.Enum):
  """Represents options to configure the waves."""
  # Wave amplitude. Determines min and max sample values.
  AMPLITUDE = 'amplitude'
  # Wave amplitude adjustment. Adjusts min and max value samples by a %.
  AMPLITUDE_ADJUSTMENT = 'amplitude_adjustment'
  # If custom wave type is specified: this template formula is used.
  # Must be a string with {variables} that will be replaced into the actual
  # values.
  CUSTOM_WAVE_FORMULA = 'custom_wave_formula'
  # Debug mode allows printing formulas and others.
  DEBUG = 'debug'
  FREQUENCY = 'frequency'
  # Max value that the wave can take. Defaults to positive Amplitude.
  MAX_WAVE_VALUE = 'max_wave_value'
  # Min value that the wave can take. Defaults to negative Amplitude.
  MIN_WAVE_VALUE = 'min_wave_value'
  # Number of frames/samples per second.
  SAMPLE_RATE = 'sample_rate'
  # Volume of the sample. Floats from 0 to 1 are recommended values.
  VOLUME = 'volume'
  # A formula that is applied to transform the wave shape. This function gets
  # applied to each sample_value at the end of the calculation process.
  # Signature must be Callable[[int], int].
  WAVE_TRANSFORMER = 'wave_transformer'


_DEFAULT_WAVE_OPTIONS = {
    # Amplitude must be always half the total range.
    SoundWaveOption.AMPLITUDE: wave_math.get_max_value_from_bytes(
        wave_settings.BYTES_OF_DATA, True) / 2,
    SoundWaveOption.AMPLITUDE_ADJUSTMENT: 1,  # 100%
    SoundWaveOption.CUSTOM_WAVE_FORMULA: '',
    SoundWaveOption.DEBUG: False,
    SoundWaveOption.FREQUENCY: 440,
    SoundWaveOption.MAX_WAVE_VALUE: wave_math.get_max_value_from_bytes(
        wave_settings.BYTES_OF_DATA, wave_settings.SIGNED_INTEGER) - 1,
    SoundWaveOption.MIN_WAVE_VALUE: wave_math.get_min_value_from_bytes(
        wave_settings.BYTES_OF_DATA, wave_settings.SIGNED_INTEGER) + 1,
    SoundWaveOption.SAMPLE_RATE: 44100,
    SoundWaveOption.VOLUME: 1,  # 100%
    SoundWaveOption.WAVE_TRANSFORMER: lambda x: x,
}


class SoundWaveType(enum.Enum):
  """Represents a Sound Wave Type(equation)."""
  SIN_WAVE = 'sin'
  X2_WAVE = 'x**2'
  RANDOM_WAVE = 'random'
  SAWTOOTH_WAVE = 'sawtooth'
  CUSTOM_WAVE = 'custom'


# Configuration of the wave options.
WaveOptions = Mapping[SoundWaveOption, Any]

# A wave function takes the frame and outputs the sample for the frame.
WaveFunction = Callable[[int], int]


class WaveSoundGenerator(object):
  """Generator of wave functions.

  Methods:
    get_wave_function: Gets a wave function that gives values for each frame.
    get_wave_sound_samples: Gets data for sound wave.
  """

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

  def _get_wave_option_value(
          self, wave_options: WaveOptions, option: SoundWaveOption) -> Any:
    """Gets the value for a given wave option, or its default value if not set.

    Args:
      wave_options: Wave configuration.
      option: Option to get from configuration.

    Raises:
      ValueError: Unknown SoundWaveOption.

    Returns:
      Config value for given wave option feature.
    """
    if option not in _DEFAULT_WAVE_OPTIONS:
      raise ValueError(f'Unknown sound wave feature: {option}')
    default_value = _DEFAULT_WAVE_OPTIONS[option]
    return wave_options.get(option, default_value)

  def _get_debug_mode(self, wave_options: WaveOptions) -> bool:
    """Gets whether to debug wave or not.

    Args:
      wave_options: Wave configuration.

    Returns:
      Whether to apply debug mode.
    """
    return self._get_wave_option_value(wave_options, SoundWaveOption.DEBUG)

  def _get_custom_wave_formula(self, wave_options: WaveOptions) -> Text:
    """Gets custom formula template for custom wave formula type.

    Args:
      wave_options: Wave configuration.

    Returns:
      Custom wave formula text template
    """
    return self._get_wave_option_value(
        wave_options, SoundWaveOption.CUSTOM_WAVE_FORMULA)

  def _get_volume(self, wave_options: WaveOptions) -> float:
    """Gets the volume based on wave options.

    Args:
      wave_options: Wave configuration.

    Returns:
      Volume.
    """
    return float(
        self._get_wave_option_value(wave_options, SoundWaveOption.VOLUME))

  def _get_wave_amplitude(self, wave_options: WaveOptions) -> int:
    """Gets the wave amplitude.

    Args:
      wave_options: Wave configuration.

    Returns:
      Wave amplitude.
    """
    wave_amplitude = self._get_wave_option_value(
        wave_options, SoundWaveOption.AMPLITUDE)
    wave_adjustment = self._get_wave_option_value(
        wave_options, SoundWaveOption.AMPLITUDE_ADJUSTMENT)
    return int(wave_amplitude * wave_adjustment)

  def _get_min_wave_value(self, wave_options: WaveOptions) -> int:
    """Gets the min value that the wave can take.

    Args:
      wave_options: Wave configuration.

    Returns:
      Min value limit for the sample value.
    """
    wave_amplitude = self._get_wave_amplitude(wave_options)
    min_allowed_value = _DEFAULT_WAVE_OPTIONS.get(
        SoundWaveOption.MIN_WAVE_VALUE)

    # Avoid overflow by limitting to the most restrictive.
    return max(-wave_amplitude, min_allowed_value)

  def _get_max_wave_value(self, wave_options: WaveOptions) -> int:
    """Gets the max value that the wave can take.

    Args:
      wave_options: Wave configuration.

    Returns:
      Max value limit for the sample value.
    """
    wave_amplitude = self._get_wave_amplitude(wave_options)
    max_allowed_value = _DEFAULT_WAVE_OPTIONS.get(
        SoundWaveOption.MAX_WAVE_VALUE)

    # Avoid overflow by limitting to the most restrictive.
    return min(wave_amplitude, max_allowed_value)

  def _get_wave_value_range(
          self, wave_options: WaveOptions) -> Tuple[int, int, int]:
    """Gets the range of values for the wave.

    Args:
      wave_options: Wave configuration.

    Returns:
     Range of values for the sample value.
    """
    min_value = self._get_min_wave_value(wave_options)
    max_value = self._get_max_wave_value(wave_options)
    return abs(min_value) + abs(max_value)

  def _get_wave_frequency(self, wave_options: WaveOptions) -> float:
    """Gets the wave frequency.

    Args:
      wave_options: Wave configuration.

    Returns:
      Wave frequency.
    """
    return self._get_wave_option_value(wave_options, SoundWaveOption.FREQUENCY)

  def _get_wave_sample_rate(self, wave_options: WaveOptions) -> int:
    """Gets the wave sample rate.

    Args:
      wave_options: Wave configuration.

    Returns:
      Wave sample rate.
    """
    return self._get_wave_option_value(
        wave_options, SoundWaveOption.SAMPLE_RATE)

  def _get_wave_transformer(self, wave_options: WaveOptions) -> WaveFunction:
    """Gets the wave transformer function.

    Args:
      wave_options: Wave configuration.

    Returns:
      Wave transformer.
    """
    return self._get_wave_option_value(
        wave_options, SoundWaveOption.WAVE_TRANSFORMER)

  def _get_samples_per_cycle(self, wave_options: WaveOptions) -> int:
    """Gets number of samples that will be generated per wave cycle.

    Args:
      wave_options: Wave configuration.

    Returns:
      Samples per cycle.
    """
    wave_frequency = self._get_wave_frequency(wave_options)
    wave_sample_rate = self._get_wave_sample_rate(wave_options)
    samples_per_cycle = int(round(wave_sample_rate / wave_frequency))
    if samples_per_cycle >= 1:
      return samples_per_cycle
    return 1

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
          wave_specific_options: Optional[SoundWaveOption] = None
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
    volume_adjustment = self._get_volume(wave_options)

    min_sample_value = self._get_min_wave_value(wave_options)
    max_sample_value = self._get_max_wave_value(wave_options)
    sample_value_range = self._get_wave_value_range(wave_options)

    samples_per_cycle = self._get_samples_per_cycle(wave_options)

    def _normalize_sample_value(sample_value: wave_math.Number) -> int:
      """Applies common normalization operations to sample value.

      Normalizations:
        - Adjust sample value by volume.
        - Limit value to a specific range.
        - Transform value to integer.
        - Applies custom wave transformer.

      Args:
        sample_value: Value of the sample.

      Returns:
        Value of the sample, after normalization opperations are applied.
      """
      sample_value = sample_value * volume_adjustment
      sample_value = wave_math.limit_value_to_range(
          sample_value, min_sample_value, max_sample_value)
      sample_value = int(sample_value)

      custom_transformer = self._get_wave_transformer(wave_options)
      sample_value = custom_transformer(sample_value)
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
        sample_value = (
            max_sample_value * math.sin(2 * math.pi * sample_frequency))
        if debug_mode:
          print(
              f'{sample_frame}: {max_sample_value} * sin(2π{sample_frequency})'
              f' = {sample_value}')
        return _normalize_sample_value(sample_value)
      return sin_sound_wave

    if sound_wave_type == SoundWaveType.SAWTOOTH_WAVE:
      def sawtooth_sound_wave(sample_frame: int) -> int:
        """Sawtooth wave function."""
        spike_cycle = int(sample_frame / sample_value_range)
        sample_value = (
            sample_frame + min_sample_value - spike_cycle * sample_value_range)
        if debug_mode:
          print(
              f'{sample_frame}: {sample_frame} + {min_sample_value} '
              f'- {spike_cycle} * {sample_value_range} = {sample_value}')
        return _normalize_sample_value(sample_value)
      return sawtooth_sound_wave

    if sound_wave_type == SoundWaveType.RANDOM_WAVE:
      def random_sound_wave(sample_frame: int) -> int:
        """Gets a random value wave."""
        random_sample = random.randint(min_sample_value, max_sample_value)
        if debug_mode:
          print(f'{sample_frame}: {random_sample}')
        return _normalize_sample_value(random_sample)
      return random_sound_wave

    if sound_wave_type == SoundWaveType.X2_WAVE:
      def x2_sound_wave(sample_frame: int) -> int:
        """Creates a sound wave with x**2 function.

        X^2 function in the shape of:
          y = a (x+b)^2 + c
        """
        a = 4 * (
            max_sample_value - min_sample_value) / (samples_per_cycle ** 2)
        b = -samples_per_cycle / 2
        c = min_sample_value
        x = sample_frame % samples_per_cycle
        sample_value = a * ((x + b) ** 2) + c
        if debug_mode:
          print(
              f'{sample_frame}: ({a} * ({x} + {b})^2 + {c}) = {sample_value}')
        return _normalize_sample_value(sample_value)
      return x2_sound_wave

    if sound_wave_type == SoundWaveType.CUSTOM_WAVE:
      def custom_sound_wave(sample_frame: int) -> int:
        """Creates a sound wave with given templated formula.

        Custom formula must be specified in:
          wave_options[SoundWaveOption.CUSTOM_WAVE_FORMULA]

        Parameters are replaced for values. Supported parameters:
          {x}: Sample frame.
          {min_sample}: Minimum value a frame can take.
          {max_sample}: Maximum value a frame can take.
          {sample_range}: Difference between max and minimum value.
          {samples_per_cycle}: Samples per cycle.
        """
        custom_formula = self._get_custom_wave_formula(wave_options)
        replaced_formula = custom_formula.format(
            x=sample_frame,
            min_sample=min_sample_value,
            max_sample=max_sample_value,
            sample_range=sample_value_range,
            samples_per_cycle=samples_per_cycle,
        )
        # This is an unsafe operation. Use and support at your own risk.
        sample_value = eval(replaced_formula)
        if debug_mode:
          print(f'{sample_frame}: {replaced_formula} = {sample_value}')
        return _normalize_sample_value(sample_value)
      return custom_sound_wave

    raise ValueError(f'Unknown wave type: {sound_wave_type}')

  def get_wave_sound_samples(
          self, duration: int, sound_wave_type: SoundWaveType,
          wave_specific_options: Optional[SoundWaveOption] = None
  ) -> array.array:
    """Gets the sound wave values for the given wave type and duration.

    Args:
      duration: Duration of the sound wave.
      sound_wave_type: Type of sound wave to generate.
      wave_specific_options: Modifiers to the specific wave.

    Returns:
      Values generated by requested sound wave for requested duration.
    """
    sound_wave_function = self.get_wave_function(
        sound_wave_type, wave_specific_options)

    wave_options = self._get_merged_wave_options(wave_specific_options)
    sample_rate = self._get_wave_sample_rate(wave_options)
    num_samples = int(duration * sample_rate)

    sound_samples = array.array('h')
    for sample_frame in range(num_samples):
      sound_sample = sound_wave_function(sample_frame)
      sound_samples.append(sound_sample)
    return sound_samples
