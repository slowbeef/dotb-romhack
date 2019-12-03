#!/usr/bin/python

#TODO: Genericize Nametags
#TODO: Extract these random control codes into a dictionary or function or something.

#TODO: Multilines seem like they don't work - possibly because second line gets caught in results first?

import re
import csv
import os
import sys
import argparse

import nametags

debugBytes = True  # Turn this on manually to export the bytes being read to standard out; useful if the script breaks
gotTranslation = False

#outputType = 'lined'
outputType = 'spreadsheet'

#000030 still has a problem
#000041 still has a problem
#000044 still has a problem
#000045 still has a problem... and beyond. A lot look like the same problem.
#000020 has weird bytes in the import - A lot of those weird test variables?
#Nothing in 38?
mesName = 'MES_IN/000020'

parser = argparse.ArgumentParser(description='MES files to pass in')
parser.add_argument("-m", default="MES_IN/000001", help="This is the name of the MES file with the directory it's in (and where to put stuff)")
args = parser.parse_args()
mesName = args.m

filename = mesName + '.MES'
transFile = mesName + '.ENG.CSV'



if os.path.exists(transFile):
    gotTranslation = True

def encodeEnglish(line):
    nametag = line["Nametag"]
    english = line["English"]

    english = '!' + english + '\x00\x81\x40'

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

    p2 = re.compile(r'<IMAGE ("[^"]+")')
    english = p2.sub(b'\x00\x81\x40\xC9\\1\xCF\x24\x23\x21',english)

    p3 = re.compile(r'<VAR (.)>')
    english = p3.sub(b'\x00\x81\x40\x0C\\1\x21', english)

    p4 = re.compile(r'<TEST (.)>')
    english = p4.sub(b'\x00\x81\x40\x08\\1\x21', english)

    p5 = re.compile(r'<VAL (.)>')
    english = p5.sub(b'\x00\x81\x40\x0D\\1\x21', english)

    p6 = re.compile(r'<SET (.)>')
    english = p6.sub(b'\x00\x81\x40\xB8\\1\x21', english)

    # The half-width english routine messes up control codes - 8140 is the hex for a Japanese space
    # Put one after a null to get things back to regular reading so control codes work again.

    english = english.replace('<IF>',b'\x00\x81\x40\xB2\xA2\x21')
    english = english.replace('<ELSE>',b'\x00\x81\x40\xA4\x21')
    english = english.replace('<ENDIF>',b'\x00\x81\x40\xA3\x21')
    english = english.replace('<OR>',b'\x00\x81\x40\xA4\x21')
    english = english.replace('\n',b'\x00\x81\x40\xBA\x28\x13\x21')
    english = english.replace('\\n',b'\x00\x81\x40\xBA\x28\x13\x21')
    english = english.replace('<SPECIAL NEWLINE?>',b'\x00\x81\x40\xA8\x28\x05\x21')
    english = english.replace('<A828OF>',b'\x00\x81\x40\xA8\x28\x0F\x21')
    english = english.replace('<C523280f>',b'\x00\x81\x40\xC5\x23\x28\x0F\x21')
    english = english.replace('<86A2>',b'\x00\x86\xA2\x21')
    english = english.replace('<A0A1>',b'\x00\xA0\xA1\x21')

    #Cleanup
#    english = english.replace(b'\x81\x40\xBA\x26', b'\xBA\x26')
#    english = english.replace(b'\x21\x00', '')
    nametag = ''

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
    '\x04' : 'Kill: ',
    '\x05' : 'Guul: ',
    '\x06' : 'Nose: ',
    '\x07' : 'Ray: ',
    '\x08' : 'Cain: ',
    '\x09' : 'Sally: ',
    '\x0A' : 'Cathy: ',
    '\x0B' : 'Man A: ',
    '\x0C' : 'Main B: ',
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


# Nonstandard lines like the telephone ring/automated message are A8280f. This matches a bunch of other stuff so we're avoiding BB and D0 if they appear right afterwards.
# This should come first because dialogue boxes will also match second/third lines in these sorts of
# constructs, so the replace will modify one line in multi-line replacements.
encodedJapaneseLines = encodedJapaneseLines + re.findall(br'\xA8\x28\x0F([^\xBB\xD0\x21].*?)(?:\x0C.)?(?:\x0D.)?(?:(?:\xBA\x26)|(?:\xA3\xFF\xFF)|(?:\xA3\xA4)|(?:\xC3\x23\x24)|(?:\xCD\x2A))', encodedMESbytes)

encodedJapaneseLines = encodedJapaneseLines + re.findall(br'[\xA8\xAA]\x28\x0E([^\xA6\xAC\xAF\xB0\xB4\xB6\xCD\xC9\xC5-\xC6\xD0(\xBC\xA2\x08)].*?)(?:\x0C.)?(?:(?:\xAB\xAA)|(?:\xBA\x26)|(?:\xA3?\xFF\xFF)|(?:\xA3\xA4)|(?:\xC3\x23\x24)|(?:\xCD\x2A))', encodedMESbytes)

