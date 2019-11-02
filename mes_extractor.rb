# Dead of the Brain MES Extractor
# Dead of the Brain MES Extractor
# (Open_1.MES)
#
# 83-9F Kanji
# BA - Control Code
# 0xBA23 - starts dialogue, Cole's nametag
# 0xBA[24|25] - second and third character
# 0xBA26 - ends dialogue
# 0xBA280E - punctuation

module Mode
	BINARY = 0
	HIRAGANA = 1
	SPECIAL1 = 2
	SPECIAL2 = 3
	CONTROL = 4
	PUNCTUATION = 5
	NORMAL = 6
	SPECIAL3 = 7
	CONDITIONAL_SCRIPTING = 8
	CONDITIONAL = 9
	WRITING_FLAG = 10
	SWITCH_SCRIPTING = 11
	SWITCH = 12
	SPECIAL_WRITING = 13
	SPECIAL4 = 14
	SPECIAL5 = 15
	NEWLINE = 16
	NEXTLINE = 17
	NAMETAG = 18
	NAMETAG_OPEN = 19
	SPECIAL6 = 20
end

state = Mode::BINARY

if (ARGV.empty?)
	puts "Hey give me an input filename, jerk!"
	puts "Usage: ruby mes_extractor.rb 'MES_IN\OPEN_1.MES' 'filled_translation\OPEN_1.TXT'"
	exit
end

mesFile = File.open(ARGV[0], "rb")
outputFile = File.open(ARGV[0] + ".ENG", "wb")
mes = ARGV[0].gsub(/[^\\]+\\/,'')

if (ARGV[1])
	filledTranslation = []
	filledTranslationfile = File.open(ARGV[1], "rb")
	until filledTranslationfile.eof?
		line = filledTranslationfile.readline
		if line =~ /New Dialog:/
			filledTranslation << (line.gsub(/New Dialog: /, ''))
		end
	end
end
	
inConditional = false
inSwitch = false
writingLine = false
previousStates = []
writingEnglish = false

allNameTags = { "OPEN_1.MES" => ["Cole: ", "Cooger: ", "Cop: "]}
nameTags = allNameTags[mes]

def writeEnglish(writingEnglish, filledTranslation, nameTag, outputFile)
	if writingEnglish == true
		return
	end

	lineLength = 60
	line = filledTranslation.shift
	line = nameTag + line

	parts = line.split(/[<>]/)

	(0..parts.count).each do |i|
		if (parts[i] == '' || parts[i] == nil)
			next
		end
		part = parts[i]
		
		if (part && part[0,2] == "C ")
		
			outputFile.write([0xbc].pack("S*").chop)
			outputFile.write([0xa2].pack("S*").chop)
			outputFile.write([0x0c].pack("S*").chop)
			outputFile.write(part[2,4].hex.chr)
		elsif (part && part[0,2] == "/C")
			outputFile.write([0x00].pack("S*").chop)
			outputFile.write([0xa3].pack("S*").chop)
		else
			line = line + " "
			outputFile.write([0x21].pack("S*").chop)   # 0x21 means start half-width English

			allSpaces = line.enum_for(:scan, /(?= )/).map{ Regexp.last_match.offset(0).first }

			lineLimit = lineLength
			lastSpace = 0
			startOfLine = 0
			allSpaces.each do |space|
				if space >= lineLimit
					outputFile.write(line[startOfLine..lastSpace])
						
					if whichLine == 2
						outputFile.write([0x00].pack("S*").chop)
						outputFile.write([0xba].pack("S*").chop)
						outputFile.write([0x26].pack("S*").chop)
						outputFile.write([0xba].pack("S*").chop)
						outputFile.write([0x23].pack("S*").chop)
						outputFile.write([0x21].pack("S*").chop)

					else
						(lastSpace..lineLimit - 2).each do
							outputFile.write(" ")
						end
					end
					whichLine = (whichLine + 1) % 3

					startOfLine = lastSpace + 1
					lineLimit = lastSpace + lineLength + 1
				end
					
				lastSpace = space
			end
			outputFile.write(line[startOfLine..line.length].chop)
				
			outputFile.write([0x00].pack("S*").chop)  #0x00 null-terminate the half-width English		
		end
	end
	return
end

