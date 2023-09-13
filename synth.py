# Formerly the prototypical file, synth. Now it's just a graveyard of functions that may never return?
from pydub import AudioSegment


import concurrent.futures
from utils import get_output_path


# This function was intended to run with multiprocessing, but Coqui won't play nice with that.
def dub_task(sub, i):
	print(f"{i}/{len(subs_adjusted)}")
	try:
		return dub_line_ram(sub)
		# empty_audio = empty_audio.overlay(line, sub.start*1000) 
	except Exception as e:
		print(e)
		with open(f"output/errors/{i}-rip.txt", 'w') as f:
			f.write(e)
		# total_errors += 1

# This may be used for multithreading?
def combine_segments():
	empty_audio = AudioSegment.silent(total_duration * 1000, frame_rate=22050)
	total_errors = 0
	for sub in subs_adjusted:
		print(f"{sub.index}/{len(subs_adjusted)}")
		try:
			segment = AudioSegment.from_file(f'output/files/{sub.index}.wav')
			empty_audio = empty_audio.overlay(segment, sub.start*1000)
		except:
			total_errors += 1
	empty_audio.export('new.wav')
	print(total_errors)
