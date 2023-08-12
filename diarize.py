# 1. visit hf.co/pyannote/speaker-diarization and accept user conditions
# 2. visit hf.co/pyannote/segmentation and accept user conditions
# 3. visit hf.co/settings/tokens to create an access token
# 4. instantiate pretrained speaker diarization pipeline
from pyannote.audio import Pipeline
import ffmpeg

# ffmpeg -i .\saiki.mkv -vn -ss 84 -to 1325 crop.wav

# audio = ffmpeg.input("saiki.mkv")
# crop = ffmpeg.trim(audio, start="00:01:24", end="00:22:05")
# out = ffmpeg.output(crop.audio, "crop.wav")
# ffmpeg.run(out)


# pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization@2.1",
									use_auth_token="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")

# # apply the pipeline to an audio file
diarization = pipeline("crop.wav")

for turn, _, speaker in diarization.itertracks(yield_label=True):
    print(f"start={turn.start:.1f}s stop={turn.end:.1f}s speaker_{speaker}")
# # start=0.2s stop=1.5s speaker_0

with open("audio.rttm", "w") as rttm:
    diarization.write_rttm(rttm)