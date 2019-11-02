# Dead of the Brain MES Inserter
# (Open_1.MES)
#
# BA[23-25] to start a dialog box
# ASCII 21 (!) to start a half-width string
# Terminate with null
# BA26 to end a dialog box.

module MODE
	BINARY   = 0
	TEXT     = 1
	CONTROL  = 2
	JAPANESE = 3
	JCONTROL = 4
	POSSIBLE_MENU = 5
	MENU     = 6
	SKIP_NEXT = 7
	SPECIAL_WRITING = 8
end

if (ARGV.empty?)
	puts "Usage: ruby mes_inserter.rb inputMesFile.MES filledTranslation.TXT"
	exit
end

originalFile = File.open(ARGV[0], "rb")
englishFile = File.open(ARGV[1],"rb")
outputFile = File.open(ARGV[0] + ".OUT", "wb")

mes = ARGV[0].gsub(/[^\\]+\\/,'')

lineLength = 60
allNameTags = { "OPEN_1.MES" => ["Cole: ", "Cooger: ", "Cop: "]}
nameTags = allNameTags[mes]

state = MODE::BINARY
countLines = 0

inMenu = false

until originalFile.eof?
	byteOrig = originalFile.read(1)
	byte = byteOrig.unpack("H*")[0]

	if (state == MODE::BINARY)
		outputFile.write(byteOrig)

		if (byte == "ba")
			state = MODE::CONTROL
		elsif (byte == "2c")
			state = MODE::POSSIBLE_MENU
		elsif (byte == "a2")
			state = MODE::SPECIAL_WRITING
		end

	elsif (state == MODE::SPECIAL_WRITING)
		if (byte == "21")
			state = MODE::BINARY
		elsif (byte == "be")
			state = MODE::BINARY
		elsif (byte == "cd")
			state = MODE::BINARY
		elsif (byte == "81")
			state = MODE::JAPANESE
			seek(-1)
		elsif (byte == "82")
			state = MODE::JAPANESE
			seek(-1)
		elsif (byte == "a4")
			state = MODE::JAPANESE
			seek(-1)
		elsif (byte == "a3")
			state = MODE::JAPANESE
			seek(-1)
		elsif (byte == "ac")
			state = MODE::JAPANESE
			seek(-1)
		elsif (byte == "ba")
			state = MODE::JAPANESE
			seek(-1)
		elsif (byte.to_i(16) >= 0x83 && byte.to_i <= 0x9F)
			state = MODE::JAPANESE
			seek(-1)
		elsif (byte.to_i(16) >= 0x2d && byte.to_i <= 0x7f)
			state = MODE::JAPANESE
			seek(-1)
		else 
			state = MODE::BINARY
		end	

		
	elsif (state == MODE::SKIP_NEXT)
		line = ""
		while !line.match("^New Dialog: ")
			line = englishFile.readline				
			puts line

		end
		while !byte == "ac"
			byteOrig = originalFile.read(1)
			byte = byteOrig.unpack("H*")[0]
		end
		state = MODE::BINARY
		
	elsif (state == MODE::POSSIBLE_MENU)
		outputFile.write(byteOrig)
		if (byte == "a2")
			state = MODE::MENU
			outputFile.write([0x21].pack("S*").chop)   # 0x21 means start half-width English
			
			line = englishFile.readline
			while !line.match("^New Dialog: ")
				line = englishFile.readline				
#				puts line
			end
			line = line.gsub(/New Dialog: /, '')
			outputFile.write(line.chop)
			outputFile.write([0x00].pack("S*").chop)  #0x00 null-terminate the half-width English		
	
		else
			state = MODE::BINARY
		end		
		
	elsif (state == MODE::MENU)
		if (byte == "a4")
			outputFile.write(byteOrig)

			outputFile.write([0x21].pack("S*").chop)   # 0x21 means start half-width English
			
			line = englishFile.readline
			while !line.match("^New Dialog: ")
				line = englishFile.readline
