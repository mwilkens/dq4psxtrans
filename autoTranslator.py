import io
from difflib import SequenceMatcher
from os import walk

# Dialog format mapping
dialogMap = {
    '\n\t': '{7f02}',
    '\n': '{0000}', # might be dangerous
    r'%a00090': '{7f1f}',
    '＊「': '',
    'アリーナ': '{7f21}' # Not sure about this one but I've seen it
}

# Searches a binary file for next instance of a certain text/hex/etc
'''
def seekText( fh, text ):
    length = len(text)
    found_text = False
    while not found_text:
        search = fh.read(length)
        if( len(search) != length ):
            return -1
        fh.seek(-(length-1),1)
        if( text in search):
            fh.seek(-1,1)
            found_text = True
            return fh.tell()
'''

def seekText( fh, text ):
    found_text = False
    startPtr = fh.tell()
    offset = 0
    while not found_text:
        start = fh.tell()
        chunk = fh.read(512)
        if start == fh.tell():
            return -1
        ptr = chunk.find(text)
        if ptr != -1:
            fh.seek( startPtr )
            return startPtr + ptr + offset
        offset += 512


# We'll cache the files just to speed things up a tad
fileCache = {}

# Read an .MPT file and return a list of lines
def readMPTFile( file ):
    script = []
    if file in fileCache:
        return fileCache[file]
    with io.open(file, mode="rb") as mptDialog:
        magic = mptDialog.read(4)
        if magic != b'MPT0':
            print( "Not valid MPT File...")
            return
        headerOffset = seekText( mptDialog, b'@a' )
        if headerOffset == -1:
            return -1
        mptDialog.seek(headerOffset + 2)
        
        dId = 0
        while True:
            dialogObj = {}
            # After the '@a'
            nameOffset = seekText( mptDialog, b'@a' ) + 2
            # Seek '@b'
            nameEnd = seekText( mptDialog, b'@b' )
            if( nameEnd == -1 ):
                # End of file found
                break
            if( nameEnd > nameOffset + 2 ):
                mptDialog.seek(nameOffset)
                name = mptDialog.read( nameEnd - nameOffset )
                dialogObj['name'] = name.decode('utf-8')
            # Seek end of dialog
            dialogEnd = seekText( mptDialog, b'@c' )
            mptDialog.seek(nameEnd+2)
            dialog = mptDialog.read((dialogEnd - nameEnd) - 2)
            mptDialog.seek(2,1)

            finalDialog = dialog.decode('utf-8')
            for key in dialogMap:
                finalDialog = finalDialog.replace( key, dialogMap[key] )

            dialogObj['line'] = finalDialog
            dialogObj['length'] = len(dialog)
            dialogObj['id'] = dId
            script.append(dialogObj)
            dId += 1
        fileCache[file] = script
        return script

# Read our generated CSV dialog files and produce a simliar list to above
def readCSVFile( file ):
    script = []
    if file in fileCache:
        return fileCache[file]
    with io.open(file, mode="rb") as csvDialog:
        for line in csvDialog:
            dialogObj = {}
            line = line.decode('utf-8').split(',')
            dialogObj['line'] = line[1]
            dialogObj['length'] = len(line[1])
            dialogObj['name'] = ''
            script.append(dialogObj)
        fileCache[file] = script
        return script

# Gather Directory Listings
_, _, mptFiles = next(walk('./assets/msg/ja')) # will be identical for en
_, _, csvFiles = next(walk('./jdialog'))

# Lets start by just translating one dialog for now.
csvDialog = readCSVFile( './jdialog/01B8.csv' )

# Translate each line in the PSX Dialog
for csvLine in csvDialog:
    # Similarity Tracker
    bestSim = 0
    bestTransId = 0
    bestTransFile = ''
    bestTransLine = ''
    for mptDialog in mptFiles:
        # Get Japanese and English Scripts
        mptjScript = readMPTFile( './assets/msg/ja/' + mptDialog )

        if mptjScript == -1:
            continue

        # Read each line of Japanese script
        for mptLine in mptjScript:
            # Calculate the similarity
            sim = SequenceMatcher(None, mptLine['line'], csvLine['line']).ratio()
            
            if sim > bestSim:
                bestTransId = mptLine['id']
                bestTransFile = mptDialog
                bestTransLine = mptLine['line']
                bestSim = sim

            if bestSim > 0.9:
                break
        if bestSim > 0.9:
            break

    # Find the appropriate translated line
    trans = ''
    mpteScript = readMPTFile( './assets/msg/en/' + bestTransFile )
    for engLine in mpteScript:
        if engLine['id'] == bestTransId:
            trans = engLine['line']

    print( "Line:\n%s" % csvLine['line'] )
    print( "Matched Line:\n%s" % bestTransLine )
    print( "Translated from %s (Confidence: %0.2f%%):\n%s" % (bestTransFile, sim*100, trans) )
    print( "+====================================+")

'''
String similarity:
https://stackoverflow.com/questions/17388213/find-the-similarity-metric-between-two-strings

Should filter all characters that aren't Katakana/Hirigana
then measure similarity

Determine structure of Android dialog and convert it to new structure.


'''