#!/usr/bin/python

#TODO: Genericize Nametags
# How this works.
# B9 23/24/25 sets the name tag.
# BA 23/24/25 uses it.
# Look for B9 25 to figure out the new nametag

#TODO: Extract these random control codes into a dictionary or function or something.

#TODO: 000063 is missing a big <IF>else construct at the end.

#TODO: BA28_ nametags
# 17PLUS has Nose

import re
import csv
import os
import sys
import argparse

import nametags

# 37 breaks stuff.
# With 38, 40, it's skipping game stuff now - most of the diary isn't read/photo isn't shown before we go to Cain.
# But 20, 30, 35, 36 work. Trying 36
#36: Is that everything?
#37: There's no doubt someone stole Doc's work...
#38: Should I re-read it?
maxEnglish = 10
skipThisLine = 2000

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

    names = ["Cole: ", "Cooger: ", "Sheila: ", "Killer: "]
    tags = [b'\x23', b'\x24', b'\x25', b'\x27']
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
    foundNewbox = False
    foundS = False
    foundSe = False
    foundSetOrOther = False

    if "in order here" in unbrokenLine:
        print unbrokenLine

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
#                count = countSinceIf
            elif c == 'E' and tagCount == 0:
                foundElseOrOther = True
            elif c == 'L' and tagCount == 1:
                foundElse = True
            elif c == 'N' and tagCount == 0:
                foundNewbox = True
            elif c == 'S' and tagCount == 0:
                foundS = True
            elif c == 'E' and tagCount == 1 and foundS:
                foundSe = True
            elif c == 'T' and tagCount == 2 and foundSe:
                foundSetOrOther = True
            else:
                foundSetOrOther = False
            tagCount = tagCount + 1

            if foundNewbox:
                numLines = 0
                linebreak = count + linewidth

        if c == '<':
            inTag = True
        if c == '>':
            if foundSetOrOther:
                foundIf = True
                countSinceIf = count
            inTag = False
            tagCount = 0
            if foundElse or foundOr:
                linebreak = count + linewidth

        count = count + 1

    if len(nametag) > 0:
        del line[0:len(nametag) + 2]

    brokenLine = ''.join(line)
    if "in order here" in brokenLine:
        print brokenLine
    return brokenLine

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

    p8 = re.compile(r'<LAST (.)>')
    english = p8.sub(b'\x00\x81\x97\x19\\1\x21', english)

    # The half-width english routine messes up control codes - 8140 is the hex for a Japanese space
    # Put one after a null to get things back to regular reading so control codes work again.

    english = english.replace('<IF>',b'\x00\x81\x40\xB2\xA2\x21')
    english = english.replace('<ELSE>',b'\x00\x81\x40\xA4\x21')
    english = english.replace('<ENDIF>',b'\x00\x81\x40\xA3\x21')
    english = english.replace('<OR>',b'\x00\x81\x40\xA4\x21')
    english = english.replace('\n',b'\x00\x81\x97\xBA\x28\x13\x21')
    english = english.replace('\\n',b'\x00\x81\x97\xBA\x28\x13\x21')
    english = english.replace('<SPECIAL NEWLINE?>',b'\x00\x81\x97\xA8\x28\x05\x21')
    english = english.replace('<A828OF>',b'\x00\x81\x97\xA8\x28\x0F\x21')
    english = english.replace('<A8280F>',b'\x00\x81\x97\xA8\x28\x0F\x21')
    english = english.replace('<C523280F>',b'\x00\x81\x97\xC5\x23\x28\x0F\x21')
    english = english.replace('<C523280FC52423>',b'\x00\x81\x97\xC5\x23\x28\x0F\xC5\x24\x23\x21')
    english = english.replace('<EMDASH>',b'\x00\x86\xA2\x21')
    english = english.replace('<A0A1>',b'\x00\x81\x40\xA0\xA1\x21')
    english = english.replace('<B6>',b'\x00\xB6\x21')
    english = english.replace('<LONEIF>',b'\x00\x81\x97\xBC\xA2\x21')
    english = english.replace('<BA27>',b'\xBA\x27')
    english = english.replace('<NEWBOX>',b'\x00\x81\x40\xBA\x26\x21')
    english = english.replace('<SETVAR91>', b'\x00\x81\x97\xBC\xA2\x19\x91\x21')
    english = english.replace('<BOX>', b'\x00\x81\x97\xBA\x26\xAA\x28\x0E\x21')
    english = english.replace(b'Quit\x00\x81\x97', b'Quit\x00\x81\x40') # One off case for the Game Overs which can't have 8197 after Quit
    english = english.replace(b'{}\x00\x81\x97', b'{}\x00\x81\x40') # One off case for the Game Overs which can't have 8197 after Quit
    english = english.replace(b'\xE3\x80\x80', '') #Some weirdo thing Google Sheets seems to do for no good reason.


    # I think I might want this one-off rather than try to output the endifs... maybe...
    # You're really looking for 0x008197A3A3 in 000029. That's both of these.
    english = english.replace(b'Is it cold in here or is it just me?\x00\x81\x97', b'Is it cold in here or is it just me?\x00\x81\x40')
    english = english.replace(b'\xA0\xA1\x21\x00\x81\x97', b'\xA0\xA1')

    # Ugly stuff around 000050 and 000051 complicated menu stuff.
    english = english.replace(b'!<TEST \x00\x81\x97\xBA\x28\x13!>', b'\x08\x0D!')
    english = english.replace(b'!<VAR \x00\x81\x97\xBA\x28\x13!>', b'\x0C\x0D!')
    english = english.replace(b'\x21\x00\x81\x97\x08\x0B', b'\x08\x0B')


    p85 = re.compile(r'(\xA4\x0C\x0D.*?\xA4)\x21\x00\x81\x97')
    english = p85.sub(b'\\1', english)

    p9 = re.compile(r'([\xA4\x16-\x1a])\x21\x00\x81\x97([\x08\x0c])')
    english = p9.sub(b'\\1\\2', english)

    if mesName == 'MES_IN/000039':  #TODO: Test drive this but it might be good for all files
        re.sub(r'(.*)\x81\x97', r'\1\x81\x40', english)

    nametag = ''

    return english

