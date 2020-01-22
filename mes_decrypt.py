#!/usr/bin/python

#LINEBREAKS ARE FIXED. NOW MARCH THROUGH THE ENG MES FILES

#10PLUS - Breaking bug when fighting the zombie and clicking on the eyes.
#Wrong people are talking in the records room.

# Missing a -Ga- in 000008 - Line 28. Stops at a linebreak.

#TODO: Genericize Nametags
# How this works.
# B9 23/24/25 sets the name tag.
# BA 23/24/25 uses it.
# Look for B9 25 to figure out the new nametag
# Put them into nametags

#TODO - I think Fixed.
# Empty "Cole: " when you enter the flashlight room from the hall
# "I've already taken the flashlight" before you do. - Missing line in the flashlight room.

#TODO: Extract these random control codes into a dictionary or function or something.

#TODO: BA28_ nametags
# 17PLUS has Nose

import re
import csv
import os
import sys
import argparse

import nametags

debugBytes = False  # Turn this on manually to export the bytes being read to standard out; useful if the script breaks
gotTranslation = False

#outputType = 'lined'
outputType = 'spreadsheet'

mesName = 'MES_IN/000020'

parser = argparse.ArgumentParser(description='MES files to pass in')
parser.add_argument("-m", default="MES_IN/000001", help="This is the name of the MES file with the directory it's in (and where to put stuff)")
parser.add_argument("-d", default=False, help="Turns on debug mode (prints all bytes as they are parsed)")
args = parser.parse_args()
mesName = args.m
debugBytes = args.d

print "Working on " + mesName

filename = mesName + '.MES'
transFile = mesName + '.ENG.CSV'



if os.path.exists(transFile):
    gotTranslation = True

def addNametags(mesCode):
    startToTag = b'\xBC\xA2\x0E\x59\xB9'
    startOfName = b'\xA2\xA8\x28\x0F\x21'
    middle = b'\x00\x81\x97\xA3\xA4\xB9'
    startToLowSpeedTag = b'\xA2\xD0\x73\x65\x20\x28\x1D\xA9\x23\xA8\x28\x0F\x21'
    end = b'\x00\x81\x97\xA9\x28\x06\x23\xD0\x73\x65\x20\x28\x1B\x18\x12\xA3\xA3'

    tagLookup = {
        "MES_IN/OPEN_1" : [b'\x23', b'\x24'],
        "MES_IN/000001" : [b'\x23', b'\x24', b'\x25'],
        "MES_IN/000002" : [b'\x23', b'\x24', b'\x25'],
        "MES_IN/000003" : [b'\x23', b'\x24', b'\x25'],
        "MES_IN/000004" : [b'\x23'],
        "MES_IN/000005" : [b'\x23'],
        "MES_IN/000006" : [b'\x23'],
        "MES_IN/000007" : [b'\x23'],
        "MES_IN/000008" : [b'\x23'],
        "MES_IN/000009" : [b'\x23'],
        "MES_IN/000010" : [b'\x23'],
        "MES_IN/000011" : [b'\x23', b'\x24', b'\x25'],
        "MES_IN/000012" : [b'\x23', b'\x24', b'\x25'],
        "MES_IN/000013" : [b'\x23', b'\x24', b'\x25']
    }


    nameLookup = {
        "MES_IN/OPEN_1" : ["Cole: ", "Cooger: "],
        "MES_IN/000001" : ["Cole: ", "Cooger: ", "Sheila: "],
        "MES_IN/000002" : ["Cole: ", "Cooger: ", "Sheila: "],
        "MES_IN/000003" : ["Cole: ", "Cooger: ", "Sheila: "],
        "MES_IN/000004" : ["Cole: "],
        "MES_IN/000005" : ["Cole: "],
        "MES_IN/000006" : ["Cole: "],
        "MES_IN/000007" : ["Cole: "],
        "MES_IN/000008" : ["Cole: "],
        "MES_IN/000009" : ["Cole: "],
        "MES_IN/000010" : ["Cole: "],
        "MES_IN/000011" : ["Cole: ", "Cooger: ", "Sheila: "],
        "MES_IN/000012" : ["Cole: ", "Cooger: ", "Sheila: "],
        "MES_IN/000013" : ["Cole: ", "Cooger: ", "Sheila: "]
    }

    names = nameLookup.get(mesName, '')
    tags = tagLookup.get(mesName, '')
    if names != '' and tags != '':
        count = 0
        for name in names:
            mesCode = startToTag + tags[count] + startOfName + name + middle + tags[count] + startToLowSpeedTag + name + end + mesCode
            count = count + 1
    return mesCode

