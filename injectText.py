# Script for Working With DQ4 Data
from libs.blockDefs import *
from autoTranslator import getTranslation
from libs.lzs import decompress
import io

with open("HBD1PS1D.Q41", "rb") as dq4b:

    print("== STARTING INJECTION ==")

    # Seek to the beginning of the block data
    dq4b.seek(0x800)

    # Only 3243 Blocks in the file - fails after this
    numBlocks = 0
    for i in range(3243):
        # Create template block
        b = Block()
        numBlocks += 1

        # Brute force read the next block header, probably unnessesary at this point
        b.zeroBytes = 1 # need to emulate a do loop
        bytesParsed = 0
        while b.zeroBytes != 0 or b.numSubBlocks > 1000:
            bHeader = dq4b.read(16)
            bytesParsed += 16
            b.parseHeader(bHeader)
        
        # evil way to do this but idc hahahahaha
        if bytesParsed > 2048:
            bytesParsed -= 16
            numBlocks += int(bytesParsed/2048)
        #print( f"Num Blocks: {numBlocks}")
        #b.printBlockInfo()

        # Calculate how much data is left based on sector size
        dataLeft = 2048 * b.sectors - 16

        # Read all the subblocks in the current block
        for j in range( b.numSubBlocks ):
            sbHeader = dq4b.read(16)
            dataLeft -= 16
            sb = SubBlock(j)
            sb.parseHeader(sbHeader)
            # sb.printBlockInfo()
            # Add to this blocks SubBlock data
            b.subBlocks.append(sb)

        # Now we can go through the subblocks
        for sb in b.subBlocks:
            offset = 0
            # If we have a textblock, make a new obj
            if False and (sb.type == 40 or sb.type == 42):
                tbHeader = dq4b.read(24)
                tb = TextBlock()
                tb.parseHeader(tbHeader)

                # go 24 bytes back, just so the offsets in the header still work
                dq4b.seek(-24,1)
                #print( "\nOffset 0x%08X" % dq4b.tell() )
                #tb.printBlockInfo()
                tbBody = dq4b.read( sb.compLength )
                tb.parseBody( tbBody )

                if tb.uuid == 0x067:
                    print( "\nOffset 0x%08X" % dq4b.tell()-sb.compLength )
                    tb.printBlockInfo()
                    #print( "-- Huff Code")
                    #printHex( tb.encData )
                    #print( "-- Huff Data")
                    #printHex( tb.encHuffTree )
                    tb.printDHeader()
                    d1hv = []

                    for i in range(0,tb.d_var[0] * 2,2):
                        b = byteRead( tb.d1, i, 2, decode=True )
                        d1hv.append(b)
                    print( d1hv )

                    nument = ((tb.d2_off - tb.d1_off - d1hv[0] - 16) / 8)
                    
                    # 0-4
                    # 4-5A
                    # the rest

                    # I want
                    # 4-5A
                    # 5A-end

                    d1idx = d1hv + [tb.d2_off - tb.d1_off]
                    last_off = d1hv[1]
                    for idx, off in enumerate(d1idx):
                        coff = off + idx*2
                        d1d = byteSlice( tb.d1, last_off, coff, decode=False)
                        for i in range(int((coff-last_off)/8)-1):
                            num = byteRead(d1d,i*8,4,decode=True)&0xFFFF
                            adr = byteRead(d1d,(i*8)+4,4,decode=True)
                            print( "[%d] Num: %04X (%d) - Off: %08X" %(i, num, num, adr))

                        printHex( d1d )
                        last_off = coff
                    
                    printHex(tb.d2)

                validDialog = False
                for line in tb.decText:
                    if "ダミー{7f0b}{0000}" in line["text"] or line["text"] == "{0000}":
                        ''' bad sign if dialog is only these '''
                    else:
                        validDialog = True

                #if validDialog:
                #    with io.open( './jdialog/%04X.csv' % tb.uuid, mode="r", encoding="utf-8") as dcsv:
                #        tdialog = [getTranslation(line) for line in dcsv]
                #        buffer = tb.encodeTranslation( ''.join(tdialog) )

                dataLeft -= ( sb.compLength )
            # Script block!!!
            elif numBlocks == 26046 and sb.type == 39:
                print( i )
                sb.printBlockInfo()
                sbBody_c = dq4b.read( sb.compLength )
                if sb.flags == 1280:
                    sbBody = decompress( sbBody_c, sb.length)
                else:
                    sbBody = sbBody_c
                printHex( sbBody )

                isComm = False
                c = b''
                for hex in sbBody:
                    if not isComm and hex == 0xB4:
                        isComm = True
                    else:
                        if hex == 0xB4:
                            isComm = False
                            print(c.hex())
                            c = b''
                            continue
                        c += hex.to_bytes(1, byteorder='little')

                dataLeft -= ( sb.compLength )
            else:
                # For now we ignore every subblock that's not a text block
                dq4b.seek(sb.compLength, 1)
                dataLeft -= sb.compLength
        # TODO: Actually parse out subblock data
        dq4b.seek(dataLeft,1)