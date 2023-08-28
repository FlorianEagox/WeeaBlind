from dataclasses import dataclass
from Voice import Voice
import ffmpeg
# from synth import get_output_path, current_file
import srt
from re import compile, sub as substitute

remove_xml = compile(r'<[^>]+>|\{[^}]+\}')

@dataclass
class DubbedLine:
	start: float
	end: float
	text: str
	index: int
	voice: Voice = 0


def load_subs(import_path=False, export=""):
	# export = get_output_path(current_file, '.srt')
	if import_path: # For importing an external subtitles file
		(
			ffmpeg
			.input(import_path)
			.output(export)
			.global_args('-loglevel', 'error')
			.run(overwrite_output=True)
		)
	with open(export, "r") as f:
		original_subs = list(srt.parse(f.read()))
		return [
			DubbedLine(
				sub.start.total_seconds(),
				sub.end.total_seconds(),
				substitute(remove_xml, '', sub.content),
				sub.index
			)
			for sub in original_subs
		]
