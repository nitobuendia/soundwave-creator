"""Plots sound waves."""

import enum
from matplotlib import pyplot
import numpy as np
import wave

from typing import Text


class WaveGraphType(enum.Enum):
  """Type of graph to plot."""
  PER_FRAME = 'frame'
  PER_SECOND = 'seconds'


def _get_image_file_name(sound_wave_file_name: Text) -> Text:
  """Gets a PNG file name for given sound wave file name.

  Args:
    sound_wave_file_name: Sound wave file name.

  Returns:
    Image file name.
  """
  return sound_wave_file_name.replace('.wav', '.png')


def create_sound_wave_graph(sound_wave_file_name: Text,
                            wave_graph_type: WaveGraphType):
  """Creates a wave graph for given sound wav file.

  Args:
    sound_wave_file_name: Wav file to plot.
    wave_graph_type: Type of plot to create.
  """
  sound_wave_file = wave.open(sound_wave_file_name, 'r')

  if sound_wave_file.getnchannels() == 2:  # 2 is stereo.
    raise ValueError('Just mono files')

  pyplot.figure(1)
  pyplot.title('Signal Wave...')

  signal = sound_wave_file.readframes(-1)
  signal = np.fromstring(signal, 'Int16')

  channels = [[] for channel in range(sound_wave_file.getnchannels())]
  for index, datum in enumerate(signal):
    channels[index % len(channels)].append(datum)

  frame_rate = sound_wave_file.getframerate()
  Time = np.linspace(0, frame_rate * len(signal) / len(channels),
                     num=len(signal) / len(channels))

  for channel in channels:
    if wave_graph_type == WaveGraphType.PER_SECOND:
      pyplot.plot(Time, channel)
    elif wave_graph_type == WaveGraphType.PER_FRAME:
      pyplot.plot(channel)
    else:
      raise ValueError(f'Unsupported graph type: {wave_graph_type}.')

  wave_graph_file_name = _get_image_file_name(sound_wave_file_name)
  pyplot.savefig(wave_graph_file_name)
