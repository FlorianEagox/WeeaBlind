# This is used to detect the spoken language in an audio file
# I wanted to abstract it to it's own file, just like vocal isolation & diarization
import feature_support
if feature_support.language_detection_supported:
	from speechbrain.inference.classifiers import EncoderClassifier

language_identifier_model = None

def detect_language(file):
	global language_identifier_model
	if not language_identifier_model:
		language_identifier_model = EncoderClassifier.from_hparams(source="speechbrain/lang-id-voxlingua107-ecapa", savedir="tmp") #, run_opts={"device":"cuda"})
	signal = language_identifier_model.load_audio(file)
	prediction = language_identifier_model.classify_batch(signal)
	return prediction[3][0].split(' ')[1]
