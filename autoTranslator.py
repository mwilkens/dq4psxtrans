import io
from difflib import SequenceMatcher
from os import walk

# Dialog format mapping
dialogMap = {
    '\n\t': '{7f02}',
    '\n': '',
    '%0': '', # Denotes something but idc
    r'%a00090': '{7f1f}',
    r'%a00120': '{7f02}{7f4b}', # yeah I don't know
    '＊「': '',
    '*: ': '',
}

# Names to control characters
nameMap = {
    'ライアン': '{7f20}',
    'アリーナ': '{7f21}', # Alena 
    'ブライ': '{7f23}',  # Brey / Borya
    'クリフト': '{7f22}', # Cristo / Kiryl
    'ブライ': '{7f23}',
    'トルネコ': '{7f24}',
    'ミネア': '{7f25}',
    'マーニャ': '{7f26}',
    'パノン': '{7f2e}',
    'ピサロ': '{7f31}', # Saro
    'ロザリー': '{7f32}',
}

# Searches a binary file for next instance of a certain text/hex/etc
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

            # replace the formatting / clear junk
            for key in dialogMap:
                finalDialog = finalDialog.replace( key, dialogMap[key] )
            
            # replace the speaker's names with their control bytes
            for name in nameMap:
                finalDialog = finalDialog.replace( name + "「", "{7f04}" + nameMap[name] + '「' )
            
            # Now we can replace all other instances of the name with the plain control byte
            for name in nameMap:
                finalDialog = finalDialog.replace( name, nameMap[name] )

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

totalLines = 0
poorMatches = 0
noMatches = 0

for csvFile in csvFiles:
    print( "\n+=======================+\n!!SCANNING %s !!\n+=======================+\n" % csvFile)
    # Lets start by just translating one dialog for now.
    csvDialog = readCSVFile( './jdialog/' + csvFile )

    # Translate each line in the PSX Dialog
    for csvLine in csvDialog:

        # Ignore blank/dummy lines
        if( csvLine['line'] == '{0000}' or csvLine['line'] == 'ダミー{7f0b}{0000}'):
            continue
        
        # PSX lines are sometimes packaged with these two controls
        # We can split the dialog, translate then repackage.
        # Also get rid of the end character, cos we add it back later
        psxLines = csvLine['line'].split('{7f0a}{7f02}')
        transLines = []
        avgConfidence = 0

        curLine = 0
        for psxLine in psxLines:

            # Similarity Tracker
            bestSim = 0
            bestTransId = 0
            bestTransFile = ''
            bestTransLine = ''

            # If we've found the file the dialog contains, lets limit our search to that file
            if bestTransFile != '':
                searchFiles = [bestTransFile]
            else:
                searchFiles = mptFiles

            for mptDialog in searchFiles:
                # Get Japanese and English Scripts
                mptjScript = readMPTFile( './assets/msg/ja/' + mptDialog )

                if mptjScript == -1:
                    continue

                # Read each line of Japanese script
                for mptLine in mptjScript:
                    # Remove all control characters for the sim check
                    a = mptLine['line'].translate(str.maketrans('', '', '{0123456789abcdef}'))
                    b = psxLine.translate(str.maketrans('', '', '{0123456789abcdef}'))
                    # Calculate the similarity
                    sim = SequenceMatcher(None, a, b).ratio()
                    
                    if sim > bestSim:
                        bestTransId = mptLine['id']
                        bestTransFile = mptDialog
                        bestTransLine = mptLine['line']
                        bestSim = sim

                    if bestSim > 0.9:
                        break
                if bestSim > 0.9:
                    break

            if avgConfidence == 0:
                avgConfidence += sim
            else:
                avgConfidence = (sim + avgConfidence)/2

            transLines.append( bestTransId )
            curLine += 1

        # Find the appropriate translated line
        trans = ''
        mpteScript = readMPTFile( './assets/msg/en/' + bestTransFile )
        for lineId in transLines:
            for engLine in mpteScript:
                if engLine['id'] == lineId:
                    if trans != '':
                        trans = trans + '{7f0a}{7f02}' + engLine['line']
                    else:
                        trans = engLine['line']
        trans += '{0000}'

        # Unnecessary but useful for debugging
        mptjScript = readMPTFile( './assets/msg/ja/' + bestTransFile )
        fullMatch = ''
        for lineId in transLines:
            for jaLine in mptjScript:
                if jaLine['id'] == lineId:
                    if fullMatch != '':
                        fullMatch = fullMatch + '{7f0a}{7f02}' + jaLine['line']
                    else:
                        fullMatch = jaLine['line']

        # Print only moderate translations
        if avgConfidence < 0.8 and avgConfidence > 0.05:
            print( "Line:\n%s" % csvLine['line'] )
            print( "Matched Line:\n%s" % fullMatch )
            print( "Translated from %s (Confidence: %0.2f%%):\n%s" % (bestTransFile, avgConfidence*100, trans) )
            print( "+========TOTAL:%d======POOR:%d======BAD:%d=========+\n" % (totalLines, poorMatches, noMatches))

        if avgConfidence < 0.05:
            noMatches += 1
        elif avgConfidence < 0.8:
            poorMatches += 1
        totalLines += 1
