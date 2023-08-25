from dataclasses import dataclass
from Voice import Voice
import ffmpeg
import synth
import srt
from re import compile, sub as substitute

remove_xml = compile(r'<[^>]+>|\{[^}]+\}')

@dataclass
class DubbedLine:
	start: float
	end: float
	text: str
	voice: Voice

def load_subs(imported=False):
	export = synth.get_output_path(synth.current_file, '.srt')
	if imported:
		(
			ffmpeg
			.input(export)
			.output(export)
			.global_args('-loglevel', 'error')
			.run(overwrite_output=True)
		)
	with open(export, "r") as f:
		subs = list(srt.parse(f.read()))
		for sub in subs:
			synth.subs_adjusted.append(DubbedLine(
				sub.start,
				sub.end,
				substitute(remove_xml, '', sub.content)
			))
		return subs
