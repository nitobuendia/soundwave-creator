"""Creates sound wave files."""

import array
import enum
import wave
import wave_settings
from typing import Any, Iterable, Mapping, Text, Union


class SoundFileOption(enum.Enum):
  """Sound wave file configurations."""
  COMPRESSION_TYPE = 'compression_type'
  COMPRESSION_NAME = 'compression_name'
  FILE_NAME = 'file_name'


_DEFAULT_FILE_OPTIONS = {
    SoundFileOption.COMPRESSION_TYPE: 'NONE',
    SoundFileOption.COMPRESSION_NAME: 'Uncompressed',
    SoundFileOption.FILE_NAME: 'sound.wav',
}

SoundFileOptions = Mapping[SoundFileOption, Any]


def _get_file_option_value(
        file_options: SoundFileOptions, option: SoundFileOption) -> Any:
  """Gets the value for a given file option, or its default value if not set.

  Args:
    file_options: File configuration.
    option: Option to get from configuration.

  Raises:
    ValueError: Unknown SoundFileOption.

  Returns:
    Config value for given wave option feature.
  """
  if option not in _DEFAULT_FILE_OPTIONS:
    raise ValueError(f'Unknown file feature: {option}')
  default_value = _DEFAULT_FILE_OPTIONS[option]
  return file_options.get(option, default_value)


def create_sound_file(
        duration: int,
        channels_data: Iterable[array.array],
        file_options: SoundFileOptions) -> wave.Wave_write:
  """Creates a sound file based on the provided sound samples.

  Args:
    duration: Duration of the file in seconds.
    channels_data: Sound samples to write to each channel.
    file_options: File configuration.

  Raises:
    ValueError: channels_data must be an iterable of size >1.

  Returns:
    Sound file.
  """
  if not channels_data:
    raise ValueError('Must provide samples for at least one channel.')

  file_options = file_options or {}

  file_name = _get_file_option_value(file_options, SoundFileOption.FILE_NAME)
  sound_file = wave.open(file_name, 'w')

  number_channels = len(channels_data)
  sample_width = wave_settings.BYTES_OF_DATA
  first_sample = channels_data[0]
  number_samples = len(first_sample)
  sample_rate = int(number_samples / duration)
  compression_type = _get_file_option_value(
      file_options, SoundFileOption.COMPRESSION_TYPE)
  compression_name = _get_file_option_value(
      file_options, SoundFileOption.COMPRESSION_NAME)

  sound_params = (number_channels, sample_width, sample_rate,
                  number_samples, compression_type, compression_name)
  sound_file.setparams(sound_params)

  mixed_sound_sample = array.array('h')
  for keyframe in range(0, number_samples):
    sample_total = 0
    for channel in range(0, number_channels):
      sample_total += channels_data[channel][keyframe]
    mixed_sound_frame = int(sample_total / number_channels)
    mixed_sound_sample.append(mixed_sound_frame)

  sound_file.writeframes(mixed_sound_sample.tobytes())
  sound_file.close()
  return sound_file
