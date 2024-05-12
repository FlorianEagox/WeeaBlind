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
		subprocess.run(program, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, check=True)
		return True
	except Exception as e:
		return False

def check_ffmpeg():
	# First we'll check if FFmpeg was installed automatically by weeablind, a "crumb" will be left behind if so
	ffmpeg_path = get_output_path('', '', path='ffmpeg')
	if os.path.exists(os.path.join(ffmpeg_path, 'installed.crumb')):
		# The dir with the ffmpeg binary will be named based dont he platform, and we need to know wthis to locate it
		os.environ["PATH"] = os.pathsep.join([os.path.join(ffmpeg_path, sys.platform), os.environ["PATH"]])
	return is_executable(["ffmpeg", "-version"])

ffmpeg_supported = check_ffmpeg() # "ffmpeg" in os.getenv('PATH').lower()
diarization_supported = is_module_available("pyannote")
ocr_supported = is_module_available("video_ocr")
nostril_supported = is_module_available("nostril")
language_detection_supported = is_module_available("speechbrain")
vocal_isolation_supported = is_module_available("spleeter")
downloads_supported = is_module_available("yt_dlp")
espeak_supported = is_module_available("espeakng") and (is_executable(["espeak", "--version"]) or is_executable(["espeak-ng", "--version"]))
coqui_supported = is_module_available("TTS") # and espeak_supported
torch_supported = is_module_available("torch.cuda")
gpu_supported = False
if torch_supported:
	from torch.cuda import is_available
	gpu_supported = is_available()
# TESTING
# language_detection_supported = coqui_supported = False

def install_ffmpeg():
	static_ffmpeg.add_paths(False, get_output_path('', '', path='ffmpeg'))
	check_ffmpeg()

# Windows has some voices PyTTSx3 can't access for some reason unless you add them to a different part of the registry, so this will try to do that
def patch_onecore_voices():
	import win32security
	import win32api

	old_path = r"SOFTWARE\Microsoft\Speech_OneCore\Voices\Tokens"

	priv_flags = win32security.TOKEN_ADJUST_PRIVILEGES | win32security.TOKEN_QUERY
	hToken = win32security.OpenProcessToken (win32api.GetCurrentProcess (), priv_flags)
	privilege_id = win32security.LookupPrivilegeValue (None, "SeBackupPrivilege")
	win32security.AdjustTokenPrivileges (hToken, 0, [(privilege_id, win32security.SE_PRIVILEGE_ENABLED)])

	backup_path = get_output_path("onecore", ".reg")
	
	try:
		subprocess.run(["reg", "export", f"HKEY_LOCAL_MACHINE\\{old_path}", backup_path, "-y"], check=True)
		# winreg.SaveKey(key, backup_path)
	except PermissionError as e:
		print("Permission denied. Please run the script with admin privileges.", e)
		return

	# Replace the old path with the new path in the exported .reg file
	with open(backup_path, 'r', encoding='utf-16') as f:
		reg_data = f.read()

	reg_data = reg_data.replace("_OneCore", "")

	# Write the modified .reg file
	modified_data_path = get_output_path("modified_tokens", ".reg")
	with open(modified_data_path, 'w', encoding='utf-16') as f:
		f.write(reg_data)

	# Import the modified .reg file to update the registry
	os.system("regedit /s " + modified_data_path)
	print("Registry modification complete.")
