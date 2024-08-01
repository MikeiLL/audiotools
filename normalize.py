import os
import sys
import logging
import subprocess
import pydub

# Do we want to normalize?
if len(sys.argv) < 2:
  print("Usage: %s <normalize|check> srcdir (defaults to cwd)" % sys.argv[0])
  sys.exit(1)

# l = logging.getLogger("pydub.converter")
# l.setLevel(logging.DEBUG)
# l.addHandler(logging.StreamHandler())
src_dir = sys.argv[2] if len(sys.argv) > 2 else '.'
print("Checking files in %s" % src_dir)
audio_files = [f for f in os.listdir(src_dir) if f.endswith('.aif')]
target_dBFS = -12.0
for fn in audio_files:
  try:
    audio = pydub.AudioSegment.from_file(src_dir + "/" + fn)
    print("%s: %.2f dB (max %.2f)" % (fn, audio.dBFS, audio.max_dBFS))
    if sys.argv[1] == 'check':
      continue
    if not os.path.exists(src_dir + "/" + 'normalized'):
      os.makedirs(src_dir + "/" + 'normalized')
    if audio.dBFS < target_dBFS:
      print("%s: Low level. Increasing by %f to %f" % (fn, target_dBFS - audio.dBFS, target_dBFS))
      subprocess.call(['ffmpeg', '-y', '-i', src_dir + "/" + fn, '-af', 'volume=%fdB' % (target_dBFS - audio.dBFS), src_dir + "/" + 'normalized/%s' % fn])
    elif audio.dBFS > target_dBFS:
      print("%s: High level" % fn)

  except pydub.exceptions.CouldntDecodeError:
    print("%s: Couldn't decode" % fn)