def readEnglishFromTranslationFile():
    englishLines = []
    japaneseEnglish = {}
    if os.path.exists(transFile):
        with open(transFile, 'rb') as csvfile:
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
englishCount = 0

encodedJapaneseLines = []

# 11PLUS introduced another weird edge case - 08CD29100027?!
encodedJapaneseLines = encodedJapaneseLines + re.findall(br'\x08\xCD\x29\x10\x00\x27(.*?)(?:\xBA\x26)', encodedMESbytes)

# Nonstandard lines like the telephone ring/automated message are A8280f. This matches a bunch of other stuff so we're avoiding BB and D0 if they appear right afterwards.
# This should come first because dialogue boxes will also match second/third lines in these sorts of
# constructs, so the replace will modify one line in multi-line replacements.
# OOOOOO.MES contains A928 and A3B9
# 000018.MES contains A5 for newlines (as does 000014 below). Excepting for now.
# 000025 - Dialogue boxes have no intro in Cole's eulogy. It just goes straight from BA26 right into dialogue. Jeez.
if mesName == 'MES_IN/000018':
    encodedJapaneseLines = encodedJapaneseLines + re.findall(br'\xA8\x28\x0F([^\xBB\xD0\x21].*?)(?:\x0C.)?(?:\x0D.)?(?:(?:\xBA\x26)|(?:\xA3\xFF\xFF)|(?:\xA3\xA4)|(?:\xC3\x23\x24)|(?:\xCD\x2A)|(?:\xC6\x28)|(?:\xA9\x28)|(?:\xA3\xB9)|(?:\x19\x90))', encodedMESbytes)
elif mesName == 'MES_IN/000025':
    encodedJapaneseLines = encodedJapaneseLines + re.findall(br'\xA8\x28\x0F([^\xBB\xD0\x21].*?)(?:\x0C.)?(?:\x0D.)?(?:(?:\xA3\xFF\xFF)|(?:\xA3\xA4)|(?:\xC3\x23\x24)|(?:\xCD\x2A)|(?:\xC6\x28)|(?:\xA9\x28)|(?:\xA3\xB9)|(?:\x19\x90))', encodedMESbytes)
