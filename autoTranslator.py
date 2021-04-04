import io
from difflib import SequenceMatcher
from os import walk
import sys
sys.stdout = open('controlCharScan.txt', 'w', encoding="utf-8")

# Dialog format mapping
dialogMap = {
    '\n\t': '{7f02}',
    '\n': '',
    '%0': '', # Denotes something but idc
    r'%a00090': '{7f1f}',
    r'%a00100': '{7f17}',
    r'%a00120': '{7fxx}', # better matching this way
    r'%a00140': '{7f33}', # Also 7f4b
    r'%a00160': '{7f30}',
    r'%a00260': '{7f42}',
    r'%a00520': '{7f15}', # Money amount
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
    'スコット': '{7f28}',
    'アレクス': '{7f29}',
    'フレア': '{7f2a}',
    'ホイミン': '{7f2b}',
    'オーリン': '{7f2c}',
    'ホフマン': '{7f2d}',
    'パノン': '{7f2e}',
    'ルーシア': '{7f2f}',
    'ピサロ': '{7f31}', # Saro
    'ロザリー': '{7f32}',
    'エッグラとチキーラ': 'チキーラとエッグラ', # The Android version swaps their names for some reason
    'チキーラとエッグラ': 'エッグラとチキーラ',
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
def readMPTFile( file, condition=False ):
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

            if condition:
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

def getTranslation( line ):
    # Default Return Value
    translation = {'line':'', 'similarity':0, 'file':'', 'ids':[]}

    # We need to keep track of how confident we are of the translation
    avgConfidence = 0

    # PSX lines are sometimes packaged with these two controls
    # We can split the dialog, translate then repackage.
    # Also get rid of the end character, cos we add it back later
    psxLines = line.split('{7f0a}{7f02}')
    for psxLine in psxLines:
        # If we've found the file the dialog contains, lets limit our search to that file
        if translation['file'] != '':
            searchFiles = [translation['file']]
        else:
            searchFiles = mptFiles

        for mptDialog in searchFiles:
            # Get Japanese and English Scripts
            mptjScript = readMPTFile( './assets/msg/ja/' + mptDialog, condition=True )

            if mptjScript == -1:
                continue

            candidateId = 0

            # Read each line of Japanese script
            for mptLine in mptjScript:
                # Remove all control characters for the sim check
                a = mptLine['line'].translate(str.maketrans('', '', '{0123456789abcdef}'))
                b = psxLine.translate(str.maketrans('', '', '\%{0123456789abcdef}'))
                # Calculate the similarity
                sim = SequenceMatcher(None, a, b).ratio()
                
                if sim > translation['similarity']:
                    candidateId = mptLine['id']
                    translation['file'] = mptDialog
                    translation['similarity'] = sim

                if translation['similarity'] > 0.9:
                    break
            if translation['similarity'] > 0.9:
                break

        if avgConfidence == 0:
            avgConfidence += sim
        else:
            avgConfidence = (sim + avgConfidence)/2
        
        # Add line to lines to matches
        translation['ids'].append( candidateId )

    translation['similarity'] = avgConfidence*100

    # Load the matched file
    mpteScript = readMPTFile( './assets/msg/en/' + translation['file'] )
    # For each matched ID
    for lineId in translation['ids']:
        for engLine in mpteScript:
            if engLine['id'] == lineId:
                if translation['line'] != '':
                    # Append translation to total buffer
                    translation['line'] = translation['line'] + '\n' + engLine['line']
                else:
                    translation['line'] = engLine['line']
    
    # Return the translation
    return translation

def getControlChars( line ):
    isCC = False
    ccBuff = ''
    ccList = []
    for char in line:
        if char == '{':
            isCC = True
            continue
        if char == '}':
            isCC = False
            ccList.append('{' + ccBuff + '}')
            ccBuff = ''
            continue
        if isCC:
            ccBuff += char
    return ccList

####################################################
## Go through each CSV File and start translating ##
####################################################

controlChars = [
    '{0000}','{7f02}','{7f04}','{7f0a}','{7f0b}','{7f1f}',
    '{7f15}','{7f16}','{7f17}','{7f18}''{7f20}','{7f21}',
    '{7f22}','{7f23}','{7f24}','{7f25}','{7f26}','{7f27}',
    '{7f28}','{7f29}','{7f2a}','{7f2b}','{7f2c}','{7f2d}',
    '{7f2e}','{7f2f}','{7f30}','{7f31}','{7f32}','{7f33}',
    '{7f34}','{7f42}','{7f43}','{7f44}','{7f45}','{7f4c}'
]
controlCharMap = {}

for csvFile in csvFiles[580:]:
    print( "\n+==================+!! SCANNING %s !!+==================+" % csvFile)
    print(   "+================TOTAL:%d======POOR:%d======BAD:%d===============+\n" % (totalLines, poorMatches, noMatches))
    # Lets start by just translating one dialog for now.
    csvDialog = readCSVFile( './jdialog/' + csvFile )

    # Translate each line in the PSX Dialog
    for csvLine in csvDialog:

        # Ignore blank/dummy lines
        if( csvLine['line'] == '{0000}' or csvLine['line'] == 'ダミー{7f0b}{0000}'):
            continue
        
        translation = getTranslation( csvLine['line'])

        # Unnecessary but useful for debugging
        mptjScript = readMPTFile( './assets/msg/ja/' + translation['file'] )
        fullMatch = ''
        for lineId in translation['ids']:
            for jaLine in mptjScript:
                if jaLine['id'] == lineId:
                    if fullMatch != '':
                        fullMatch = fullMatch + '\n' + jaLine['line']
                    else:
                        fullMatch = jaLine['line']

        ccs = getControlChars( csvLine['line'] )
        if translation['similarity'] > 50 and ccs != None:
            for cc in ccs:
                if cc not in controlChars:
                    print( "======== FOUND NEW CONTROL CHAR ============")
                    print( "==> %s <==" % cc )
                    print( "Line:\n%s" % csvLine['line'] )
                    print( "Matched Line:\n%s" % fullMatch )
                    print( "Translated from %s (Confidence: %0.2f%%):\n%s" % (translation['file'], translation['similarity'], translation['line']) )
                    controlChars.append(cc)

        # Print only moderate translations
        if False and translation['similarity'] < 70:
            print( "Line:\n%s" % csvLine['line'] )
            print( "Matched Line:\n%s" % fullMatch )
            print( "Translated from %s (Confidence: %0.2f%%):\n%s" % (translation['file'], translation['similarity'], translation['line']) )

        if translation['similarity'] < 5:
            noMatches += 1
        elif translation['similarity'] < 80:
            poorMatches += 1
        totalLines += 1
sys.stdout.close()