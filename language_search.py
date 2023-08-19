import langid

# Load the WAV audio file
audio_file = '~/Music/vaporeon.wav'

# Read audio data and convert to text (if needed)
# audio_text = ...  # Process audio to text if required

# Perform language identification
lang, _ = langid.classify(audio_text)

# Check if the identified language is English
if lang == 'en':
    print("The audio contains English speech.")
else:
    print("The audio is likely not in English.")
