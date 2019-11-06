#!/usr/bin/python

import re

#outputType = 'lined'
outputType = 'spreadsheet'

filename = './OPEN_1.MES'
with open(filename, 'rb') as f:
    content = f.read()
# get lines from bytes start marker BA 23-25 to end marker BA 26
# 23 == cole, 24 == doc, 25 == jack(?)
results = re.findall(br'(\xBA[\x23-\x25].*?)\xBA\x26', content)
if results:
    if outputType == 'spreadsheet':
        print "Nametag,Japanese,English"
    for r in results:
        # print repr(r)
        # r = results[0]
        sym = False
        control = False
        skip = False
        sub = ''
        for c in r:
            if c == '\xBA' and not skip:    # control byte
                control = True
            elif control and c == '\x23':   # dialog start cole
                if outputType == 'lined':
                    sub += '\x83\x52\x81\x5B\x83\x8B\x81\x46'
                elif outputType == 'spreadsheet':
                    sub += 'Cole,'
                control = False
            elif control and c == '\x24':   # dialog start doc
                if outputType == 'lined':
                    sub += '\x83\x4E\x81\x5B\x83\x4B\x81\x5B\x81\x46'
                elif outputType == 'spreadsheet':
                    sub += 'Cooger,'
                control = False
            elif control and c == '\x25':   # dialog start jack?
                if outputType == 'lined':
                    sub += '\x81\x5B\x81\x46'
                elif outputType == 'spreadsheet':
                    sub += 'Officer Jack,'
                control = False
            elif control and c == '\x26':   # dialog end
                control = False
            elif control and c == '\x28':   # symbol byte
                sym = True
                control = False
            elif sym and c == '\x0D':       # comma
                sub += '\x81\x41'
                sym = False
            elif sym and c == '\x0E':       # ..
                sub += '\x81\x64'
                sym = False
            elif sym and c == '\x0F':       # period
                sub += '\x81\x42'
                sym = False
            elif sym and c == '\x10':       # space
                sub += '\x81\x40'
                sym = False
            elif sym and c == '\x11':       # !
                sub += '\x81\x49'
                sym = False
            elif sym and c == '\x12':       # ?
                sub += '\x81\x48'
                sym = False
            elif sym and c == '\x13':       # newline for two characted dialog in one box
                sub += '\n'
                sym = False
            elif skip:
                sub += c
                skip = False
            elif re.match('[\x81-\x83,\x88-\x9F,\xE0-\xEA]', c):    # kana, kanji and some symbols - skip next byte
                sub += c
                skip = True
            elif sym or control:
                print "ERROR sym/control byte skipped"
                sym = False
                control = False
            else:
                # hiragana char, prefix 82 and shift by 74
                sub += '\x82' + chr(ord(c)+114)
        if outputType == 'lined':
            sub += '\n'
            print (sub.decode('shift-jis')).encode('utf-8', 'ignore') + 'English: \n'
        elif outputType == 'spreadsheet':
            print (sub.decode('shift-jis')).encode('utf-8', 'ignore') + ','
