#!/usr/bin/python

#TODO: Genericize Nametags
#TODO: Conditionals!

import re
import csv

debug = True

#outputType = 'lined'
outputType = 'spreadsheet'

mesName = '000001'
filename = mesName + '.MES'

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
    content = f.read()
# get lines from bytes start marker BA 23-25 to end marker BA 26
# 23 == cole, 24 == doc, 25 == jack(?)

results = []
results = results + re.findall(br'(\xBA[\x23-\x25].*?)(?:\x0c.)?(?:(?:\xBA\x26)|(?:\xA3\xA3))', content)
results = results + re.findall(br'\xA4\xAA\x28\x0E(.*?)\xAC', content)

extractedLines = []
if results:
    for result in results:
        isPunctuation = False
        isControl = False
        isConditional = False
        skip = False  # Skip is a misnomer, it actually collects the next byte
        sub = ''
        english = ''
        nameTag = ''
        originalByteSequence = result

        print ('')
        for c in result:
            if debug:
                print (c,)
            if c == '\xBA' and not skip:    # control byte
                isControl = True
            elif c == '\xB2':
                isConditional = True
            elif c == '\xA2' and isConditional:
                sub += '<IF>'
            elif c == '\xA3' and not isConditional:
                break
            elif c == '\xA4' and isConditional:
                sub += '<ELSE>'
            elif c == '\xA3' and isConditional:
                sub += '<ENDIF>'
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
            elif skip:
                sub += c
                skip = False
            elif re.match('[\x81-\x83,\x88-\x9F,\xE0-\xEA]', c):    # kana, kanji and some symbols - skip next byte
                sub += c
                skip = True
            elif isPunctuation or isControl:
                print "ERROR isPunctuation/control byte skipped"
                isPunctuation = False
                isControl = False
            else:
                # hiragana char, prefix 82 and shift by 74
                sub += '\x82' + chr(ord(c)+114)
        japanese = sub
        extractedText = (originalByteSequence, nameTag, japanese, english)
        extractedLines.append(extractedText)

writeJapaneseToTranslationFile(extractedLines)