else:
    encodedJapaneseLines = encodedJapaneseLines + re.findall(br'\xA8\x28\x0F([^(?:\xA5{3,6})\xBB\xD0\x21].*?)(?:\x0C.)?(?:\x0D.)?(?:(?:\xBA\x26)|(?:\xA3\xFF\xFF)|(?:\xA3\xA4)|(?:\xC3\x23\x24)|(?:\xCD\x2A)|(?:\xC6\x28)|(?:\xA9\x28)|(?:\xA3\xB9)|(?:\x19\x90))', encodedMESbytes)

# Findall collides - meaning a previous match can influence another - ending on AB AA will screw it up if the next line
# starts with AA. Hence the replace below.

# One file will break without the BCA208 thing below, but then it doesn't match something with BCA219 in 000063. How to fix?
# Negating C52424 for an edge case in 000012
encodedMESbytes = encodedMESbytes.replace('\xAB\xAA','\xAB\xAB\xAA')
if mesName == 'MES_IN/OPEN_2':
    encodedJapaneseLines = encodedJapaneseLines + re.findall(br'\xAA\x28\x0E([^\xA5{3,6}\xA6\xAC\xAD\xAF\xB0\xB4\xB6\xC9\xC5\xC6\xCD\xCF\xD0].*?)(?:(?:\xAB\xAB)|(?:\xBA\x26)|(?:\xA3?\xFF\xFF)|(?:\xA3\xA4)|(?:\xC3\x23\x24)|(?:\xCD\x2A)|(?:\x24\x24)|(?:\xC6\x28)|(?:\xD0\x73)|(?:\xAC\x28)|(?:\xA3\xA3))', encodedMESbytes)
elif mesName == 'MES_IN/10PLUS' or mesName == 'MES_IN/11PLUS':
    encodedJapaneseLines = encodedJapaneseLines + re.findall(br'\xAA\x28\x0E([^\xA5{3,6}\xA6\xAC\xAD\xAF\xB0\xB4\xB6\xC9\xC5\xC6\xCD\xCF\xD0].*?)(?:\x0C.)?(?:(?:\xAB\xAB)|(?:\xBA\x26)|(?:\xA3?\xFF\xFF)|(?:\xA3\xA4)|(?:\xC3\x23\x24)|(?:\xCD\x2A)|(?:\x24\x24)|(?:\xC6\x28)|(?:\xD0\x73)|(?:\xAC\x28)|(?:\xA3\xA3))', encodedMESbytes)
elif mesName == 'MES_IN/000014' or mesName == 'MES_IN/000054' or mesName == 'MES_IN/000063':
    encodedJapaneseLines = encodedJapaneseLines + re.findall(br'\xAA\x28\x0E([^\xA6\xAC\xAD\xAF\xB0\xB4\xB6\xC9\xC5\xC6\xCD\xCF\xD0].*?)(?:\x0C.)?(?:(?:\xAB\xAB)|(?:\xBA\x26)|(?:\xA3?\xFF\xFF)|(?:\xA3\xA4)|(?:\xC3\x23\x24)|(?:\xCD\x2A)|(?:\x24\x24)|(?:\xC6\x28)|(?:\xD0\x73)|(?:\xAC\x28)|(?:\xA3\xA3))', encodedMESbytes)
else:
    encodedJapaneseLines = encodedJapaneseLines + re.findall(br'\xAA\x28\x0E([^\xA5{3,6}\xA6\xAC\xAD\xAF\xB0\xB4\xB6\xC9\xC5\xC6\xCD\xCF\xD0](?:\xBC\xA2^\x08).*?)(?:\x0C.)?^(\xC5\x24\x24)?(?:(?:\xAB\xAB)|(?:\xBA\x26)|(?:\xA3?\xFF\xFF)|(?:\xA3\xA4)|(?:\xC3\x23\x24)|(?:\xCD\x2A)|(?:\x24\x24)|(?:\xC6\x28)|(?:\xD0\x73)|(?:\xAC\x28)|(?:\xA3\xA3))', encodedMESbytes)
encodedMESbytes = encodedMESbytes.replace('\xAB\xAB\xAA','\xAB\xAA')

