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

    # Starts its search at FF0, wrapping around when it can

    def findMatch(buff, idx, data, pos):
        l = 0
        while True:
            if (pos+l) >= len(data):
                break
            if l >= 0x12:
                break
            if idx >= 0 and (idx+l) == pos:
                break
            if buff[(idx+l)%4096] == data[pos+l]:
                l += 1
            else:
                break
        if l < 3:
            return -1
        return l

    def findLongestMatch( data, pos ):
        bdist = -1
        blen = 2
        # Create a buffer with only the data we can access
        buffer = data[:pos] + bytearray(4096-pos)

        l = -1
        for i in range( 0xFFF, 0xFFF-0x12, -1):
            l = findMatch(buffer,i,data,pos)
            if l > blen:
                bdist = i
                blen = l
        
        if l < 0:
            idx = 0
            while idx < pos:
                l = findMatch(buffer,idx,data,pos)
                if l > blen:
                    bdist = idx
                    blen = l
                idx += 1

        
        return (bdist, blen)
    
    comp = bytearray()
    idx = 0

    while idx < len(in_data) - 8:
        cbuf = 0
        dbuf = []
        for i in range( 0, 8, 1 ):
            match = findLongestMatch( in_data, idx )
            if match[0] != -1:
                # no need to do anything to cbuf, 0 already there :)

                # First byte is length minus 3, second is offset minus 18
                b1 = (match[1] - 3) | ((match[0]-18) & 0xF00) >> 4
                b2 = (match[0]-18) & 0xFF
                dbuf.append( b2 )
                dbuf.append( b1 )

                vals = []
                for i in range(match[1]):
                    vals.append( in_data[idx+i] )
                print(f"0 - {idx} {match[0]} {match[1]} {b2:02X} {b1:02X} - {' '.join('%02X'%x for x in vals)}")

                # print(f"\n[{b2:02X} {b1:02X}]", end=' ')
                # for i in range(match[1]):
                #     if match[0] < 0xF00:
                #         print("%02X" % in_data[match[0]+i], end=' ')
                #     else:
                #         print("00", end=' ')
                # print()

                idx += match[1]
            else:
                cbuf |= 1 << i
                try:
                    print(f"1 - {in_data[idx]:02X}")
                    dbuf.append( in_data[idx] )
                    # print( "%02X" % in_data[idx], end=' ')
                except Exception as e:
                    '''do nothing'''
                idx += 1
        print("Block Done")
        comp.append(cbuf)
        [ comp.append(v) for v in dbuf ]

    return comp

'''

FEB(0) vs. FEF(0)
4093   vs. 4097
FE7(4) vs. FF3(4)

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

======================== ORIGINAL =============================================== MINE ===========================
0x0000 | F5 B0 EB F0 04 E7 F4 A4 | 01 00 00 45 10 EB F0 0A | | F5 B0 EB F0 04 E7 F4 A4 | 01 00 00 45 10 EB F0 0A |
0x0010 | E3 F8 02 09 EA F1 5C EA | F1 2F 02 00 00 40 23 00 | | E3 F8 02 09 03.01.5C 03.| 01.2F 02 00 00 40 23 00 |
0x0020 | 68 27 04 31 0F BA E8 F3 | B1 EA F1 C0 21 A0 FB F0 | | 68 27 04 30.0F 7A.03.03.| B1 03.01.C0 21 A0 01.03.|
0x0030 | 00 77 F1 06 3A EC F0 B0 | B0 B2 EA F1 97 43 43 43 | | 00 FF.F1 06 3A 00.00.B0 | B0 B0.5D.B2.03.01.43 43 |
0x0040 | 4A 0C 01 5A 0F 50 06 02 | 74 76 0F 50 06 03 92 0F | | 43.4A.0C.01.5A.0F.D2.50.| 06.02.5A.0F.50.06.03.5A.|
0x0050 | 21 A0 CD EB F0 FF B4 01 | A0 E1 03 00 B3 02 2C 52 | | 0F.21.A0.FD.CD.03.00.B4.| 01.A0.E1.03.00.B3.B3.02.|
0x0060 | 01 4F 07 04 00 96 0D CF | C3 0F 52 04 E9 05 DD 0E | | 52.01.4F.07.04.00.5E.0D.| CF.A4.C3.0F.52.04.05.DD.|
0x0070 | 52 04 06 AE 0F 21 A0 5F | 3C FB F0 F2 0A 16 78 01 | | 0E.52.04.06.5A.0F.21.F3.| A0.5F.52.00.C6.0A.16.78.|
0x0080 | A0 23 10 4F 00 3D 88 37 | 1D 61 A0 78 01 F2 00 4F | | 01.A0.F4.5B.00 4F.00.88.| 37.1D.61.A0.78.01.74.C6.|
0x0090 | 00 9D 7F 37 15 01 B3 02 | 2F 01 56 00 08 09 00 4D | | 00 4F.00.7F.37.15.01.B3.| 02.2F.01.26.56.00.08.00.|
0x00A0 | 11 52 04 07 DD 0B 4B 11 | 62 1F 74 18 A5 0C 4E 08 | | 4D.11.52.04.07.DD.0B.4B.| 11.94.62.1F.74.18.0C.4E.|
0x00B0 | 0B 09 1F 53 03 0F 22 16 | 58 57 58 58 14 EB F0 30 | | 08.0B.09.1F.53.03.0F.5E.| 5A.06.58 58 58.14.03.00.|
0x00C0 | EB F0 4C EB F0 A5 68 EB | F0 94 4C 01 EB F0 DC EB | | 30.03.00.95.4C.03.00.68.| 03.00.94.4C.01.03.00.DC.|
0x00D0 | F0 44 AA FB F0 04 FB F0 | 4C 12 20 38 FB F0 80 2A | | AA.03.00.44.52.00.04.52.| 00.4C.12.20.38.AA.52.00.|
0x00E0 | FB F0 54 0F 24 74 FB F0 | 9C 52 01 EB F0 55 1C EB | | 80.52.00.54.0F.24.74.52.| 00.9C.54.52.01.03.00.1C.|
0x00F0 | F0 38 EB F0 54 EB F0 70 | EB F0 15 9C EB F0 C8 EB | | 03.00.38.03.00.54.03.00.| 55.70.03.00.9C.03.00.C8.|
0x0100 | F0 E4 F3 11 FB F0 51 11 | 06 EC F3 00 00 75 00 31 | | 03.00.E4.F3.11.00.52.00.| 51.11.59.00 03.02.75.00.|
0x0110 | 22 91 00 35 22 AD 00 12 | 39 22 04 ED F0 3E 21 05 | | 31.22.91.00.35.22.24.AD.| 00.39.22.04.57.20.3E.21.|
0x0120 | ED F0 42 21 21 10 42 45 | 22 07 ED F0 4A 21 7F 10 | | 05.57.20.42.21 84.21.10.| 45.22.07.57.20.4A.21.7F.|
0x0130 | 4D 22 09 ED F0 00 52 21 |                         | | 10.4D.22.09.            |                         |
'''