def addLineBreaks(unbrokenLine, nametag):
    linewidth = 59
    linebreak = 59
    count = 0
    inTag = False
    lastSpace = -1
    numLines = 1
    skip = 0
    inNameTag = False
    foundIfOrImage = False
    foundIf = False
    foundElseOrOther = False
    foundElse = False
    foundOr = False
    tagCount = 0
    countSinceIf = 0
    escaping = False

    if len(nametag) > 0:
        unbrokenLine = nametag + ": " + unbrokenLine

    # Strings are immutable in Python?!!
    line = list(unbrokenLine)
    debugLine = False

    for c in line:
        if c == '\\':
            escaping = True

        if escaping and c == 'n':
            escaping = False
            c = '\n'

        if (count >= linebreak and not inTag) or c == '\n':
            if numLines < 3:
                if count != lastSpace and c != '\n':
                    line[lastSpace] = '\n'
            else:
                numLines = 0
                linebreak = linebreak + linewidth
                tag = "<BOX>"
                tagAsList = list(tag)
                line[lastSpace:len(tagAsList) + 1] = tagAsList
                skip = len(tagAsList)
            numLines = numLines + 1
            linebreak = lastSpace + linewidth
            if c == '\n':
                linebreak = count + linewidth

        if c == ' ' and not inTag:
            lastSpace = count

        if inTag:
            if c == 'I' and tagCount == 0:
                foundIfOrImage = True
            elif c == 'F' and tagCount == 1:
                foundIf = True
                countSinceIf = count
            elif c == 'O' and tagCount == 0:
                foundOr = True
                count = countSinceIf
            elif c == 'E' and tagCount == 0:
                foundElseOrOther = True
            elif c == 'L' and tagCount == 1:
                foundElse = True

            tagCount = tagCount + 1
            linebreak = linebreak + 1

        if c == '<':
            inTag = True
        if c == '>':
            inTag = False
            tagCount = 0
            if foundElse:
                linebreak = count + linewidth

        count = count + 1

    if len(nametag) > 0:
        del line[0:len(nametag) + 2]
    return ''.join(line)

def encodeEnglish(line, count):
    nametag = line["Nametag"]
    english = line["English"]

    english = addLineBreaks(english, nametag)
    if count == 23 and mesName == "MES_IN/000004":
        print english

    english = '!' + english + '\x00\x81\x97'

    #TODO: I know, I know, I'm just testing eng insertion
    if nametag == 'Cole':
        english = '\xBA\x23' + english
    elif nametag == 'Cooger':
        english = '\xBA\x24' + english
    elif nametag == 'Officer Jack':
        english = '\xBA\x25' + english
    elif nametag == 'Sheila':
        english = '\xBA\x25' + english
    elif nametag == 'Killer':
        english = '\xBA\x27' + english

    p = re.compile(r'<IF (.)>')
    english = p.sub(b'\x00\xBC\xA2\x0C\\1\x21', english)

    p2 = re.compile(r'<IMAGE ("[^"]+")>')
    english = p2.sub(b'\x00\x81\x97\xC9\\1\xCF\x24\x23\x21',english)

    p3 = re.compile(r'<VAR (.)>')
    english = p3.sub(b'\x00\x81\x97\x0C\\1\x21', english)

    p4 = re.compile(r'<TEST (.)>')
    english = p4.sub(b'\x00\x81\x97\x08\\1\x21', english)

    p5 = re.compile(r'<VAL (.)>')
    english = p5.sub(b'\x00\x81\x97\x0D\\1\x21', english)

    p6 = re.compile(r'<SET (.)>')
    english = p6.sub(b'\x00\x81\x97\xBC\xA2\x08\\1\x21', english)

    p7 = re.compile(r'<SETVAR (.)>')
    english = p7.sub(b'\x00\x81\x97\x19\\1\x21', english)

    p8 = re.compile(r'<FINAL (.)>')
    english = p8.sub(b'\x00\x81\x97\x19\\1\x21', english)

    # The half-width english routine messes up control codes - 8140 is the hex for a Japanese space
    # Put one after a null to get things back to regular reading so control codes work again.

    english = english.replace('<IF>',b'\x00\x81\x97\xB2\xA2\x21')
    english = english.replace('<ELSE>',b'\x00\x81\x40\xA4\x21')
    english = english.replace('<ENDIF>',b'\x00\x81\x40\xA3\x21')
    english = english.replace('<OR>',b'\x00\x81\x97\xA4\x21')
    english = english.replace('\n',b'\x00\x81\x97\xBA\x28\x13\x21')
    english = english.replace('\\n',b'\x00\x81\x97\xBA\x28\x13\x21')
    english = english.replace('<SPECIAL NEWLINE?>',b'\x00\x81\x97\xA8\x28\x05\x21')
    english = english.replace('<A828OF>',b'\x00\x81\x97\xA8\x28\x0F\x21')
    english = english.replace('<C523280f>',b'\x00\x81\x97\xC5\x23\x28\x0F\x21')
    english = english.replace('<C523280FC52423>',b'\x00\x81\x97\xC5\x23\x28\x0F\xC5\x24\x23\x21')
    english = english.replace('<EMDASH>',b'\x00\x86\xA2\x21')
    english = english.replace('<A0A1>',b'\x00\xA0\xA1\x21')
    english = english.replace('<B6>',b'\x00\xB6\x21')
    english = english.replace('<LONEIF>',b'\x00\x81\x97\xBC\xA2\x21')
    english = english.replace('<BA27>',b'\xBA\x27')
    english = english.replace('<SETVAR91>', b'\x00\x81\x97\xBC\xA2\x19\x91\x21')
    english = english.replace('<BOX>', b'\x00\x81\x97\xBA\x26\xAA\x28\x0E\x21')
    nametag = ''

    return english

