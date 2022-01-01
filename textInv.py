from libs.parsing import *
from libs.helpers import *
from libs.blockDefs import *
from autoTranslator import getTranslation, readMPTFile
import io
import re
import sys
import codecs
from os import walk

# Two tasks
# 1. Get android dialog match(s) for each scene
# 2. Get huffman offsets for translated text

select = 26046

if __name__ == '__main__':

    alreadyDone = []
    with open('dialogMatch.csv', 'r') as fh:
        for line in fh:
            dialog = line.split('|')[0]
            dialog = re.sub(r"[^A-Za-z0-9]","",dialog)
            if dialog != '':
                dialog = int(dialog,16)
                alreadyDone.append(dialog)
    for b in parseHBD1('HBD1PS1D.Q41'):
        for sb in parseBlock(b):
            if b.id == select and (sb.type == 40 or sb.type == 42):
                #b.printBlockInfo()
                #sb.printBlockInfo()
                tb = TextBlock(sb)
                tb.printBlockInfo()
                tb.parse()
                old = sb.data
                for line in tb.decText:
                    if "ダミー{7f0b}{0000}" in line["text"] or line["text"] == "{0000}":
                        ''' bad sign if dialog is only these '''
                    else:
                        validDialog = True
                matches = []
                if validDialog and tb.uuid not in alreadyDone:
                    #for line in tb.decText:
                    #    t = getTranslation(line['text'])
                    #    print( line['text'] )
                    #    print( t['line'])
                    #    if t['similarity'] > 90:
                    #        matches.append(t['file'])
                    with io.open( './jdialog/%04X.csv' % tb.uuid, mode="r", encoding="utf-8") as dcsv:
                        tdialog = []
                        for line in dcsv:
                            dialog = line.split('|')
                            if len(dialog[0]) > 1:
                                tdialog.append(dialog[1])
                            else:
                                tdialog.append(dialog[1])
                        print(tdialog)
                        buffer = tb.encodeTranslation( ''.join(tdialog) )
                        compHex(old,buffer)
                        sb.data = buffer
                        tb = TextBlock(sb)
                        tb.parse()
                    #matches = list(set(matches))
                    #print(f"{tb.uuid:04X}|{matches}")