import srt
from TTS.api import TTS
import ffmpeg
import ass
import threading

start_line = 114-1

end_line = start_line + 10

# stream = ffmpeg.input("./saiki.mkv")

tts = TTS(TTS.list_models()[10])
# for index, model in enumerate(TTS.list_models()):
# 	print(index, model)
tts.tts_to_file("This do be a test!", file_path="owo.wav")

raw_subs = ""
with open("out.srt","r") as f:
	raw_subs = srt.parse(f.read())

lines = list(raw_subs)[start_line:end_line]

def tts_thread(text, filename):
	tts.tts_to_file(text, file_path=filename)

tts_threads = []
for index, line in enumerate(lines):
	threading.Thread(target=tts_thread, args=[line.content, f"files/{index}.wav"]).start()