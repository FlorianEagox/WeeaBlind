import os

import importlib.util
import static_ffmpeg
import subprocess

def is_module_available(module_name):
	try:
		return importlib.util.find_spec(module_name) is not None
	except Exception as e:
		print(f"failed to import {module_name}: {e}")
		return False

def check_ffmpeg():
	try:
		subprocess.run(['ffmpeg', '-version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
		return True
	except:
		return False

ffmpeg_supported = check_ffmpeg() # "ffmpeg" in os.getenv('PATH').lower()
diarization_supported = is_module_available("pyannote")
ocr_supported = is_module_available("video_ocr")
nostril_supported = is_module_available("nostril")
language_detection_supported = is_module_available("speechbrain")
vocal_isolation_supported = is_module_available("spleeter")
downloads_supported = is_module_available("yt-dlp")
espeak_supported = "espeak" in os.getenv('PATH').lower()
coqui_supported = False # is_module_available("TTS") # and espeak_supported
torch_supported = is_module_available("torch")
gpu_supported = False
if torch_supported:
	from torch.cuda import is_available
	gpu_supported = is_available()
# TESTING
# language_detection_supported = coqui_supported = False

def install_ffmpeg():
	# static_ffmpeg._add_paths.get_or_fetch_platform_executables_else_raise(True)
	return static_ffmpeg.add_paths(True)