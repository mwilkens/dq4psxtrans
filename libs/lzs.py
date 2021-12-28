import math

def decompress( in_data, d_size ):
    buffer = bytearray(4096)
    maxOff = 4096

    offComp = 0
    offDecomp = 0
    offBuff = 0

    decomp = bytearray(d_size)

    while( offComp < len(in_data) ):
        controlByte = in_data[offComp]

        offComp += 1
        fullBreak = False

        for i in range( 0, 8, 1 ):
            bit = (controlByte >> i) & 0x1
            if bit:
                decomp[offDecomp] = in_data[offComp]
                buffer[offBuff] = in_data[offComp]

                offComp += 1
                offDecomp += 1
                offBuff += 1

                offBuff = offBuff % maxOff
            else:
                if offDecomp >= d_size:
                    offComp += 2
                    fullBreak = True
                    break
                ref = in_data[offComp]<<8 | in_data[offComp+1]

                # Length
                l = ref & 0xF
                l = l + 3

                # Offset
                off = (ref & 0xFF00) >> 8 | (ref & 0xF0) << 4
                off = (off+18) % maxOff

                #print( f"Bytes {ref:04X} Len: {l} - Off: {off}")

                for j in range(l):
                    literal = buffer[(off+j) % maxOff]
                    decomp[offDecomp] = literal
                    buffer[offBuff] = literal

                    offDecomp += 1
                    offBuff += 1
                    offBuff = offBuff % maxOff

                offComp += 2
            if offComp >= len(in_data):
                break
        #print(f"Comp: {offComp} - Decomp: {offDecomp} - Buff: {offBuff} - DSize: {d_size} - CSize: {len(in_data)}")
        if fullBreak:
            break
    return decomp

def compress( in_data ):

    def findLongestMatch( data, pos ):
        bdist = -1
        blen = 2

        if pos > len(data) - 8:
            return (bdist, blen)

        idx = 0
        match = []
        for d in data:
            if idx == pos:
                break

            if d == data[pos]:
                tidx = 1
                stillMatched = True
                while stillMatched:
                    if data[idx+tidx] != data[pos+tidx]:
                        stillMatched = False
                    else:
                        tidx += 1
                if tidx > blen:
                    blen = tidx
                    bdist = idx
            
            # We should also check for zeros
            if data[pos] == 0:
                tidx = 1
                stillMatched = True
                while stillMatched:
                    if data[pos+tidx] != 0:
                        stillMatched = False
                    else:
                        tidx += 1
                if tidx > blen:
                    blen = tidx
                    bdist = 0xFFF - tidx + 1
            idx += 1
        
        return (bdist, blen)
    
    comp = bytearray()
    idx = 0

    while idx < len(in_data) - 8:
        cbuf = 0
        dbuf = []
        for i in range( 0, 8, 1 ):
            print("%d - %02X" % (idx,in_data[idx]))
            match = findLongestMatch( in_data, idx )
            if match[0] != -1:
                print(match)
                # no need to do anything to cbuf, 0 already there :)

                # First byte is length minus 3, second is offset minus 18
                b1 = (match[1] - 3) | ((match[0]-18) & 0xF00) >> 4
                b2 = (match[0]-18) & 0xFF
                dbuf.append( b2 )
                dbuf.append( b1 )
                idx += match[1]
            else:
                cbuf |= 1 << i
                try:
                    dbuf.append( in_data[idx] )
                except Exception as e:
                    '''do nothing'''
                idx += 1
        comp.append(cbuf)
        [ comp.append(v) for v in dbuf ]

    return comp

'''
Compressed
0x0000 | DF 7B 02 00 00 0C E7 F4 | F0 03 57 00 00 18 EB F0 | #{#..#####W..###
0x0010 | 0E E3 F8 0D DF FC 7D 5C | EB F0 4C 04 00 00 AC 23 | ######}\##L#..##
0x0020 | 00 D1 E4 27 04 31 0F E8 | F3 B1 EA F1 C0 21 FB A0 | .##'#1#######!##
0x0030 | C6 EB F0 B4 01 A0 E1 03 | EF 00 B3 02 01 EB F0 F4 | #########.######
0x0040 | 21 A0 8A 5E 01 01 4E 01 | B9 53 0C 4F 00 5E 01 F1 | !##^##N##S#O.^##
0x0050 | DF 06 3A 00 00 B2 EA F1 | 43 43 F9 43 4A 05 81 04 | ##:..###CC#CJ###
0x0060 | 03 00 B0 B0 B0 A4 8A 0F | 83 02 04 A2 0F 7F 06 05 | #.##############
0x0070 | BE 0F 21 53 A0 CD 6F 0F | 81 04 06 89 0E CF EF 0F | ##!S##o#########

Decompressed
0x0000 | 7B 02 00 00 0C 00 00 00 | 00 00 00 00 F0 03 00 00 | {#..#.......##..
0x0010 | 18 00 00 00 0E 00 00 00 | 00 00 00 00 00 00 00 00 | #...#...........
0x0020 | 0D 00 00 00 00 00 00 00 | 00 00 00 00 00 00 00 00 | #...............
0x0030 | 5C 00 00 00 4C 04 00 00 | AC 04 00 00 E4 04 00 00 | \...L#..##..##..
0x0040 | E4 04 00 00 00 00 00 00 | 00 00 00 00 00 00 00 00 | ##..............
0x0050 | 00 00 00 00 00 00 00 00 | 00 00 00 00 B1 00 00 00 | ............#...
0x0060 | 00 C0 21 A0 C6 00 00 00 | B4 01 A0 E1 03 00 B3 02 | .#!##...#####.##
'''