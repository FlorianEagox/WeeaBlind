# Weeablind

A program to dub anime using modern AI speech synthesization, diarization, and deep-fake cloning.

## Why

This software is a product of war. My sister turned me onto my now-favorite comedy anime "The Disastrous Life of Saiki K." but Netflix never ordered a dub for the 2nd season. I'm blind and cannot and will not ever be able to read subtitles, but I MUST know how the story progresses! Netflix has forced my hand and I will bring AI-dubbed anime to the blind! There are many other shows I'd love to watch, but they'll never receive dubs either. Ideally, this software would be useful for dubbing movies as well from any language to any other language. It will also be good for multi-lengual interviews and news coverage!

## How

This project relies on some rudimentary slapping together of some very complicated models. The program will rip the audio from a video file, diarize it, and then combine the diarized data with the subtitles from the video to generate the lines for each character with a unique voice model. FFmpeg will then combine these voice lines into a new audio track added to the video with the dub. Ideally, you'll be able to import a show or season and create a clone of the characters' voices to use for future dubs. 

## When?

This is mega-WIP, not even MVP, so idk. Email me or make an issue if you want to contribute or point me in a better direction, idk what I'm doing.

## Things to do:
	- GUI tab to list and select audio / subtitle streams w/ FFMPEG
	- Move the tabs into their own classes
	- Add labels and screen reader landmarks to all the controls
	- Single speaker or multispeaker control switch
	- Download YouTube video with Closed Captions
	- GUI to select start and end time for dubbing
	- Use OCR to generate subtitles for videos that don't have sub streams
	- Use OCR for non-text based subtitles
	- Make a cool logo?
	- Learn how to package python programs as binaries to make releases
	- Remove the copyrighted content from this repo (sorry no sorry TV Tokyo)
	- Save and import config files for later
### Diarization
	- Select from multiple diarization models / pipelines
	- Optimize audio trakcs for diarizaiton by isolating lines speech based on subtitle timings
	- Investigate Diart?
	- For multi-langual media, compare diary with subtitles to find non-english components of a video
### TTS
	- Rework the speed control to use PyDub to speed up audio.
	- match the volume of the speaker to TTS
	- investigate voice conversion?
	- Rename "SAPI5" to PyTTSx3 and add better support for SAPI5 and OneCore voices
	- Build an asynchronous queue of operations to perform
	- Asynchronous GUI for Coqui model downloads
	- Add support for MyCroft Mimic 3
	- Add Support for PiperTTS
### Cloning
	- Use diaries and subtitles to isolate and build training datasets
	- Build a tool to streamline the manual creation of datasets

###### (oh god that's literally so many things, the scope of this has gotten so big how will this ever become a thing)