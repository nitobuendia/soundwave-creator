"""Creates a sound wave file and its wave graph."""

import time
import wave_creator
import wave_generator
import wave_plotter


_SOUND_FILE_NAME = 'sounds/sound.wav'
_FILE_DURATION = 3  # In seconds.

_SOUND_WAVE_OPTIONS = {
    wave_generator.SoundWaveOption.CUSTOM_WAVE_FORMULA: (
        '({x} + {min_sample}) / {max_sample}'),
    wave_generator.SoundWaveOption.WAVE_TRANSFORMER: lambda x: int(x / 5),
    wave_generator.SoundWaveOption.DEBUG: False,
    wave_generator.SoundWaveOption.FREQUENCY: 440,
}

_FILE_OPTIONS = {
    wave_creator.SoundFileOption.FILE_NAME: _SOUND_FILE_NAME,
}

_SOUND_WAVE_GRAPH_TYPE = wave_plotter.WaveGraphType.PER_FRAME


if __name__ == "__main__":
  wave_sound_generator = wave_generator.WaveSoundGenerator(_SOUND_WAVE_OPTIONS)

  wave_types = [
      wave_generator.SoundWaveType.X2_WAVE,
      wave_generator.SoundWaveType.SIN_WAVE,
      wave_generator.SoundWaveType.RANDOM_WAVE,
      wave_generator.SoundWaveType.CUSTOM_WAVE,
  ]

  channels_data = [
      wave_sound_generator.get_wave_sound_samples(_FILE_DURATION, wave_type)
      for wave_type in wave_types
  ]

  wave_creator.create_sound_file(_FILE_DURATION, channels_data, _FILE_OPTIONS)

  wave_plotter.create_sound_wave_graph(
      _SOUND_FILE_NAME, _SOUND_WAVE_GRAPH_TYPE)