def readEnglishFromTranslationFile():
    englishLines = []
    japaneseEnglish = {}
    if os.path.exists(transFile):
        with open(transFile) as csvfile:
            reader = csv.DictReader(csvfile)
            count = 0
            for line in reader:
                japaneseEnglish[line["Japanese"]] = line["English"]
                count = count + 1
                encodedEnglishLine = encodeEnglish(line, count)
                englishLines.append(encodedEnglishLine)
            return (japaneseEnglish, englishLines)
    else:
        print "No translation file found " + transFile

# Function to handle writing the Japanese to a CSV. It supports the old 'linefile'
# format I used on Policenauts, but my translator asked for CSV so he could add notes, etc.
def writeJapaneseToTranslationFile(japaneseLines, both):
    if outputType == 'lined':
        for (nameTag, japanese, english) in japaneseLines:
            print (nameTag + ': ' + japanese + '\nEnglish: \n')
    elif outputType == 'spreadsheet':
        with open(mesName + '.CSV', 'wb') as csvfile:
            fieldnames = 'Nametag','Japanese','English'
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            for (orig, nameTag, japanese, english) in japaneseLines:
                writer.writerow({'Nametag' : nameTag, 'Japanese' : japanese, 'English' : both.get(japanese.decode("shift-jis").encode("utf-8"), '') })
        with open(mesName + '.MASTER.CSV', 'w') as csvfile:
            fieldnames = 'Original Bytes','Nametag','Japanese','English'
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            for (originalByteSequence, nameTag, japanese, english) in japaneseLines:
                writer.writerow({'Original Bytes' : originalByteSequence, 'Nametag' : nameTag, 'Japanese' : japanese, 'English' : ''})

puncutation = {
    '\x04' : 'Kill: ',
    '\x05' : 'Guul: ',
    '\x06' : 'Nose: ',
    '\x07' : 'Ray: ',
    '\x08' : 'Cain: ',
    '\x09' : 'Sally: ',
    '\x0A' : 'Cathy: ',
    '\x0B' : 'Man A: ',
    '\x0C' : 'Man B: ',
    '\x0D' : '\x81\x41',
    '\x0E' : '\x81\x64',
    '\x0F' : '\x81\x42',
    '\x10' : '\x81\x40',
    '\x11' : '\x81\x49',
    '\x12' : '\x81\x48',
    '\x13' : '\\n',
}

# TODO : Don't hardcode these!
# (but maybe it's good enough to just associate them with the MES file than parse how DotB actually does it)
nameTags = {
    '\x23' : 'Cole',
    '\x24' : 'Cooger',
    '\x25' : 'Sheila',
    '\x27' : 'Killer'
}

