import os
import pydub
import logging
import subprocess

l = logging.getLogger("pydub.converter")
l.setLevel(logging.DEBUG)
l.addHandler(logging.StreamHandler())
audio_files = [f for f in os.listdir() if f.endswith('.aif')]
target_dBFS = -12.0
for fn in audio_files:
  try:
    audio = pydub.AudioSegment.from_file(fn)
    print("%s: %.2f dB (max %.2f)" % (fn, audio.dBFS, audio.max_dBFS))
    if audio.dBFS < target_dBFS:
      print("%s: Low level. Increasing by %f to %f" % (fn, target_dBFS - audio.dBFS, target_dBFS))
      subprocess.call(['ffmpeg', '-y', '-i', fn, '-af', 'volume=%fdB' % (target_dBFS - audio.dBFS), 'normalized-%s' % fn])
    elif audio.dBFS > target_dBFS:
      print("%s: High level" % fn)

  except pydub.exceptions.CouldntDecodeError:
    print("%s: Couldn't decode" % fn)
