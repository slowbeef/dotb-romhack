import os, sys

file = open(sys.argv[1], 'rb+')
filename = []
startloc = []
endloc = []
finished = False
count = 0
path = sys.argv[1] + " output"

def oddswap(st):
    s = list(st)
    t = [s[6], s[7], s[4], s[5], s[2], s[3], s[0], s[1]]
    s = "".join(t)
    return s

def readline():
    return file.read(16)

# grab the file information from the header stop when null hit
for line in iter(readline, ''):
    if not finished:
        if line[:10] != b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00":
            filename.append(line[:12].decode().rstrip('\x00'))
            startloc.append(oddswap(line[-4:].hex()))
        else:
            endloctemp =line[-4:].hex()
            endloc = oddswap(line[-4:].hex())
            finished = True
            break
print("The files are ",filename," files at ",startloc," and ends at ",endloc)

try:
    os.mkdir(path)
except OSError:
    print ("Creation of the directory %s failed" % path)
else:
    print ("Successfully created the directory %s " % path)

# store the chunks of data as their files
while count < len(filename):
    file.seek(int("0x" + startloc[count], 16))
    if count+1 < len(filename):
        temploc = int("0x" + startloc[count+1], 16)
        temploc = temploc - int("0x" + startloc[count], 16)
        readfile = file.read(temploc)
    else:
        temploc = int("0x" + endloc, 16) - int("0x" + startloc[count], 16)
        readfile = file.read(temploc)
    destination = path + "\\" + filename[count]
    read = open(destination, "wb")
    read.write(readfile)
    read.close
    print("Wrote",filename[count], "with the file size",temploc, "bytes")
    count += 1

# store the order of files for archiving in a file named fileorder
destination = path + "\\fileorder"
with open(destination, "w") as read:
    for item in filename:
        read.write("%s\n" % item)
read.close
file.close