#				puts line
			end
			line = line.gsub(/New Dialog: /, '')
			
			outputFile.write(line.chop)
			outputFile.write([0x00].pack("S*").chop)  #0x00 null-terminate the half-width English		
		elsif (byte == "a3")
			outputFile.write(byteOrig)
			state = MODE::BINARY
		else 
		end
	
	elsif (state == MODE::CONTROL)
		if (byte == "23" or byte == "24" or byte == "25")
		
		#BA23 signals Character 1 is about to speak
		#BA24 signals Character 2 is about to speak
		#BA25 signals Character 3 is about to speak
			nameTag = ""
	
			whichLine = 0
			if (byte == "23")
				nameTag = nameTags[0]
			elsif (byte == "24")
				nameTag = nameTags[1]
			elsif (byte == "25")
				nameTag = nameTags[2]
			end
		
			outputFile.write(byteOrig)
		
			line = englishFile.readline
			while !line.match("^New Dialog: ")
				line = englishFile.readline
#				puts line
			end
			line = nameTag + line
			line = line.gsub(/New Dialog: /, '')
		
			parts = line.split(/[<>]/)

			if (parts.count == 1)
				line = line + " "
				outputFile.write([0x21].pack("S*").chop)   # 0x21 means start half-width English

				allSpaces = line.enum_for(:scan, /(?= )/).map{ Regexp.last_match.offset(0).first }

				lineLimit = lineLength
				lastSpace = 0
				startOfLine = 0
				allSpaces.each do |space|
					if space >= lineLimit
						outputFile.write(line[startOfLine..lastSpace])
#						puts "#{startOfLine} #{lastSpace} #{line[startOfLine..lastSpace].chop}X"
						
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
#						outputFile.write([0xa5].pack("S*").chop)  #0x00 null-terminate the half-width English
						whichLine = (whichLine + 1) % 3

						startOfLine = lastSpace + 1
						lineLimit = lastSpace + lineLength + 1
					end
					
					lastSpace = space
				end
				outputFile.write(line[startOfLine..line.length].chop)
#				puts "#{startOfLine} #{lastSpace} #{line[startOfLine..line.length].chop}X"
				
#				outputFile.write(line.chop)
				outputFile.write([0x00].pack("S*").chop)  #0x00 null-terminate the half-width English		

			else 
				(0..parts.count).each do |i|
					if (parts[i] == '' || parts[i] == nil)
						next
					end
					### 5/16 - Why was I taking out spaces from the start of lines?
					#					part = parts[i].gsub(/^ /,'')
					part = parts[i]
					puts "!" + part + "!"
					if (part && part[0,2] == "C ")
						outputFile.write([0xbc].pack("S*").chop)
						outputFile.write([0xa2].pack("S*").chop)
						outputFile.write([0x0c].pack("S*").chop)
						outputFile.write(part[2,4].hex.chr)
					elsif (part && part[0,2] == "/C")
						outputFile.write([0x00].pack("S*").chop)
						outputFile.write([0xa3].pack("S*").chop)
					else
						outputFile.write([0x21].pack("S*").chop)   # 0x21 means start half-width English
						outputFile.write(part)
						outputFile.write([0x00].pack("S*").chop)  #0x00 null-terminate the half-width English					
					end
				end
			end
		
			state = MODE::JAPANESE
			
		elsif (byte == "a2")
			outputFile.write(byteOrig)
			outputFile.write([0x21].pack("S*").chop)   # 0x21 means start half-width English
			line = englishFile.readline
			while !line.match("^New Dialog: ")
				line = englishFile.readline
				line = replaceConditionals(line)
#				puts line
			end
			line = line.gsub(/New Dialog: /, '')
		
			outputFile.write(line.chop)
			outputFile.write([0x00].pack("S*").chop)  #0x00 null-terminate the half-width English
		
		else
			outputFile.write(byteOrig)
			state = MODE::BINARY
		end
	
	elsif (state == MODE::JAPANESE)
		if (byte == "ba")
			byteOrig = originalFile.read(1)
			byte = byteOrig.unpack("H*")[0]
			if (byte == "26")
				outputFile.write([0xBA].pack("S*").chop)
				outputFile.write([0x26].pack("S*").chop)   # 0xBA26 ends a dialogue box

				state = MODE::BINARY
			end
		elsif (byte == "0c")
			outputFile.write(byteOrig)
			outputFile.write(originalFile.read(1))
		end
	end
	countLines = countLines + 1
end