until mesFile.eof?
	byteOrig = mesFile.read(1)
	byte = byteOrig.unpack("H*")[0]
	
	if (state == Mode::BINARY)
		outputFile.write(byteOrig)

		if (byte == "ba")
			previousStates.push(state)
			state = Mode::CONTROL
		elsif (byte == "a4")
			state = Mode::SPECIAL1
		elsif (byte == "a2")
			state = Mode::SPECIAL_WRITING
		elsif (byte == "a8")
			state = Mode::SPECIAL4
		elsif (byte == "b9")
			byteOrig = mesFile.read(1)
			byte = byteOrig.unpack("H*")[0]

			outputFile.write(byteOrig)

			if (byte == "23" || byte == "24" || byte == "25")
				if (byte == "23")
					nameTag = nameTags[0]
				elsif (byte == "24")
					nameTag = nameTags[1]
				elsif (byte == "25")
					nameTag = nameTags[2]
				end
				state = Mode::NAMETAG_OPEN
			end
		end
		next
		
	elsif (state == Mode::NAMETAG_OPEN)
		outputFile.write(byteOrig)

		if (byte == "0f")
			outputFile.write([0xA3].pack("S*").chop) # A2 is the "don't write nametag, abort" control code

			print "Found nametag: "
			state = Mode::NAMETAG				
		end
		next

	elsif (state == Mode::NAMETAG)
		if (byte == "81")
			print [0x81].pack("S*").chop
			print mesFile.read(1)
		elsif (byte == "82")
			print [0x82].pack("S*").chop
			print mesFile.read(1)
		elsif (byte == "a3")
			byte = mesFile.read(1)
			print "\n\n"
			state = Mode::BINARY
		elsif (byte == "a9")
			print "\n\n"
			state = Mode::BINARY
		elsif (byte.to_i(16) >= 0x83 && byte.to_i <= 0x9F)
			print [byte.to_i(16)].pack("S*").chop
			print mesFile.read(1)
		elsif (byte.to_i(16) >= 0x2d && byte.to_i <= 0x7f)
			print [0x82].pack("S*").chop
			print [byte.to_i(16) + 0x72].pack("S*").chop
		else
			state = Mode::BINARY
		end

	
	elsif (state == Mode::SPECIAL1)
		outputFile.write(byteOrig)
		if (byte == "aa")
			state = Mode::SPECIAL2
		elsif (byte == "ba")
			state = Mode::CONTROL
		elsif (byte == "21")
			state = Mode::BINARY
		else
			state = Mode::BINARY
		end
		next

	elsif (state == Mode::SPECIAL2)
		outputFile.write(byteOrig)
		if (byte == "28")
			state = Mode::SPECIAL3
		else
			state = Mode::BINARY
		end
		next

	elsif (state == Mode::SPECIAL3)
		outputFile.write(byteOrig)
		if (byte == "0e")
			state = Mode::NORMAL
		else
			state = Mode::BINARY
		end
		next

	elsif (state == Mode::SPECIAL4)
		outputFile.write(byteOrig)
		if (byte == "28")
			state = Mode::SPECIAL5
		else
			state = Mode::BINARY
		end
		next

	elsif (state == Mode::SPECIAL5)
		outputFile.write(byteOrig)
		if (byte == "0f")
			state = Mode::SPECIAL6
		else
			state = Mode::BINARY
		end
		next

	elsif (state == Mode::SPECIAL6)
		if (byte == "bb")
			outputFile.write(byteOrig)
			outputFile.write(mesFile.read(2))
		elsif (byte == "d0")
			outputFile.write(byteOrig)
			state = Mode::BINARY
		elsif (byte == "ba")
			outputFile.write(byteOrig)
			previousStates.push(state)
			state = Mode::CONTROL
		elsif (byte == "81")
			writeEnglish(writingEnglish, filledTranslation, nameTag, outputFile)
			writingEnglish = true

			print [0x81].pack("S*").chop
			print mesFile.read(1)
		elsif (byte == "82")
			writeEnglish(writingEnglish, filledTranslation, nameTag, outputFile)
			writingEnglish = true

			print [0x82].pack("S*").chop
			print mesFile.read(1)
		elsif (byte == "ac")
			outputFile.write(byteOrig)
			print "\nNew Dialog: \n\n"
		elsif (byte.to_i(16) >= 0x83 && byte.to_i <= 0x9F)
			writeEnglish(writingEnglish, filledTranslation, nameTag, outputFile)
			writingEnglish = true

			print [byte.to_i(16)].pack("S*").chop
			print mesFile.read(1)
		elsif (byte.to_i(16) >= 0x2d && byte.to_i <= 0x7f)
			writeEnglish(writingEnglish, filledTranslation, nameTag, outputFile)
			writingEnglish = true

			print [0x82].pack("S*").chop
			print [byte.to_i(16) + 0x72].pack("S*").chop
		else 
			outputFile.write(byteOrig)
			state = Mode::BINARY
			writingEnglish = false
		end
		next
		
	elsif (state == Mode::CONTROL)
		if (byte == "23" || byte == "24" || byte == "25")
			if (byte == "23")
				nameTag = nameTags[0]
			elsif (byte == "24")
				nameTag = nameTags[1]
			elsif (byte == "25")
				nameTag = nameTags[2]
			end

			if (writingLine == true)
