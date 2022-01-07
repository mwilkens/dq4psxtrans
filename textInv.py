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

select = 26058

# block 259 has a VERY short d-block

if __name__ == '__main__':
    for b in parseHBD1('HBD1PS1D.Q41'):
        for sb in parseBlock(b):
            offsetMap = []
            if (sb.type == 40 or sb.type == 42):
                b.printBlockInfo()
                sb.printBlockInfo()
                tb = TextBlock(sb)
                tb.parse()
                tb.printBlockInfo()
                tb.printDHeader()
                oldText = tb.decText

                tb.printDBlockPages()

                # print("D1 Block")
                # printHex( tb.d1 )
                # print("D2 Block")
                # printHex( tb.d2 )

                # d2bits = []
                # for byt in tb.d2:
                #     d2bits.append( byt >> 0 & 0x3 )
                #     d2bits.append( byt >> 2 & 0x3 )
                #     d2bits.append( byt >> 4 & 0x3 )
                #     d2bits.append( byt >> 6 & 0x3 )
                # 
                # for p in tb.d1_pages:
                #     last_off = len(d2bits)
                #     for e in p:
                #         print( f"{e['offset']} - {last_off}")
                #         chunk = d2bits[e['offset']:last_off]
                #         data = bytearray()
                #         adjust = True
                #         inByte = True
                #         counter = 0
                #         db = 0
                #         for nib in chunk:
                #             if nib == 0 and adjust == True:
                #                 continue
                #             else:
                #                 adjust = False
                #             if counter == 4:
                #                 inByte = False
                #             if inByte:
                #                 db = db << 2
                #                 db |= nib
                #                 counter += 1
                #             else:
                #                 data.append(db)
                #                 inByte = True
                #                 db = 0
                #                 counter = 0
                #         printHex(data)
                #         last_off = e['offset']


                # check if it's valid dialog
                # validDialog = False
                # for line in tb.decText:
                #     if "ダミー{7f0b}{0000}" in line["text"] or line["text"] == "{0000}":
                #         ''' bad sign if dialog is only these '''
                #     else:
                #         validDialog = True

                # # read translation CSV
                # tdialog = []
                # with io.open( './jdialog/%04X.csv' % tb.uuid, mode="r", encoding="utf-8") as dcsv:
                #     for line in dcsv:
                #         dialog = line.split('|')
                #         if len(dialog[0]) > 1:
                #             tdialog.append(dialog[1])
                #         else:
                #             tdialog.append(dialog[1])
                # # huffman encode translation
                # buffer = tb.encodeTranslation( ''.join(tdialog) )
                # # replace buffer with new text block
                # sb.data = buffer

                # get new offsets (yeah idk it works though)
                #tb = TextBlock(sb)
                #tb.parse()