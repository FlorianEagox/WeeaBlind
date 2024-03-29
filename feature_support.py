import os
import sys
import importlib.util
import static_ffmpeg
import subprocess
from utils import get_output_path

def is_module_available(module_name):
	try:
		return importlib.util.find_spec(module_name) is not None
	except Exception as e:
		print(f"failed to import {module_name}: {e}")
		return False

def is_executable(program):
	try:
		subprocess.run([program, "-version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
		return True
	except Exception as e:
		print(program, e)
		return False

def check_ffmpeg():
	# First we'll check if FFmpeg was installed automatically by weeablind, a "crumb" will be left behind if so
	ffmpeg_path = get_output_path('', '', path='ffmpeg')
	if os.path.exists(os.path.join(ffmpeg_path, 'installed.crumb')):
		# The dir with the ffmpeg binary will be named based dont he platform, and we need to know wthis to locate it
		os.environ["PATH"] = os.pathsep.join([os.path.join(ffmpeg_path, sys.platform), os.environ["PATH"]])
	return is_executable("ffmpeg")

ffmpeg_supported = check_ffmpeg() # "ffmpeg" in os.getenv('PATH').lower()
diarization_supported = is_module_available("pyannote")
ocr_supported = is_module_available("video_ocr")
nostril_supported = is_module_available("nostril")
language_detection_supported = is_module_available("speechbrain")
vocal_isolation_supported = is_module_available("spleeter")
downloads_supported = is_module_available("yt-dlp")
espeak_supported = is_module_available("espeakng") and (is_executable("espeak") or is_executable("espeakng"))
coqui_supported = False # is_module_available("TTS") # and espeak_supported
torch_supported = is_module_available("torch")
gpu_supported = False
if torch_supported:
	from torch.cuda import is_available
	gpu_supported = is_available()
# TESTING
# language_detection_supported = coqui_supported = False

def install_ffmpeg():
	static_ffmpeg.add_paths(False, get_output_path('', '', path='ffmpeg'))
	check_ffmpeg()
