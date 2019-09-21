"""Creates sound wave files."""

import array
import wave
import wave_settings
from typing import Text


# Number of channels (1: mono, 2: stereo).
_NUMBER_CHANNELS = 1
_DEFAULT_COMPRESSION_TYPE = 'NONE'
_DEFAULT_COMPRESSION_NAME = 'Uncompressed'


def create_sound_file(
        sound_wave_file_name: Text,
        duration: int,
        sound_samples: array.array) -> wave.Wave_write:
  """Creates a sound file based on the provided sound samples.

  Args:
    sound_wave_file_name: Name of the sound wave file to create.
    duration: Duration of the file in seconds.
    sound_samples: Sound samples to write to file.

  Returns:
    Sound file.
  """
  number_channels = _NUMBER_CHANNELS
  sample_width = wave_settings.BYTES_OF_DATA
  number_samples = len(sound_samples)
  sample_rate = int(number_samples / duration)
  compression_type = _DEFAULT_COMPRESSION_TYPE
  compression_name = _DEFAULT_COMPRESSION_NAME

  sound_params = (number_channels, sample_width, sample_rate,
                  number_samples, compression_type, compression_name)

  sound_file = wave.open(sound_wave_file_name, 'w')
  sound_file.setparams(sound_params)
  sound_file.writeframes(sound_samples.tobytes())
  sound_file.close()
  return sound_file
