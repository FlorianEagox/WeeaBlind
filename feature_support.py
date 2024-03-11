import os

import importlib.util

def is_module_available(module_name):
    try:
        return importlib.util.find_spec(module_name) is not None
    except Exception as e:
        print(f"failed to import {module_name}: {e}")
        return False

ffmpeg_supported = "ffmpeg" in os.getenv('PATH').lower()
diarization_supported = is_module_available("pyannote")
ocr_supported = is_module_available("video_ocr")
nostril_supported = is_module_available("nostril")
language_detection_supported = is_module_available("speechbrain")
vocal_isolation_supported = is_module_available("spleeter")
downloads_supported = is_module_available("yt-dlp")
espeak_supported = "espeak" in os.getenv('PATH').lower()
coqui_supported = is_module_available("TTS") # and espeak_supported
torch_supported = is_module_available("torch")
gpu_supported = False
if torch_supported:
    from torch.cuda import is_available
    gpu_supported = is_available()
# TESTING
# language_detection_supported = coqui_supported = False
