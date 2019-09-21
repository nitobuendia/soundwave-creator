"""Creates sound wave files."""

import array
import enum
import wave
import wave_settings
from typing import Any, Mapping, Text, Union


# Number of channels (1: mono, 2: stereo).
_NUMBER_CHANNELS = 1


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
        sound_samples: array.array,
        file_options: SoundFileOptions) -> wave.Wave_write:
  """Creates a sound file based on the provided sound samples.

  Args:
    file_name: Name of the sound wave file to create.
    duration: Duration of the file in seconds.
    sound_samples: Sound samples to write to file.
    file_options: File configuration.

  Returns:
    Sound file.
  """
  file_options = file_options or {}
  file_name = _get_file_option_value(file_options, SoundFileOption.FILE_NAME)
  compression_type = _get_file_option_value(
      file_options, SoundFileOption.COMPRESSION_TYPE)
  compression_name = _get_file_option_value(
      file_options, SoundFileOption.COMPRESSION_NAME)

  sample_width = wave_settings.BYTES_OF_DATA

  number_samples = len(sound_samples)
  sample_rate = int(number_samples / duration)
  number_channels = _NUMBER_CHANNELS

  sound_params = (number_channels, sample_width, sample_rate,
                  number_samples, compression_type, compression_name)

  sound_file = wave.open(file_name, 'w')
  sound_file.setparams(sound_params)
  sound_file.writeframes(sound_samples.tobytes())
  sound_file.close()
  return sound_file
