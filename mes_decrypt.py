#!/usr/bin/python

#TODO: Genericize Nametags
#TODO: 000007 has an annoying <SET VAR><OR><NAMETAG> thing (0C__A4BA23)

import re
import csv
import os
import sys

import nametags

debugBytes = False  # Turn this on manually to export the bytes being read to standard out; useful if the script breaks
gotTranslation = False

#outputType = 'lined'
outputType = 'spreadsheet'

mesName = 'MES_IN/000006'
filename = mesName + '.MES'
transFile = mesName + '.ENG.CSV'

if os.path.exists(transFile):
    gotTranslation = True

def encodeEnglish(line):
    nametag = line["Nametag"]
    english = line["English"]

    english = '!' + english + '\x00'

    #TODO: I know, I know, I'm just testing eng insertion
    if nametag == 'Cole':
        english = '\xBA\x23' + english
    elif nametag == 'Cooger':
        english = '\xBA\x24' + english
    elif nametag == 'Officer Jack':
        english = '\xBA\x25' + english
    elif nametag == 'Sheila':
        english = '\xBA\x25' + english

    p = re.compile(r'<IF (.)>')
    english = p.sub(b'\x00\xBC\xA2\x0C\\1\x21', english)
    english = english.replace('<IF>',b'\x00\xA2\x21')
    english = english.replace('<ELSE>',b'\x00\xA4\x21')
    english = english.replace('<ENDIF>',b'\x00\xA3\x21')
    english = english.replace('<OR>',b'\x00\xA3\x21')
    english = english.replace('\\n',b'\xA5')
    english = english.replace('<SPECIAL NEWLINE?>',b'\xA8\x28\x05')

    return english

def readEnglishFromTranslationFile():
    englishLines = []
    if os.path.exists(transFile):
        with open(transFile) as csvfile:
            reader = csv.DictReader(csvfile)
            for line in reader:
                encodedEnglishLine = encodeEnglish(line)
                englishLines.append(encodedEnglishLine)
            return englishLines
    else:
        print "No translation file found " + transFile
# Function to handle writing the Japanese to a CSV. It supports the old 'linefile'
# format I used on Policenauts, but my translator asked for CSV so he could add notes, etc.
def writeJapaneseToTranslationFile(japaneseLines):
    if outputType == 'lined':
        for (nameTag, japanese, english) in japaneseLines:
            print (nameTag + ': ' + japanese + '\nEnglish: \n')
    elif outputType == 'spreadsheet':
        with open(mesName + '.CSV', 'w') as csvfile:
            fieldnames = 'Nametag','Japanese','English'
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            for (orig, nameTag, japanese, english) in japaneseLines:
                writer.writerow({'Nametag' : nameTag, 'Japanese' : japanese, 'English' : ''})
        with open(mesName + '.MASTER.CSV', 'w') as csvfile:
            fieldnames = 'Original Bytes','Nametag','Japanese','English'
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            for (originalByteSequence, nameTag, japanese, english) in japaneseLines:
                writer.writerow({'Original Bytes' : originalByteSequence, 'Nametag' : nameTag, 'Japanese' : japanese, 'English' : ''})

puncutation = {
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
    '\x25' : 'Officer Jack',
}

with open(filename, 'rb') as f:
    encodedMESbytes = f.read()
# get lines from bytes start marker BA 23-25 to end marker BA 26
# 23 == cole, 24 == doc, 25 == jack(?)

encodedJapaneseLines = []

# This regex matches standard dialog boxes, usually BA23-25...BA26. But as you can see, they can also end on A3A3, A4, C92242 or C32324. Note A4 can also appear as <ELSE> mid-dialog.
# Note BA23-25 are nametags. They're technically not delimiters, but dialogue boxes can flow right after one another so BA26 may immediately be followed by BA23-25
#encodedJapaneseLines = encodedJapaneseLines + re.findall(br'(\xBA[\x23-\x25].*?)(?:\x0c.)?(?:\x19\x90)?(?:\x0c.)?(?:(?:\xBA\x26)|(?:\xA3\xA3)|(?:\xA4\xBA[\x23-25])|(?:\xC9\x22\x42)|(?:\xC3\x23\x24))', encodedMESbytes)
encodedJapaneseLines = encodedJapaneseLines + re.findall(br'(\xBA[\x23-\x25].*?)(?:\x0c.)?(?:\x19\x90)?(?:\x0c.)?(?:(?:\xBA\x26)|(?:\xA3\xA3)|(?:\xC9\x22\x42)|(?:\xC3\x23\x24))', encodedMESbytes)

