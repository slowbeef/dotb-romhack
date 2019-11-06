# dotb-romhack
Effort to translate DOTB into English

About time I put this in github. This code isn't great because I wrote most of it on stream and didn't really have a great plan. My ROMHack streams turned into impromptu Com Sci stuff, so I had finite state machines on the brain.

Lately I've been thinking "just to do this whole thing with regex" but I haven't moved on it in forever so...

Easy game stuff:

The Japanese is all Shift-JIS, sorta. Hiragana is encoded funny; I guess as really lazy compression, they subtract 0x8270 to make a one-byte character out of two-byte kana. But katakana and Kanji are just regular shift-JIS.

There's markup code in there - the mes_extractor.rb has some of it; things like alternate lines in a dialogue box that can appear depending on flags, or lines that might or might not appear at all.

There's no real text pointers, either. It just reads the lines serially so you don't have to worry about space in that sense. 

TODO: Get rid of mes_decrypt.py maybe? Or make it work.

Text Files
-----

I've included a Windows executable called EDITDISK - it's extracts FDI (Floppy Disk Images) into a drag and drop interface so you can pull files out. DOTB keeps its text in MES files which are generally numbered and correspond to a "room" in the game. Note there are cutscene sequences which can consist of multiple "rooms" and such.

There's a couple of special ones like:

* OOOOOO.MES - Please note this is not 000000.MES; This contains the nametags for the different characters... at different speeds! This is weird so basically what that means is there's nametags with and without bytecode prepended to perform "blitting" - that thing where text in dialogue boxes comes onscreen character-by-character.

* OPEN\_1.MES, OPEN\_2.MES - This is the game's (long) opening cutscene split across two MES files. Once you get past these, the game has everything else in the numbered MES files like 000000.MES, 000001.MES, etc.

DOTB Text Encoding
----
The easiest way to find a line of Japanese is 0xBA23, 0xBA24, 0xBA25.

0xBA is a general control code the game uses for a lot of stuff. 23,24,25 are "Character 1, 2, and 3" depending on the scene you're in, and tell the game which nametag to use (from the OOOOOO.MES file, again, that's capital o, not zero).

It is not safe to assume character 1 is always Cole and character 2 is always Doc Cooger, though that is generally the case, especially for Disk 1.

Japanese is mostly Shift-JIS except for hiragana. Note that there's bytecode inserted in the text sometimes which will basically say "if a flag is set, display this sentence" - I mean in the middle of text, mind!

0xBA26 is how dialogue boxes end - when you're reading it in to extract Japanese, consider that the end of that line.

0xBA28 signifies punctuation for some reason. There's a section on that.


DOTB Japanese Encoding
-----

DOTB puts Katakana and Kanji in Shift-JIS. Hiragana is a little silly; to "compress" the text somewhat, they take the shift-JIS version (two-bytes), remove the first byte (0x82) and subtract 0x72.

Basically, when extracting the Japanese to a text file from your translator, anything between 0x2D and 0x7F (inclusive) is hiragana and you have to add 0x8272 to it to make it into valid Shift-JIS hiragana.

DOTB Puncutation Encoding
-----

Note these are all full-width (16x16).

Colons are a special case. Yep.

* 0xBA280D: 、(Japanese comma)
* 0xBA280E: ‥ (Double ellipse)
* 0xBA280F: 。(Japanese period)
* 0xBA2810: (whitespace)
* 0xBA2811: ！(full-width exclamation point)
* 0xBA2812: ？(full-width question mark)
* 0xBA2813: Newline

DOTB Inline Control Codes
----
Some dialogue boxes have dynamic text - that is, text that may or not be displayed depending on if a game flag is set. For example, you may see:

> Cole: It's a flashlight.

Or:

> Cole: It's a flashlight. I've seen it before.

And "I've seen it before." would be surrounded by bytecode which basically says "Print this if Flag 0x03 is set" like \<IF FLAG(C)=TRUE> ... \<ENDIF>

There's a different control code which does \<IF> \<ELSE> \<ENDIF> functionality.

DOTB If Statements
----

* 0xBC0C\__ tells you that it's testing for a flag, the next byte is which flag. 0xA3 tells it the conditional part is over. (\<ENDIF>)

Putting that together:

> 0xBA23 It's a flashlight. 0xBC0C03 I've seen it before. 0xA3 0xBA26

This means it's testing flag 03, and if that's set, it'll print the second part of the text, "I've seen it before.

DOTB If/Else Statements
----
* 0xB2A2 tells you there's going to be an if, else. statement. 0xA4 is the \<ELSE> and 0xA3 is the \<ENDIF> just like in the if-statement.

Just a note, I'm not sure where DOTB gets which flag to test on in this example, though you shouldn't need it to replace Japanese with English.

Suppose the text:

> Cole: It's a zombie. I've never seen one before!

Versus:

> Cole: It's a zombie. The same one I saw earlier.

DOTB would encode this like:

> 0xBA23 It's a zombie. 0xB2A2 I've never seen one before! 0xA4 The same one I saw earlier. 0xA3 0xBA26


Writing English in DOTB
----

Of course, Shift-JIS is full-width English which is pretty ugly, but we have a workaround. Start half-width English with 0x21 (Exclamation point in ASCII), terminate with null 0x00.

You'll still want to start a dialogue box with 0xBA23 (for example) and end with 0xBA26.

As of this writing, I don't know if this supports the in-line control codes, though I believe you can null terminate a section of half-width English and start it again. I won't put the example since this is theory and I haven't tried it out just yet.

Linebreaking
----

DOTB supports line breaks with 0xBA2813. Dialogue boxes have 30 characters full-width or 60 if you're using the halfwidth English. Note you have to account for the name tag!

Half-width English is using the system font (aka what's on your PC-98).

Nametags (a special note about colons too)
----

OOOOOO.MES contains the nametags. They're repeated three times for silly reasons. At the main menu, you can change game text speed to NOMAL-SPEED [sic], or HI-SPEED.

HI-SPEED means the game just prints the text onscreen with no delay. You'll notice the nametags in the hi-speed section are just, well, nametags. That is, it's the character name in Katakana or Kanji followed by a Japanese colon)

NOMAL-SPEED (game default, which is quite slow and I don't recommend) has each nametag prepended with 10 or so bytes of bytecode. The bytecode seems to be what tells Dead of the Brain to print the text slowly! So rather than some variable or config that tells DOTB how to print text, it's injected into the dialogue box bytecode with every box.

Why are the nametags in there 3 times then?

Well, the first section is the default. The second is if the player selects high speed. The third is if they select normal speed again. What's that? Why didn't they just use the first one for normal speed and default (since it's the same)? Beats me!

Each nametag is suffixed with 0x815B which is a Shift-JIS colon. Unfortunately, the script reader is using 5B in that location and if you try to change it to a half-width English colon, the game hangs! There's two solutions:

* Make nametags like this: 0x21 Cole 0x00 0x815B - Use half-width text with a full-width colon. 
* Remove nametags entirely with 0xA3 - this tells the reader to abort. You can then print the nametag directly in your dialogue box (i.e. put it in the English manually.) Only thing is, with the Normal speed, the nametag will "blip" in like regular text, then. But you can use the half-width colon.

Honestly, the full-width colon doesn't look bad or anything, but the separate nametag does throw off linebreak calculation. It's fine either way, in my opinion.