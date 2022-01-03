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
    for b in parseHBD1('HBD1PS1D.Q41'):
        for sb in parseBlock(b):
            offsetMap = []
            if b.id == select and (sb.type == 40 or sb.type == 42):
                tb = TextBlock(sb)
                tb.parse()
                if tb.uuid != 0x6C:
                    continue
                oldText = tb.decText

                # check if it's valid dialog
                validDialog = False
                for line in tb.decText:
                    if "ダミー{7f0b}{0000}" in line["text"] or line["text"] == "{0000}":
                        ''' bad sign if dialog is only these '''
                    else:
                        validDialog = True

                # read translation CSV
                tdialog = []
                with io.open( './jdialog/%04X.csv' % tb.uuid, mode="r", encoding="utf-8") as dcsv:
                    for line in dcsv:
                        dialog = line.split('|')
                        if len(dialog[0]) > 1:
                            tdialog.append(dialog[1])
                        else:
                            tdialog.append(dialog[1])
                # huffman encode translation
                buffer = tb.encodeTranslation( ''.join(tdialog) )
                # replace buffer with new text block
                sb.data = buffer

                # get new offsets (yeah idk it works though)
                tb = TextBlock(sb)
                tb.parse()

                [print(t['offset'], end=' ') for t in oldText]
                print()

                [print(t['offset'], end=' ') for t in tb.decText]
                print()