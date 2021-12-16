# Script for Working With DQ4 Data
from libs.blockDefs import *
import io

ent = []
d3 = []

with open("HBD1PS1D.Q41", "rb") as dq4b:

    print("== STARTING EXTRACTION ==")

    # Seek to the beginning of the block data
    dq4b.seek(0x800)

    numBlocks = 0

    # Only 3243 Blocks in the file - fails after this
    for i in range(3243):
        # Create template block
        b = Block()

        ''' Probably these don't exist and whatever if they do
        t = dq4b.read(4)
        if (int.from_bytes(t,byteorder='little') == 0x60010108):
            print("!!!! 0x60010108 BLOCK !!!!")
            numBlocks += 1
            # ignore it lmao
            d14b.seek(2044,1)
        else:
            dq4b.seek(-4,1)
        '''
        print( f"BLOCK COUNT: {numBlocks}")

        # Brute force read the next block header, probably unnessesary at this point
        b.zeroBytes = 1 # need to emulate a do loop
        while b.zeroBytes != 0 or b.numSubBlocks > 1000:
            bHeader = dq4b.read(16)
            b.parseHeader(bHeader)
        b.id = (dq4b.tell()-16)/2048
        b.printBlockInfo()
        numBlocks += 1

        # Calculate how much data is left based on sector size
        dataLeft = 2048 * b.sectors - 16

        # Read all the subblocks in the current block
        for i in range( b.numSubBlocks ):
            sbHeader = dq4b.read(16)
            dataLeft -= 16
            sb = SubBlock(i)
            sb.parseHeader(sbHeader)
            sb.printBlockInfo()
            # Add to this blocks SubBlock data
            b.subBlocks.append(sb)

        # Now we can go through the subblocks
        for sb in b.subBlocks:
            offset = 0

            # Script block!!!
            if sb.type == 39:
                ''' do nothing for now '''
            
            # If we have a textblock, make a new obj
            if sb.type == 40 or sb.type == 42:
                tbHeader = dq4b.read(24)
                tb = TextBlock()
                tb.parseHeader(tbHeader)

                # go 24 bytes back, just so the offsets in the header still work
                dq4b.seek(-24,1)
                #print( "\nOffset 0x%08X" % dq4b.tell() )
                #tb.printBlockInfo()

                #print( "TEXTBLOCK ID %02X" % tb.uuid )

                tbBody = dq4b.read( sb.compLength )
                tb.parseBody( tbBody )

                validDialog = False
                for line in tb.decText:
                    if "ダミー{7f0b}{0000}" in line["text"] or line["text"] == "{0000}":
                        ''' bad sign if dialog is only these '''
                    else:
                        validDialog = True
                
                if validDialog and tb.one and tb.d_var[3] != 0:
                    tb.printBlockInfo()
                    tb.printDHeader()

                    d1hv = []

                    for i in range(0,tb.d_var[0] * 2,2):
                        b = byteRead( tb.d1, i, 2, decode=True )
                        d1hv.append(b)
                    #print( d1hv )

                    nument = ((tb.d2_off - tb.d1_off - d1hv[0] - 16) / 8)
                    
                    last_off = 0
                    idx = 0
                    for off in d1hv:
                        coff = off + idx*2
                        d1d = byteSlice( tb.d1, last_off, coff, decode=False)
                        #printHex( d1d )
                        last_off = coff
                        idx += 1
                    #printHex( byteSlice(tb.d1, last_off, tb.d2_off - tb.d1_off, decode=False) )

                #if validDialog:
                #    with io.open( './jdialog/%04X.csv' % tb.uuid, mode="w", encoding="utf-8") as dcsv:
                #        for line in tb.decText:
                #            dcsv.write( "\"\"," + ",".join(line.values()) + "\n")

                dataLeft -= ( sb.compLength )
            else:
                # For now we ignore every subblock that's not a text block
                dq4b.seek(sb.compLength, 1)
                dataLeft -= sb.compLength
        # TODO: Actually parse out subblock data
        dq4b.seek(dataLeft,1)