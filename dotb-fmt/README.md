# dotb-fmt
Supplementary tools for FM-Towns Dead of the Brain

These two scripts can be used to extract as well as recreate the archived files used on the FM-Towns release. Once extracted the files are the same as PC-98 and should be able to have the translation patch applied. Two scripts are included. fmt-builder.py and fmt-extractor.py

# fmt-extractor.py

Simply call a file with the script to have it extracted to a folder named "<FILENAME> output" along with an order list inside the folder named "filelist". You can also drag & drop a file to have it extract.

> fmt-extractor.py BRAIN.003

# fmt-builder.py

Simply call the script with a directory to have it recreated as the original file. The script will read the filelist to mash up all the files and recreate the header. You can also drag & drop folders to have them rebuilt.

> fmt-builder.py "BRAIN.003 output"

Please note that these were made with Windows in mind and probably won't work on other operating systems.