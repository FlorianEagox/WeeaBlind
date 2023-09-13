from Voice import Voice

video = None
speakers = [Voice(Voice.VoiceType.COQUI, name="Sample")]
speakers[0].set_voice_params('tts_models/en/vctk/vits', 'p326') # p340
current_speaker = speakers[0]
sample_speaker = current_speaker