with open(filename, 'rb') as f:
    encodedMESbytes = f.read()
# get lines from bytes start marker BA 23-25 to end marker BA 26
# 23 == cole, 24 == doc, 25 == jack(?)

encodedJapaneseLines = []

# 11PLUS introduced another weird edge case - 08CD29100027?!
encodedJapaneseLines = encodedJapaneseLines + re.findall(br'\x08\xCD\x29\x10\x00\x27(.*?)(?:\xBA\x26)', encodedMESbytes)

# Nonstandard lines like the telephone ring/automated message are A8280f. This matches a bunch of other stuff so we're avoiding BB and D0 if they appear right afterwards.
# This should come first because dialogue boxes will also match second/third lines in these sorts of
# constructs, so the replace will modify one line in multi-line replacements.
# OOOOOO.MES contains A928 and A3B9
encodedJapaneseLines = encodedJapaneseLines + re.findall(br'\xA8\x28\x0F([^(?:\xA5{3,6})\xBB\xD0\x21].*?)(?:\x0C.)?(?:\x0D.)?(?:(?:\xBA\x26)|(?:\xA3\xFF\xFF)|(?:\xA3\xA4)|(?:\xC3\x23\x24)|(?:\xCD\x2A)|(?:\xC6\x28)|(?:\xA9\x28)|(?:\xA3\xB9)|(?:\x19\x90))', encodedMESbytes)

# Findall collides - meaning a previous match can influence another - ending on AB AA will screw it up if the next line
# starts with AA. Hence the replace below.

# One file will break without the BCA208 thing below, but then it doesn't match something with BCA219 in 000063. How to fix?
encodedMESbytes = encodedMESbytes.replace('\xAB\xAA','\xAB\xAB\xAA')
encodedJapaneseLines = encodedJapaneseLines + re.findall(br'\xAA\x28\x0E([^\xA5{3,6}\xA6\xAC\xAD\xAF\xB0\xB4\xB6\xC9\xC5\xC6\xCD\xCF\xD0](?:\xBC\xA2^\x08)?.*?)(?:\x0C.)?(?:(?:\xAB\xAB)|(?:\xBA\x26)|(?:\xA3?\xFF\xFF)|(?:\xA3\xA4)|(?:\xC3\x23\x24)|(?:\xCD\x2A)|(?:\x24\x24)|(?:\xC6\x28)|(?:\xD0\x73)|(?:\xAC\x28))', encodedMESbytes)


# This regex matches standard dialog boxes, usually BA23-25...BA26. But as you can see, they can also end on A3A3, A4, C92242 or C32324. Note A4 can also appear as <ELSE> mid-dialog.
# Note BA23-25 are nametags. They're technically not delimiters, but dialogue boxes can flow right after one another so BA26 may immediately be followed by BA23-25
encodedJapaneseLines = encodedJapaneseLines + re.findall(br'(\xBA[\x23\x24\x25\x27].*?)(?:\xBC\xA2)?(?:[\x0c\x0d].)?(?:\x19\x90)?(?:\x0c.)?(?:\x0d[\xf6-\xf8])?(?:(?:\xBA\x26)|(?:\xA3\xA3)|(?:\xC3[\x23-\x24]\x24)|(?:\xC1\x23)|(?:\xCC\x28\x14)|(?:\xD0\x73)|(?:\xD0\x23)|(?:\xC6\x28)|(?:\xA8\x28\x0F)|(?:\xBC\xA2\x0A\x59))', encodedMESbytes)

# As of 000039.MES, instead of nametag macros (BA23) it'll use BA2804-0C for nametag macros.
encodedJapaneseLines = encodedJapaneseLines + re.findall(br'(\xBA\x28[\x04-\x0C].*?)(?:\x0c.)?(?:\xD0\x24)?(?:\x19\x90)?(?:\x0d[\xf6-\xf8])?(?:(?:\xBA\x26)|(?:\xA3\xA3)|(?:\xC3[\x23-\x24]\x24)|(?:\xC4\x23\x23)|(?:\xC1[\x23\x24])|(?:\xCC\x28\x14)|(?:\xD0\x73)|(?:\xD0\x23))', encodedMESbytes)

