"""Creates a sound wave file and its wave graph."""

import time
import wave_creator
import wave_functions
import wave_plotter


_SOUND_FILE_NAME = 'sounds/sound.wav'
_SOUND_DURATION_IN_SECONDS = 3
_SOUND_WAVE_TYPE = wave_functions.SoundWaveType.SPIKE_WAVE
_SOUND_WAVE_GRAPH_TYPE = wave_plotter.WaveGraphType.PER_SECOND

if __name__ == "__main__":
  wave_creator.create_sound_wave_file(
      _SOUND_DURATION_IN_SECONDS, _SOUND_FILE_NAME, _SOUND_WAVE_TYPE)

  wave_plotter.create_sound_wave_graph(
      _SOUND_FILE_NAME, _SOUND_WAVE_GRAPH_TYPE)