#				print "\nNew Dialog: \n\n"
			else
				writingLine = true
			end
		end
		
		if (byte == "23")
			nameTag = nameTags[0]
			outputFile.write(byteOrig)
			print "Cole: "
			state = Mode::NORMAL
		elsif (byte == "24")
			nameTag = nameTags[1]
			outputFile.write(byteOrig)

			print "Cooger: "
			state = Mode::NORMAL
		elsif (byte == "25")
			nameTag = nameTags[2]
			outputFile.write(byteOrig)

			print "Officer: "
			state = Mode::NORMAL
		elsif (byte == "26")
			outputFile.write([0xBA].pack("S*").chop)
			outputFile.write(byteOrig)

			if (ARGV[1])
				line = filledTranslation.shift
				print "\nNew Dialog: "
				print line
			else
				print "\nNew Dialog: \n\n"
			end
			writingLine = false
			state = previousStates.pop
		elsif (byte == "28")
			state = Mode::PUNCTUATION
		elsif (byte == "2e")
			outputFile.write(byteOrig)
			state = Mode::BINARY
		elsif (byte == "22")
			outputFile.write(byteOrig)
			state = Mode::BINARY
		end
		
	elsif (state == Mode::PUNCTUATION)
		if (byte == "0d")
			print [0x81].pack("S*").chop
			print [0x41].pack("S*").chop
		elsif (byte == "0e")
			print [0x81].pack("S*").chop
			print [0x64].pack("S*").chop
		elsif (byte == "0f")
			print [0x81].pack("S*").chop
			print [0x42].pack("S*").chop
		elsif (byte == "10")
			print [0x81].pack("S*").chop
			print [0x40].pack("S*").chop
		elsif (byte == "11")
			print [0x81].pack("S*").chop
			print [0x49].pack("S*").chop
		elsif (byte == "12")
			print [0x81].pack("S*").chop
			print [0x48].pack("S*").chop
		elsif (byte == "13")
			print "\\n"
			# Looks like \\n
			# Don't know, but might be a scripting control code
#			state = Mode::NEWLINE
#			next
		else
#			state = Mode::BINARY
			state = previousStates.pop()
		end
		state = Mode::NORMAL			

	elsif (state == Mode::NEWLINE)
		if (byte == "ba")
			state = Mode::NEXTLINE
		end

	elsif (state == Mode::NEXTLINE)		
		if (byte == "23")		
			nameTag = nameTags[0]
			print "Cole: "
			state = Mode::NORMAL
		elsif (byte == "24")
			nameTag = nameTags[1]
			print "Cooger: "
			state = Mode::NORMAL
		elsif (byte == "25")
			nameTag = nameTags[2]
			print "Officer: "
			state = Mode::NORMAL
		end
		
	elsif (state == Mode::NORMAL)

		if (byte == "ba")
#			outputFile.write(byteOrig)
			state = Mode::CONTROL
		elsif (byte == "bc")
			outputFile.write(byteOrig)
			state = Mode::CONDITIONAL_SCRIPTING
		elsif (byte == "b2")
			outputFile.write(byteOrig)
			state = Mode::SWITCH_SCRIPTING
		elsif (byte == "ac")
			print "\nNew Dialog: \n\n"
			state = Mode::BINARY
		elsif (byte == "a5") # Was this end of text in another context?
			outputFile.write(byteOrig)
			print "\\n"