# Nonstandard lines - usually with no nametag - start with A4AA280E...AC
# Options, like when you can pick "Leave for the corridor" or "Cancel" appear as 022CA2 ... A3. Note this is like the A2, A4, A3 if/else/endif construction, so 022C is the real delimiter
# Also OOOOOO.MES has these for NEW GAME, in English so let's exclude that.
encodedJapaneseLines = encodedJapaneseLines + re.findall(br'\x02\x2C\xA2([^\x21].*?)\xA3', encodedMESbytes)


# Oof, there's control codes for displaying an image mid-dialog box too!
# Okay, this collides with 000001.MES
encodedJapaneseLines = encodedJapaneseLines + re.findall(br'[^\x22-\x23]\xCF\x24\x23(.*?)(?:\x0c.)?\xBA\x26', encodedMESbytes)

# 000025.MES has an incredible thing where one half of a sentnce starts, there's an <IF> and if it succeeds, you get one
# entire cutscene which also includes an <ELSE>. Then you get the <ELSE> that matches the first <IF> and an alternate second
# half of a sentence.
# This is a hack to get around that while I discover if the game has more stuff like that in it.
encodedJapaneseLines = encodedJapaneseLines + re.findall(br'\x74\x41\x49\x32\x4c\xba\x28\x0e\xba\x28\x0e\xba\x28\x0e\xba\x28\x0f', encodedMESbytes)

# 000008.MES has a crappy one-off for zombie on the comms
encodedJapaneseLines = encodedJapaneseLines + re.findall(br'\xBC\xA2\x0A\x59\x81\x97\xD0\x73\x65\x20\x28\x1D\xA9\x23\x23\xA3(.*?)(?:\xBA\x26)', encodedMESbytes)

finalMES = encodedMESbytes

extractedLines = []
both = {}

if gotTranslation:
    translation = readEnglishFromTranslationFile()
    both = translation[0]
    englishLines = translation[1]

