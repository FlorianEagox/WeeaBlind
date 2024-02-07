import os

import importlib.util

def is_module_available(module_name):
    return importlib.util.find_spec(module_name) is not None


ffmpeg_supported = "ffmpeg" in os.getenv('PATH').lower()
diarization_supported = is_module_available("pyannote.audio")
ocr_supported = is_module_available("video_ocr")
language_detection_supported = is_module_available("speechbrain")
vocal_isolation_supported = is_module_available("spleeter")
downloads_supported = is_module_available("yt-dlp")
espeak_supported = "espeak" in os.getenv('PATH').lower()
coqui_supported = is_module_available("TTS") # and espeak_supported

# TESTING
# language_detection_supported = coqui_supported = False
