from Voice import Voice
import feature_support
from video import Video
import sys

platform = sys.platform
video: Video = None
if feature_support.coqui_supported:
    speakers = [Voice(Voice.VoiceType.COQUI, name="Sample")]
    speakers[0].set_voice_params('tts_models/en/vctk/vits', 'p326') # p340
else:
    speakers = [Voice(Voice.VoiceType.SYSTEM, name="Sample")]
current_speaker = speakers[0] 
sample_speaker = current_speaker