#			state = Mode::BINARY			
		elsif (byte == "a4")
			outputFile.write(byteOrig)
			if (inSwitch)
				print "<ELSE>"				
			end
		elsif (byte == "a3")
			outputFile.write(byteOrig)
			if (inConditional)
				inConditional = false
				print "</C>"
			elsif (inSwitch)
				inSwitch = false
				print "</SWITCH>"
			else
				print "\nNew Dialog: \n\n"
				state = Mode::BINARY
			end
		elsif (byte == "d0")
			outputFile.write(byteOrig)
			state = Mode::BINARY
		elsif (byte == "81")
			writeEnglish(writingEnglish, filledTranslation, nameTag, outputFile)
			writingEnglish = true
			print [0x81].pack("S*").chop
			print mesFile.read(1)
		elsif (byte == "82")
			writeEnglish(writingEnglish, filledTranslation, nameTag, outputFile)
			writingEnglish = true
			print [0x82].pack("S*").chop
			print mesFile.read(1)
		elsif (byte.to_i(16) >= 0x83 && byte.to_i <= 0x9F)
			writeEnglish(writingEnglish, filledTranslation, nameTag, outputFile)
			writingEnglish = true
			print [byte.to_i(16)].pack("S*").chop
			print mesFile.read(1)
		elsif (byte.to_i(16) >= 0x2d && byte.to_i <= 0x7f)
			writeEnglish(writingEnglish, filledTranslation, nameTag, outputFile)
			writingEnglish = true
			print [0x82].pack("S*").chop
			print [byte.to_i(16) + 0x72].pack("S*").chop
		else 
			outputFile.write(byteOrig)
			state = Mode::BINARY
			writingEnglish = false
		end

	elsif (state == Mode::SPECIAL_WRITING)
		if (byte == "21")
			outputFile.write(byteOrig)
			state = Mode::BINARY
		elsif (byte == "be")
			outputFile.write(byteOrig)
			state = Mode::BINARY
		elsif (byte == "cd")
			outputFile.write(byteOrig)
			state = Mode::BINARY
		elsif (byte == "81")
			writeEnglish(writingEnglish, filledTranslation, nameTag, outputFile)
			writingEnglish = true

			print [0x81].pack("S*").chop
			print mesFile.read(1)
		elsif (byte == "82")
			writeEnglish(writingEnglish, filledTranslation, nameTag, outputFile)
			writingEnglish = true
			print [0x82].pack("S*").chop
			print mesFile.read(1)
		elsif (byte == "a4")
			outputFile.write(byteOrig)
			print "\nNew Dialog: \n\n"
		elsif (byte == "a3")
			outputFile.write(byteOrig)
			print "\nNew Dialog: \n\n"
			state = Mode::BINARY
		elsif (byte == "ac")
			outputFile.write(byteOrig)
			print "\nNew Dialog: \n\n"
			state = Mode::BINARY
		elsif (byte == "ba")
			outputFile.write(byteOrig)
			state = Mode::CONTROL
		elsif (byte.to_i(16) >= 0x83 && byte.to_i <= 0x9F)
			writeEnglish(writingEnglish, filledTranslation, nameTag, outputFile)
			writingEnglish = true

			print [byte.to_i(16)].pack("S*").chop
			print mesFile.read(1)
		elsif (byte.to_i(16) >= 0x2d && byte.to_i <= 0x7f)
			writeEnglish(writingEnglish, filledTranslation, nameTag, outputFile)
			writingEnglish = true

			print [0x82].pack("S*").chop
			print [byte.to_i(16) + 0x72].pack("S*").chop
		else 
			outputFile.write(byteOrig)
			state = Mode::BINARY
			writingEnglish = false
		end	
		
	elsif (state == Mode::WRITING_FLAG)
		outputFile.write(byteOrig)
		print "<C "
		print byte
		print ">"
		state = Mode::NORMAL
		
	elsif (state == Mode::CONDITIONAL)
		outputFile.write(byteOrig)
		if (byte == "0c")
			inConditional = true
			state = Mode::WRITING_FLAG	
		end
		
	elsif (state == Mode::CONDITIONAL_SCRIPTING)
		outputFile.write(byteOrig)
		if (byte == "a2")
			state = Mode::CONDITIONAL	
		end
		
	elsif (state == Mode::SWITCH_SCRIPTING)
		outputFile.write(byteOrig)
		if (byte == "a2")
			print "<SWITCH>"
			inSwitch = true
			state = Mode::NORMAL
		end
		
	end
end