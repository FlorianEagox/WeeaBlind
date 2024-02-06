from Voice import Voice
import feature_support

video = None
if feature_support.coqui_supported:
    speakers = [Voice(Voice.VoiceType.COQUI, name="Sample")]
else:
    speakers = [Voice(Voice.VoiceType.SYSTEM, name="Sample")]
speakers[0].set_voice_params('tts_models/en/vctk/vits', 'p326') # p340
current_speaker = speakers[0]
sample_speaker = current_speaker