# This regex matches standard dialog boxes, usually BA23-25...BA26. But as you can see, they can also end on A3A3, A4, C92242 or C32324. Note A4 can also appear as <ELSE> mid-dialog.
# Note BA23-25 are nametags. They're technically not delimiters, but dialogue boxes can flow right after one another so BA26 may immediately be followed by BA23-25
if mesName == "MES_IN/000030":
    encodedJapaneseLines = encodedJapaneseLines + re.findall(br'(\xBA[\x23\x24\x25\x27].*?)(?:\xBC\xA2)?(?:\x19\x90)?(?:\x0C.)?(?:\x0A\x59)?(?:\x0D[\xF6-\xF8])?(?:\x81\x97)?(?:(?:\xBA\x26)|(?:\xA3\xA3)|(?:\xC3[\x23-\x24]\x24)|(?:\xC1\x23)|(?:\xCC\x28\x14)|(?:\xD0\x73)|(?:\xD0\x23)|(?:\xC6\x28)|(?:\xA8\x28\x0F)|(?:\xBA\x28\x13\xBA\x28[\x04-\x0C]))', encodedMESbytes)
else:
    encodedJapaneseLines = encodedJapaneseLines + re.findall(br'(\xBA[\x23\x24\x25\x27].*?)(?:\xBC\xA2)?(?:\x19\x90)?(?:\x0C.)?(?:\x0A\x59)?(?:\x0D[\xF6-\xF8])?(?:\x81\x97)?(?:(?:\xBA\x26)|(?:\xA3\xA3)|(?:\xC3[\x23-\x24]\x24)|(?:\xC1\x23)|(?:\xCC\x28\x14)|(?:\xD0\x73)|(?:\xD0\x23)|(?:\xC6\x28)|(?:\xA8\x28\x0F))', encodedMESbytes)

# As of 000028.MES, instead of nametag macros (BA23-25,BA27) it'll use BA2804-0C for nametag macros.
encodedJapaneseLines = encodedJapaneseLines + re.findall(br'(\xBA\x28[\x04-\x0C].*?)(?:\x0c.)?(?:\xD0\x24)?(?:\x19\x90)?(?:\x0d[\xf6-\xf8])?(?:(?:\xBA\x23)|(?:\xBA\x26)|(?:\xA3\xA3)|(?:\xC3[\x23-\x24]\x24)|(?:\xC4\x23\x23)|(?:\xC1[\x23\x24])|(?:\xCC\x28\x14)|(?:\xD0\x73)|(?:\xD0\x23))', encodedMESbytes)


# Nonstandard lines - usually with no nametag - start with A4AA280E...AC
# Options, like when you can pick "Leave for the corridor" or "Cancel" appear as 022CA2 ... A3. Note this is like the A2, A4, A3 if/else/endif construction, so 022C is the real delimiter
# Also OOOOOO.MES has these for NEW GAME, in English so let's exclude that.
encodedJapaneseLines = encodedJapaneseLines + re.findall(br'\x02\x2C\xA2([^\x21].*?)\xA3', encodedMESbytes)


# Oof, there's control codes for displaying an image mid-dialog box too!
# Okay, this collides with 000001.MES
encodedJapaneseLines = encodedJapaneseLines + re.findall(br'[^\x22-\x23]\xCF\x24\x23(.*?)(?:\x0c.)?\xBA\x26', encodedMESbytes)

# 000025.MES has an incredible thing where one half of a sentence starts, there's an <IF> and if it succeeds, you get one
# entire cutscene which also includes an <ELSE>. Then you get the <ELSE> that matches the first <IF> and an alternate second
# half of a sentence.
# This is a hack to get around that while I discover if the game has more stuff like that in it.
encodedJapaneseLines = encodedJapaneseLines + re.findall(br'\x74\x41\x49\x32\x4c\xba\x28\x0e\xba\x28\x0e\xba\x28\x0e\xba\x28\x0f', encodedMESbytes)

# 000008.MES has a crappy one-off for zombie on the comms
encodedJapaneseLines = encodedJapaneseLines + re.findall(br'\xBC\xA2\x0A\x59\x81\x97\xD0\x73\x65\x20\x28\x1D\xA9\x23\x23\xA3(.*?)(?:\xBA\x26)', encodedMESbytes)