# Nonstandard lines - usually with no nametag - start with A4AA280E...AC
encodedJapaneseLines = encodedJapaneseLines + re.findall(br'\xA4\xAA\x28\x0E(.*?)\xAC', encodedMESbytes)

# Options, like when you can pick "Leave for the corridor" or "Cancel" appear as 022CA2 ... A3. Note this is like the A2, A4, A3 if/else/endif construction, so 022C is the real delimiter
encodedJapaneseLines = encodedJapaneseLines + re.findall(br'\x02\x2C\xA2(.*?)\xA3', encodedMESbytes)

# Nonstandard lines like the telephone ring/automated message are A8280f. This matches a bunch of other stuff so we're avoiding BB and D0 if they appear right afterwards.
encodedJapaneseLines = encodedJapaneseLines + re.findall(br'\xA8\x28\x0F([^\xBB\xD0].*?)(?:\x0c.)?\xBA\x26', encodedMESbytes)

# Oof, there's control codes for displaying an image mid-dialog box too!
encodedJapaneseLines = encodedJapaneseLines + re.findall(br'\xCF\x24\x23(.*?)(?:\x0c.)?\xBA\x26', encodedMESbytes)


finalMES = encodedMESbytes

extractedLines = []

if gotTranslation:
    englishLines = readEnglishFromTranslationFile()

if encodedJapaneseLines:
    for result in encodedJapaneseLines:
        isPunctuation = False
        isControl = False
        isConditional = False
        isFlagTest = False
        skip = False  # Skip is a misnomer, it actually collects the next byte
        sub = ''
        english = ''
        nameTag = ''
        originalByteSequence = result

#        print englishLines[0]
        if gotTranslation:
            if (len(englishLines) > 0):
                finalMES = finalMES.replace(result, englishLines[0])
                del englishLines[0]

        result = re.sub(br'\xBC\xA2\x0C', b'\xBC', result) # Flag tests are multibyte and annoying to deal with so let's pare it down
        result = re.sub(br'\xA8\x28\x05', b'\xAB', result) # TODO: Remove this, just temp to debug this weird part

        for c in result:
            if debugBytes:
                print (c,)
            if c == '\xBA' and not skip:    # control byte
                isControl = True
            elif skip:
                sub += c
                skip = False
            elif c == '\xB2':
                isConditional = True
            elif c == '\xBC':
                # BC is a flag test and the following byte is which flag. Annoying,
                # but it happens mid text and we have to retain it, hence we turn on a
                # toggle to tell the reader that the next byte is the flag.
                sub += '<IF '
                isFlagTest = True
            elif isFlagTest == True:
                # Turn the hex flag into a readable hex number. Translator, please C&P it!
                sub += c.encode()
                sub += '>'
                isFlagTest = False
                isConditional = True
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
            elif c== '\xAB':
                # TODO: I'm a little worried about encountering AB as a control code later.
                # Probably a better way to do this but multibyte parsing mid-text makes this
                # uglier.
                sub += '<SPECIAL NEWLINE?>'
            elif isControl and re.match('[\x23-\x25]', c):   # dialog start cole
                if nameTag == '':
                    nameTag = nameTags[c]
                else:
                    sub += nameTags[c] + ': '
                isControl = False
            elif isControl and c == '\x28':   # punctuation control byte
                isPunctuation = True
                isControl = False
            elif isPunctuation and re.match('[\x0D-\x13]', c): # punctuation value
                sub += puncutation[c]
                isPunctuation = False
            elif re.match('[\x81-\x83,\x88-\x9F,\xE0-\xEA]', c):    # kana, kanji and some symbols - skip parsing next byte
                sub += c
                skip = True
            elif isPunctuation or isControl:
                print "ERROR isPunctuation/control byte skipped"
                isPunctuation = False
                isControl = False
            else:
                # hiragana char, prefix 82 and shift by 74 to get the SJIS value
                sub += '\x82' + chr(ord(c)+114)
        japanese = sub
        extractedText = (originalByteSequence, nameTag, japanese, english)
        extractedLines.append(extractedText)

writeJapaneseToTranslationFile(extractedLines)

if gotTranslation:
    print "Translating"
    outputFile = open(mesName + '.ENG.MES', 'w+b')
    outputFile.write(finalMES)
    outputFile.close()
