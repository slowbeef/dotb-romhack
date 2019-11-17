import os, sys, binascii
from shutil import copyfileobj

path=sys.argv[1]
parentfile=open(path.strip(" output"),"wb+")
filename = [filename.rstrip('\n') for filename in open(sys.argv[1]+"\\fileorder", "r")]
startloc = [0] * (len(filename))
endloc = []
count = 0
count2 = 0
data = ""
header = ""
location = [""] * 8

# Create initial header
while count < len(filename):
    headerlist = ["\x00"] * 16
    currentfile = list(filename[count])
    while count2 < len(currentfile):
        headerlist[count2] = currentfile[count2]
        count2 += 1
    header = "".join(headerlist)
    data += header
    del headerlist[:]
    count2 = 0
    count += 1
count = 0
data += "\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
parentfile.write(bytes(data, 'ascii'))
startloc[0]=hex(len(data))

#Slap data on to file
while count < len(filename):
    print("Doing",path+"\\"+filename[count])
    tmpfile=open(path+"\\"+filename[count],"rb")
    copyfileobj(tmpfile,parentfile)
    parentfile.seek(0, os.SEEK_END)
    if count+1 < len(filename):
        startloc[count+1] = hex(parentfile.tell())
    else:
        endloc = hex(parentfile.tell())
    count += 1
count=0


#Go back and put the locations in the header
parentfile.seek(0)
while count < len(filename):
    parentfile.seek(12,1)
    startloclist=list(startloc[count])
    if (len(startloclist)) == 4:
        location = [startloclist[2],startloclist[3],"0","0","0","0","0","0"]
    if (len(startloclist)) == 5:
        location = [startloclist[3],startloclist[4],"0",startloclist[2],"0","0","0","0"]
    if (len(startloclist)) == 6:
        location = [startloclist[4],startloclist[5],startloclist[2],startloclist[3],"0","0","0","0"]
    if (len(startloclist)) == 7:
        location = [startloclist[5],startloclist[6],startloclist[3],startloclist[4],"0",startloclist[2],"0","0"]
    locationst="".join(location)
    parentfile.write(binascii.unhexlify(locationst))
    count += 1
parentfile.seek(12,1)
startloclist=list(endloc)
location = [startloclist[5],startloclist[6],startloclist[3],startloclist[4],"0",startloclist[2],"0","0"]
locationst="".join(location)
parentfile.write(binascii.unhexlify(locationst))
parentfile.close()
    

    

print("We wrote",filename,"to",parentfile,"and these locations",startloc,"ending at",endloc)
parentfile.close()
