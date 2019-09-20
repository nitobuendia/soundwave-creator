"""Creates sound wave files."""

import array
import enum
import math
import wave
import wave_functions
from typing import Any, Callable, Mapping, Optional, Text

# 2 bytes because of using signed short integers => bit depth = 16
_DATA_SIZE = 2

# Number of channels (1: mono, 2: stereo).
_NUMBER_CHANNELS = 1


def create_sound_wave_file(
        duration: int,
        sound_wave_file_name: Text,
        sound_wave_type: wave_functions.SoundWaveType,
        wave_options: Optional[wave_functions.WaveOptions] = None
) -> wave.Wave_write:
  """Creates a soundwave representation.

  Args:
    duration: Seconds of duration of the wave.
    sound_wave_file_name: Name of the sound wave to create.
    sound_wave_type: Formula to use for the soundwave.
    wave_options: Configuration of the sound wave.

  Raises:
    ValueError: sound wave unknown.

  Returns:
    Array representing the sound wave.
  """
  sound_wave_generator = (
      wave_functions.SOUND_WAVE_FUNCTION_MAP.get(sound_wave_type))
  if not sound_wave_generator:
    raise ValueError(f'Unknown wave type: {sound_wave_type}')

  sound_wave_function = sound_wave_generator(wave_options)

  num_samples = int(duration * wave_functions._DEFAULT_SAMPLE_RATE)
  sound_samples = _create_sound_sample(sound_wave_function, num_samples)

  sound_file = _create_sound_file(sound_wave_file_name, sound_samples)
  return sound_file


def _create_sound_sample(
        sound_wave_function: wave_functions.WaveFunction,
        num_samples: int) -> array.array:
  """Gets a sound sample based on a wave function.

  Args:
    sound_wave_function: Function used to generate the sound.
    num_samples: Number of samples to take from wave function.

  Returns:
    Array of sound samples for given sound wave function.
  """
  sound_samples = array.array('h')
  for sample_frame in range(num_samples):
    sound_sample = sound_wave_function(sample_frame)
    sound_samples.append(sound_sample)
  return sound_samples


def _create_sound_file(
        sound_wave_file_name: Text,
        sound_samples: array.array) -> wave.Wave_write:
  """Creates a sound file based on the provided sound samples.

  Args:
    sound_wave_file_name: Name of the sound wave file to create.
    sound_samples: Sound samples to write to file.

  Returns:
    Sound file.
  """
  sound_file = wave.open(sound_wave_file_name, 'w')
  sound_file.setparams(
      (_NUMBER_CHANNELS, _DATA_SIZE, wave_functions._DEFAULT_SAMPLE_RATE,
       len(sound_samples), "NONE", "Uncompressed"))
  sound_file.writeframes(sound_samples.tobytes())
  sound_file.close()
  return sound_file
