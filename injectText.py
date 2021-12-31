# Script for Working With DQ4 Data
from libs.blockDefs import *
from libs.parsing import *
import io

if __name__ == '__main__':
    with open('HBD1PS1D.Q41.NEW', 'wb') as fh:
        for b in parseHBD1('HBD1PS1D.Q41', yield_invalid=True):
            if b.valid:
                subblocks = []
                for sb in parseBlock(b):
                    if sb.type == 40 or sb.type == 42:
                        tb = TextBlock(sb)
                        # tb.parse()
                        # validDialog = False
                        # for line in tb.decText:
                        #     if "ダミー{7f0b}{0000}" in line["text"] or line["text"] == "{0000}":
                        #         ''' bad sign if dialog is only these '''
                        #     else:
                        #         validDialog = True

                        # if validDialog:
                        #     with io.open( './jdialog/%04X.csv' % tb.uuid, mode="r", encoding="utf-8") as dcsv:
                        #         tdialog = [getTranslation(line) for line in dcsv]
                        #         buffer = tb.encodeTranslation( ''.join(tdialog) )
                    if sb.type == 39:
                        sbbak = sb
                        scb = ScriptBlock(sb)
                        oldlen = sb.compLength
                        # for now just recompress
                        scb.compress()
                        if oldlen != sb.compLength:
                            print(f"Uh oh!!!!! {b.id}")
                            sb = sbbak
                    subblocks.append(sb)
                
                # insert headers into new block
                idx = 0
                for sb in subblocks:
                    b.data = b.data[:idx] + sb.recalculateHeader() + b.data[idx+16:]
                    idx += 16
                
                # insert bodies into new block
                for sb in subblocks:
                    b.data = b.data[:idx] + sb.data + b.data[idx+sb.compLength:]
                    idx += sb.compLength
            
            # rewrite block
            fh.write( b.header )
            fh.write( b.data )