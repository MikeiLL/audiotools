import os
import sys
import logging
import subprocess
import pydub
import ffmpeg_normalize

# Do we want to normalize?
if len(sys.argv) < 2:
  print("Usage: %s <normalize|check> srcdir (defaults to cwd)" % sys.argv[0])
  sys.exit(1)

normalizer = ffmpeg_normalize.FFmpegNormalize(target_level=-14)
# l = logging.getLogger("pydub.converter")
# l.setLevel(logging.DEBUG)
# l.addHandler(logging.StreamHandler())
src_dir = sys.argv[2] if len(sys.argv) > 2 else '.'
audio_files = [f for f in os.listdir(src_dir) if f.endswith('.aif')]
target_dBFS = -14.0

if sys.argv[1] == 'check':
  print("Checking files in %s" % src_dir)

if sys.argv[1] == 'normalize':
  if not os.path.exists(src_dir + "/" + 'normalized/boosted'):
    os.makedirs(src_dir + "/" + 'normalized/boosted')

for fn in audio_files:
  if sys.argv[1] == 'check':
    audio = pydub.AudioSegment.from_file(src_dir + "/" + fn)
    print("%s: %.2f dB (max %.2f)" % (fn, audio.dBFS, audio.max_dBFS))
    continue
  try:
    normalizer.add_media_file(src_dir + "/" + fn, src_dir + "/" + 'normalized/%s' % fn)
    print("Normalizing %s" % fn)
    normalizer.run_normalization()
    try:
      audio = pydub.AudioSegment.from_file(src_dir + "/" + 'normalized/%s' % fn)
      print("%s: %.2f dB (max %.2f)" % (fn, audio.dBFS, audio.max_dBFS))
      if audio.dBFS < target_dBFS:
        print("%s: Low level. Increasing by %f to %f" % (fn, target_dBFS - audio.dBFS, target_dBFS))
        subprocess.call(['ffmpeg', '-y', '-i', src_dir + "/" + 'normalized/%s' % fn, '-af', 'volume=%fdB' % (target_dBFS - audio.dBFS), src_dir + "/" + 'normalized/boosted/%s' % fn])
      elif audio.dBFS > target_dBFS:
        print("%s: High level" % fn)

    except pydub.exceptions.CouldntDecodeError:
      print("%s: Couldn't decode" % fn)
  except ffmpeg_normalize.FFmpegNormalizeError:
    print("Error normalizing %s" % fn)
    continue
