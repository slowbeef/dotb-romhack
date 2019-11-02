# dotb-romhack
Effort to translate DOTB into English

About time I put this in github. This code isn't great because I wrote most of it on stream and didn't really have a great plan. My ROMHack streams turned into impromptu Com Sci stuff, so I had finite state machines on the brain.

Lately I've been thinking "just to do this whole thing with regex" but I haven't moved on it in forever so...

Easy game stuff:

The Japanese is all Shift-JIS, sorta. Hiragana is encoded funny; I guess as really lazy compression, they subtract 0x8270 to make a one-byte character out of two-byte kana. But katakana and Kanji are just regular shift-JIS.

There's markup code in there - the mes_extractor.rb has some of it; things like alternate lines in a dialogue box that can appear depending on flags, or lines that might or might not appear at all.

There's no real text pointers, either. It just reads the lines serially so you don't have to worry about space in that sense. 