# 000028.MES has an annoying one-off for Sheila's Note, also 000050-51 have Doc's diary which works like that.
encodedJapaneseLines = encodedJapaneseLines + re.findall(br'(\x81\x77.*?\x81\x78)(?:\xBA\x26)', encodedMESbytes)

# 000029.MES has an annoying one-off for Cole's knocking.
encodedJapaneseLines = encodedJapaneseLines + re.findall(br'\xBA\x26(\x83\x52.*?)(?:\xBA[\x23\x26])', encodedMESbytes)
encodedJapaneseLines = encodedJapaneseLines + re.findall(br'\xBA\x26(\x8F\x97.*?)(?:\xBA[\x23\x26])', encodedMESbytes)
# 000030.MES has one for Cole just out of nowhere without a nametag
encodedJapaneseLines = encodedJapaneseLines + re.findall(br'\xC5\x23\x23(\x83\x52.*?)(?:\xAD\x28)', encodedMESbytes)
# 000039.MES has a one-off for Sheila (Woman)
encodedJapaneseLines = encodedJapaneseLines + re.findall(br'\xBA\x26(\x8F\x97.*?)(?:\xBA\x26)', encodedMESbytes)

# 000054.MES has one-offs for Cain
encodedJapaneseLines = encodedJapaneseLines + re.findall(br'\xBA\x26(\x83\x50.*?)(?:\xBA[\x23\x26])', encodedMESbytes)
encodedJapaneseLines = encodedJapaneseLines + re.findall(br'\x81\x42\xBA\x26(\x83\x52.*?\x81\x49\x81\x49)(?:\xBA\x26)', encodedMESbytes)
encodedJapaneseLines = encodedJapaneseLines + re.findall(br'\x81\x48\xBA\x26(\x83\x50.*?\x81\x49\x81\x49)(?:\xBA\x26)', encodedMESbytes)

if mesName == 'MES_IN/000058':
    encodedJapaneseLines = encodedJapaneseLines + re.findall(br'\xD0\x23(\x89.*?)(?:\xBA\x26)',
                                                             encodedMESbytes)
    encodedJapaneseLines = encodedJapaneseLines + re.findall(br'\xBA\x26(\x83\x6D.*?)(?:\xBA[\x23\x26])', encodedMESbytes)
    encodedJapaneseLines = encodedJapaneseLines + re.findall(br'\xBA\x26(\x2E\x5A.*?)(?:\xBA[\x23\x26])', encodedMESbytes)
    encodedJapaneseLines = encodedJapaneseLines + re.findall(br'\xBA\x26(\x94\xDE.*?)(?:\xBA[\x23\x26])', encodedMESbytes)

if mesName == 'MES_IN/000059':
    encodedJapaneseLines = encodedJapaneseLines + re.findall(br'\xBA\x26(\x89\xB4\x5B\x8A.*?)(?:\xBA[\x23\x26])', encodedMESbytes)
    encodedJapaneseLines = encodedJapaneseLines + re.findall(br'\xBA\x26(\x89\xB4.*?)(?:\x0D\xF9)?(?:\xBA[\x23\x26])', encodedMESbytes)
    encodedJapaneseLines = encodedJapaneseLines + re.findall(br'\xBA\x26(\x83\x56.*?)(?:\xBA[\x23\x26])', encodedMESbytes)

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
            if (len(englishLines) > 0) and englishCount < maxEnglish:
                if englishCount == maxEnglish - 1:
                    print englishLines[0]
                finalMES = finalMES.replace(result, englishLines[0], 1)
                del englishLines[0]
            englishCount = englishCount + 1

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
                sub += '<A8280F>'
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
            elif isControl and c == '\x26':
                sub += "<NEWBOX>"
                isControl = False
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
                print "ERROR isPunctuation/control byte skipped 0x" + c.encode("hex")
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

#    if mesName == "MES_IN/000053":
#        finalMES = finalMES.replace(b'\x81\x97', b'\x81\x40')

    if mesName == "MES_IN/OPEN_2":
        finalMES = finalMES
    else:
        finalMES = addNametags(finalMES)

    outputFile.write(finalMES)
    outputFile.close()
