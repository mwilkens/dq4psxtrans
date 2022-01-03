# Script for Working With DQ4 Data
from libs.blockDefs import *
from libs.parsing import *
import io
import os

select = 26046

if __name__ == '__main__':
    with open('HBD1PS1D.Q41.NEW', 'wb') as fh:
        for b in parseHBD1('HBD1PS1D.Q41', yield_invalid=True):
            if b.valid:
                changed = False
                dialogId = None
                offsetMap = []
                subblocks = []
                for sb in parseBlock(b):
                    if b.id == select and (sb.type == 40 or sb.type == 42):
                        tb = TextBlock(sb)
                        tb.parse()
                        oldText = tb.decText
                        dialogId = tb.uuid

                        print(f"Changed ID: {dialogId:04X}")

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
                        changed = True

                        # get new offsets (yeah idk it works though)
                        tb = TextBlock(sb)
                        tb.parse()
                        
                        for i in range(len(tb.decText)):
                            old = int( oldText[i]['offset'], 16 )
                            new = int( tb.decText[i]['offset'], 16 )
                            print( f"{oldText[i]['offset']} - {tb.decText[i]['offset']}" )
                            offsetMap.append( (old,new) )
                    subblocks.append(sb)
                
                if changed:
                    # if we altered a text box, we need to alter the script
                    for sb in subblocks:
                        if sb.type == 39:
                            sbbak = sb.data
                            scb = ScriptBlock(sb)
                            # replace all the offsets
                            for off in offsetMap:
                                scb.replaceOffset( dialogId, off[0], off[1] )
                            # recompress
                            sb.length = len(scb.raw)
                            sb.data = scb.compress()
                            sb.compLength = len(sb.data)
                            changed = True
                    # insert headers into new block
                    idx = 0
                    oldbdata = b.data
                    for sb in subblocks:
                        b.data = b.data[:idx] + sb.recalculateHeader() + b.data[idx+16:]
                        idx += 16
                    
                    # insert bodies into new block
                    for sb in subblocks:
                        b.data = b.data[:idx] + sb.data + b.data[idx+sb.compLength:]
                        idx += sb.compLength

                    # We can verify with this routine
                    #for i in range(len(oldbdata)):
                    #    if oldbdata[i] != b.data[i]:
                    #        print("Mismatch in ID %d" % b.id)
                    #        break
            
            # rewrite block
            fh.write( b.header )
            fh.write( b.data )

    # Create new ROM
    #os.replace('./HBD1PS1D.Q41.NEW', './Dragon Quest IV - Michibikareshi Mono Tachi (Japan)/HBD1PS1D.Q41')
    #os.system('.\psximager\psxbuild -c "Dragon Quest IV - Michibikareshi Mono Tachi (Japan).cat" DQ4_En.bin')