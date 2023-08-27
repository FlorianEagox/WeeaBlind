# Weeablind

A program to dub multi-lingual media and anime using modern AI speech synthesis, diarization, language identification, and voice cloning.

## Why

Many shows, movies, news segments, interviews, and videos will never recieve proper dubs to other languages, and dubbing something from scratch can be an enormous undertaking. This presents a common accesiblity hurdle for people with blindness, dyslexia, learning disabilities, or simply folks that don't enjoy reading subtitles. This program aims to create a pleasant alternative for folks facing these struggles. 

This software is a product of war. My sister turned me onto my now-favorite comedy anime "The Disastrous Life of Saiki K." but Netflix never ordered a dub for the 2nd season. I'm blind and cannot and will not ever be able to read subtitles, but I MUST know how the story progresses! Netflix has forced my hand and I will bring AI-dubbed anime to the blind!

## How

This project relies on some rudimentary slapping together of some state of the art technologies. It uses numerous audio processing libraries and techniques to analyze and synthesize speech that tries to stay in-line with the source video file. It primarily relies on ffmpeg and pydub for audio and video editing, Coqui TTS for speech synthesis, speechbrain for language identification, and pyannote.audio for speaker diarization.

You have the option of dubbing every subtitle in the video, setting the s tart and end times, dubbing only foreign-language content, or fullblown multi-speaker dubbing with speaking rate and volume matching.

## When?

This project is currently what some might call in alpha. The major, core functionality is in place, and it's possible to use by cloning the repo, but it's only starting to be ready for a first release. There are numerous optimizations, UX, and refactoring that need to be done before a first release candidate. Stay tuned for regular updates, and feel free to extend a hand with contributions, testing, or suggestions if this is something you're interested in.

## The Name

I had the idea to call the software Weeablind as a portmantaue of Weeaboo (someone a little too obsessed with anime), and blind. I might change it to something else in the future like Blindtaku, DubHub, or something similar and more catchy because the software can be used for far more than just anime.

## Things to do:
- GUI tab to list and select audio / subtitle streams w/ FFMPEG
- ~~Move the tabs into their own classes~~
- Add labels and screen reader landmarks to all the controls
- Single speaker or multispeaker control switch~~
- ~~Download YouTube video with Closed Captions~~
- ~~GUI to select start and end time for dubbing~~
- Use OCR to generate subtitles for videos that don't have sub streams
- Use OCR for non-text based subtitles
- Make a cool logo?
- Learn how to package python programs as binaries to make releases
- Remove the copyrighted content from this repo (sorry not sorry TV Tokyo)
- Save and import config files for later
- Support for all subtitle formats
### Diarization
- Select from multiple diarization models / pipelines
- Optimize audio trakcs for diarizaiton by isolating lines speech based on subtitle timings
- Investigate Diart?
### TTS
- ~~Rework the speed control to use PyDub to speed up audio.~~
- ~~match the volume of the speaker to TTS~~
- Checkbox to remove sequential subtitle entries and entries that are tiny, e.g. "nom" "nom" "nom" "nom"
- investigate voice conversion?
- Rename "SAPI5" to PyTTSx3 and add better support for SAPI5 and OneCore voices
- Build an asynchronous queue of operations to perform
- Started - Asynchronous GUI for Coqui model downloads
- Add support for MyCroft Mimic 3
- Add Support for PiperTTS
### Cloning
- Use diaries and subtitles to isolate and build training datasets
- Build a tool to streamline the manual creation of datasets

###### (oh god that's literally so many things, the scope of this has gotten so big how will this ever become a thing)