# Weeablind

A program to dub anime using modern AI speech synthesization, diarization, and deep-fake cloning.

## Why

This software is a product of war. My sister turned me onto my now-favorite comedy anime "The Disastrous Life of Saiki K." but Netflix never ordered a dub for the 2nd season. I'm blind and cannot and will not ever be able to read subtitles, but I MUST know how the story progresses! Netflix has forced my hand and I will bring AI-dubbed anime to the blind! There are many other shows I'd love to watch, but they'll never receive dubs either. Ideally, this software would be useful for dubbing movies as well from any language to any other language.

## How

This project relies on some rudimentary slapping together of some very complicated models. The program will rip the audio from a video file, diarize it, and then combine the diarized data with the subtitles from the video to generate the lines for each character with a unique voice model. FFmpeg will then combine these voice lines into a new audio track added to the video with the dub. Ideally, you'll be able to import a show or season and create a clone of the characters' voices to use for future dubs. 

## When?

This is mega-WIP, not even MVP, so idk. contrib if ya can.