# This regex matches standard dialog boxes, usually BA23-25...BA26. But as you can see, they can also end on A3A3, A4, C92242 or C32324. Note A4 can also appear as <ELSE> mid-dialog.
# Note BA23-25 are nametags. They're technically not delimiters, but dialogue boxes can flow right after one another so BA26 may immediately be followed by BA23-25
#encodedJapaneseLines = encodedJapaneseLines + re.findall(br'(\xBA[\x23-\x25].*?)(?:\x0c.)?(?:\x19\x90)?(?:\x0c.)?(?:(?:\xBA\x26)|(?:\xA3\xA3)|(?:\xA4\xBA[\x23-25])|(?:\xC9\x22\x42)|(?:\xC3\x23\x24))', encodedMESbytes)
#encodedJapaneseLines = encodedJapaneseLines + re.findall(br'(\xBA[\x23-\x25].*?)(?:\x0c.)?(?:\x19\x90)?(?:\x0c.)?(?:(?:\xBA\x26)|(?:\xA3\xA3)|(?:\xC9\x22\x42)|(?:\xC3\x23\x24))', encodedMESbytes)
encodedJapaneseLines = encodedJapaneseLines + re.findall(br'(\xBA[\x23-\x25].*?)(?:\x0c.)?(?:\x19\x90)?(?:\x0c.)?(?:\x0d\xf6)?(?:(?:\xBA\x26)|(?:\xA3\xA3)|(?:\xC3[\x23-\x24]\x24)|(?:\xC1\x23)|(?:\xCC\x28\x14))', encodedMESbytes)

# As of 000039.MES, instead of nametag macros (BA23) it'll use BA2804-0C for nametag macros.
encodedJapaneseLines = encodedJapaneseLines + re.findall(br'(\xBA\x28[\x04-\x0C].*?)(?:\x0c.)?(?:\xD0\x24)?(?:\x19\x90)?(?:\x0d\xf6)?(?:(?:\xBA\x26)|(?:\xA3\xA3)|(?:\xC3[\x23-\x24]\x24)|(?:\xC1\x23)|(?:\xCC\x28\x14))', encodedMESbytes)

# Nonstandard lines - usually with no nametag - start with A4AA280E...AC
#encodedJapaneseLines = encodedJapaneseLines + re.findall(br'\xAA\x28\x0E(.*?)(?:(?:\xBA\x26)|(?:\xAC)|(?:\xFF\xFF))', encodedMESbytes)
# Options, like when you can pick "Leave for the corridor" or "Cancel" appear as 022CA2 ... A3. Note this is like the A2, A4, A3 if/else/endif construction, so 022C is the real delimiter
encodedJapaneseLines = encodedJapaneseLines + re.findall(br'\x02\x2C\xA2(.*?)\xA3', encodedMESbytes)


# Oof, there's control codes for displaying an image mid-dialog box too!
# Okay, this collides with 000001.MES
encodedJapaneseLines = encodedJapaneseLines + re.findall(br'[^\x22-\x23]\xCF\x24\x23(.*?)(?:\x0c.)?\xBA\x26', encodedMESbytes)


finalMES = encodedMESbytes

extractedLines = []

if gotTranslation:
    englishLines = readEnglishFromTranslationFile()

if encodedJapaneseLines:
    for result in encodedJapaneseLines:
        isPunctuation = False
        isControl = False
        isConditional = False
        isFlag = False
        skip = False  # Skip is a misnomer, it actually collects the next byte
        sub = ''
        english = ''
        nameTag = ''
        originalByteSequence = result
        isQuote = False

#        print englishLines[0]
        if gotTranslation:
            if (len(englishLines) > 0):
                finalMES = finalMES.replace(result, englishLines[0])
                del englishLines[0]

        result = re.sub(br'\xBC\xA2\x0C', b'\xBC', result) # Flag tests are multibyte and annoying to deal with so let's pare it down
        result = re.sub(br'\xBC\xA2\x08', b'\xB8', result) # Is this another flag test? Might be a setter? Not sure diff between 08 and 0C

        result = re.sub(br'\xA8\x28\x05', b'\xAB', result) # TODO: Remove this, just temp to debug this weird part
        result = re.sub(br'\xCF\x24\x23', b'\xCF', result) # C9-CF2423 defines an image which can appear mid dialog.
        result = re.sub(br'\xA8\x28\x0F', b'\xA8', result) # In 000008, A8280F seems to end a dialog box? Not really sure.
        result = re.sub(br'\xC5\x23\x28\x0F', b'\xC5', result) # In 17PLUS, looks kind of like a newline?
        result = re.sub(br'\x86\xA2',b'\x86', result) # In 000025, not sure. It's mid text.
        result = re.sub(br'\xA0\xA1',b'\xA0',result) # In 000029

        if debugBytes:
            print "----===----"

        for c in result:
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
            elif c == '\x86':
                sub += '<86A2>'
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
            elif c == '\xBC':
                # BC is a flag test and the following byte is which flag. Annoying,
                # but it happens mid text and we have to retain it, hence we turn on a
                # toggle to tell the reader that the next byte is the flag.
                sub += '<IF '
                isFlag = True
            elif c == '\xB8':
                sub += '<SET '
                isFlag = True
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
            elif isControl and re.match('[\x23-\x25]', c):   # dialog start cole
                if nameTag == '':
                    nameTag = nameTags[c]
                else:
                    sub += nameTags[c] + ': '
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

writeJapaneseToTranslationFile(extractedLines)

if gotTranslation:
    print "Translating"
    outputFile = open(mesName + '.ENG.MES', 'w+b')
    outputFile.write(finalMES)
    outputFile.close()
