"""Creates a sound wave file and its wave graph."""

import time
import wave_creator
import wave_generator
import wave_plotter


_SOUND_FILE_NAME = 'sounds/sound.wav'
_SOUND_DURATION_IN_SECONDS = 3

_SOUND_WAVE_OPTIONS = {
    wave_generator.SoundWaveOption.DEBUG: False,
    wave_generator.SoundWaveOption.FREQUENCY: 440,
}

_FILE_OPTIONS = {
    wave_creator.SoundFileOption.FILE_NAME: _SOUND_FILE_NAME,
}

_SOUND_WAVE_GRAPH_TYPE = wave_plotter.WaveGraphType.PER_FRAME


if __name__ == "__main__":
  wave_sound_generator = wave_generator.WaveSoundGenerator(_SOUND_WAVE_OPTIONS)

  first_wave_type = wave_generator.SoundWaveType.X2_WAVE
  sound_wave_data = wave_sound_generator.get_wave_sound_samples(
      _SOUND_DURATION_IN_SECONDS, first_wave_type)

  wave_creator.create_sound_file(
      _SOUND_DURATION_IN_SECONDS, sound_wave_data, _FILE_OPTIONS)

  wave_plotter.create_sound_wave_graph(
      _SOUND_FILE_NAME, _SOUND_WAVE_GRAPH_TYPE)
