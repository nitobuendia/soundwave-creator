"""Creates a sound wave file and its wave graph."""

import time
import wave_creator
import wave_generator
import wave_plotter


_SOUND_FILE_NAME = 'sounds/sound.wav'
_SOUND_DURATION_IN_SECONDS = 3
_SOUND_WAVE_TYPE = wave_generator.SoundWaveType.SIN_WAVE
_SOUND_WAVE_OPTIONS = {
    wave_generator.SoundWaveOption.DEBUG: False,
}
_SOUND_WAVE_GRAPH_TYPE = wave_plotter.WaveGraphType.PER_FRAME


if __name__ == "__main__":
  wave_sound_generator = wave_generator.WaveSoundGenerator()

  sound_wave_data = wave_sound_generator.get_wave_sound_samples(
      _SOUND_DURATION_IN_SECONDS, _SOUND_WAVE_TYPE, _SOUND_WAVE_OPTIONS)

  wave_creator.create_sound_file(
      _SOUND_FILE_NAME, _SOUND_DURATION_IN_SECONDS, sound_wave_data)

  wave_plotter.create_sound_wave_graph(
      _SOUND_FILE_NAME, _SOUND_WAVE_GRAPH_TYPE)