if encodedJapaneseLines:
    for result in encodedJapaneseLines:
        isPunctuation = False
        isControl = False
        isConditional = False
        isFlag = False
        isFirst = True
        couldBeNametag = False
        skip = False  # Skip is a misnomer, it actually collects the next byte
        sub = ''
        english = ''
        nameTag = ''
        originalByteSequence = result
        isQuote = False

        if gotTranslation:
            if (len(englishLines) > 0):
                finalMES = finalMES.replace(result, englishLines[0])
                del englishLines[0]

        result = re.sub(br'\xBC\xA2\x0C', b'\xBC', result) # Flag tests are multibyte and annoying to deal with so let's pare it down
        result = re.sub(br'\xBC\xA2\x08', b'\xB8', result) # Is this another flag test? Might be a setter? Not sure diff between 08 and 0C
        result = re.sub(br'\xBC\xA2\x19\x91', b'\xB1', result) # BC A2 19 91 - Found in 000066
        result = re.sub(br'\xBC\xA2\x19', b'\xB9', result) # BC A2 19 30 - Found in 000063
        result = re.sub(br'\xBC\xA2([^\x0C\x08])', b'\xBF\\1', result) # BCA2 by itself? It happens (000044)

        result = re.sub(br'\xA8\x28\x05', b'\xAB', result) # TODO: Remove this, just temp to debug this weird part
        result = re.sub(br'\xCF\x24\x23', b'\xCF', result) # C9-CF2423 defines an image which can appear mid dialog.
        result = re.sub(br'\xA8\x28\x0F', b'\xA8', result) # In 000008, A8280F seems to end a dialog box? Not really sure.
        result = re.sub(br'\xC5\x23\x28\x0F\xC5\x24\x23', b'\xC7', result) # In 000027, There's 2 in a row like this that collides with C5 replacement.
        result = re.sub(br'\xC5\x23\x28\x0F', b'\xC5', result) # In 17PLUS, looks kind of like a newline?
        result = re.sub(br'\x86\xA2',b'\x86', result) # In 000025, not sure. It's an EMDASH
        result = re.sub(br'\xA0\xA1',b'\xA0',result) # In 000029

        if debugBytes:
            print "----===----"

        for c in result:
            if c != '\xBA' and isFirst:
                isFirst = False
            if c == '\xBA' and isFirst:
                couldBeNametag = True
                isFirst = False

            if debugBytes:
                print (c,)
            if c == '\xBA' and not skip:    # control byte
                isControl = True
            elif skip:
                sub += c
                skip = False
            elif isFlag == True:
                # Turn the hex flag into a readable hex number. Translator, please C&P it!
                sub += c.encode()
                sub += '>'
                isFlag = False
                isConditional = True
            elif c == '\x19':
                sub += '<LAST '
                isFlag = True
            elif c == '\x86':
                sub += '<EMDASH>'
            elif c == '\xA0':
                sub += '<A0A1>'
            elif c == '\xC9':
                # Encountered in 000006 - When Cole looks at the letter, image comes inline with the dialog
                sub += "<IMAGE "
                isQuote = True
            elif c == '\xCF':
                sub += ">"
                isQuote = False
            elif isQuote:
                sub += c
            elif c == '\xB2':
                isConditional = True
            elif c == '\xB6':
                sub += '<B6>'
            elif c == '\xBC':
                # BC is a flag test and the following byte is which flag. Annoying,
                # but it happens mid text and we have to retain it, hence we turn on a
                # toggle to tell the reader that the next byte is the flag.
                sub += '<IF '
                isFlag = True
            elif c == '\xB8':
                sub += '<SET '
                isFlag = True
            elif c == '\xB1':
                sub += '<SETVAR91>'
            elif c == '\xB9':
                sub += '<SETVAR '
                isFlag = True
            elif c == '\xBF':
                sub += '<LONEIF>'
            elif c == '\xA8':
                sub += '<A828OF>'
            elif c == '\xA2' and isConditional:
                # If conditional, but there's no flag present. Not really sure how DotB knows
                # which flag to test in cases like this, honestly.
                sub += '<IF>'
            elif c == '\xA3':
                sub += '<ENDIF>'
                isConditional = False
            elif c == '\xA4':
                # Regardless of the conditional type, A4 is always an ELSE
                # In options, meaning when you can do things like "Leave or Cancel",
                # A4 is just a delimiter. I used '<>' originally but '<OR>' makes more sense.
                if isConditional:
                    sub += '<ELSE>'
                else:
                    sub += '<OR>'
            elif c == '\xA5':
                sub += '\n'
            elif c == '\xAB':
                # TODO: I'm a little worried about encountering AB as a control code later.
                # Probably a better way to do this but multibyte parsing mid-text makes this
                # uglier.
                sub += '<SPECIAL NEWLINE?>'
            elif c == '\x0C' and not isPunctuation: # This can be encountered if there's a variable set in the middle of text.
                sub += '<VAR '
                isFlag = True
            elif c == '\x0D' and not isPunctuation:
                sub += '<VAL '
                print "VAL"
                isFlag = True
            elif c == '\x08' and not isPunctuation: # Found in 000020.MES, looks like it's something that tages an argument.
                sub += '<TEST '
                isFlag = True
            elif c == '\xC5':
                sub += '<C523280F>'
            elif c == '\xC7':
                sub += '<C523280FC52423>'
            elif isControl and re.match('[\x23\x24\x25\x27]', c):   # dialog start cole
                if nameTag == '' and couldBeNametag:
                    nameTag = nameTags[c]
                    if nameTag == 'Sheila' and (mesName == 'MES_IN/OPEN_1' or mesName == 'MES_IN/OPEN_2'):
                        nameTag = 'Officer Jack'
                else:
                    sub += nameTags[c] + ': '
                isControl = False
                couldBeNametag = False
            elif isControl and c == '\x28':   # punctuation control byte
                isPunctuation = True
                isControl = False
            elif isPunctuation and re.match('[\x04-\x13]', c): # punctuation value
                sub += puncutation[c]
                isPunctuation = False
            elif re.match('[\x81-\x83,\x88-\x9F,\xE0-\xEA]', c):    # kana, kanji and some symbols - skip parsing next byte
                sub += c
                skip = True
            elif isPunctuation or isControl:
                print "ERROR isPunctuation/control byte skipped" + c.encode()
                isPunctuation = False
                isControl = False
            else:
                # hiragana char, prefix 82 and shift by 74 to get the SJIS value
                # print hex(ord(c))
                sub += '\x82' + chr(ord(c)+114)
        japanese = sub
        extractedText = (originalByteSequence, nameTag, japanese, english)
        extractedLines.append(extractedText)

writeJapaneseToTranslationFile(extractedLines, both)

if gotTranslation:
    print "Translating"
    outputFile = open(mesName + '.ENG.MES', 'w+b')
    finalMES = addNametags(finalMES)
    outputFile.write(finalMES)
    outputFile.close()
