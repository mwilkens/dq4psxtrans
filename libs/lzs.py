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

    # probably the best way to do this would be to
    # insert "data" into a 4096 byte buffer and perform the matching
    # from there, this however works fine for what its worth
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

            # First check in the data for a match
            if d == data[pos]:
                tidx = 1
                stillMatched = True
                while stillMatched and tidx < 0x12:
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
                while stillMatched and tidx < 0x12:
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
            match = findLongestMatch( in_data, idx )
            if match[0] != -1:
                # no need to do anything to cbuf, 0 already there :)

                # First byte is length minus 3, second is offset minus 18
                b1 = (match[1] - 3) | ((match[0]-18) & 0xF00) >> 4
                b2 = (match[0]-18) & 0xFF
                dbuf.append( b2 )
                dbuf.append( b1 )

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
                    dbuf.append( in_data[idx] )
                    # print( "%02X" % in_data[idx], end=' ')
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

======================== ORIGINAL =============================================== MINE ===========================
0x0000 | DF 7B 02 00 00 0C E7 F4 | F0 03 57 00 00 18 EB F0 | | DF 7B 02 00 00 0C E7 F4 | F0 03 57 00 00 18 EB F0 |
0x0010 | 0E E3 F8 0D DF FC 7D 5C | EB F0 4C 04 00 00 AC 23 | | 0E E3 F8 0D DF FC 7D 5C | EB F0 4C 04 00 00 AC 23 |
0x0020 | 00 D1 E4 27 04 31 0F E8 | F3 B1 EA F1 C0 21 FB A0 | | 00 D1 E4 27 04 DC.FF.E8 | F3 B1 EA F1 C0 21 FB A0 |
0x0030 | C6 EB F0 B4 01 A0 E1 03 | EF 00 B3 02 01 EB F0 F4 | | C6 EB F0 B4 01 A0 E1 03 | EF 00 B3 02 01 EB F0 F4 |
0x0040 | 21 A0 8A 5E 01 01 4E 01 | B9 53 0C 4F 00 5E 01 F1 | | 21 A0 8A 5E 01 01 4E 01 | B9 53 0C 4F 00 5E 01 F1 |
0x0050 | DF 06 3A 00 00 B2 EA F1 | 43 43 F9 43 4A 05 81 04 | | DF 06 3A 00 00 B2 EA F1 | 43 43 F9 43 4A 05 81 04 |
0x0060 | 03 00 B0 B0 B0 A4 8A 0F | 83 02 04 A2 0F 7F 06 05 | | 03 00 B0 B0 B0 A4 8A 0F | 83 02 04 A2 0F 7F 06 05 |
0x0070 | BE 0F 21 53 A0 CD 6F 0F | 81 04 06 89 0E CF EF 0F | | A2.0F 21 53 A0 CD 6F 0F | 81 04 06 89 0E CF 6F.0F |
0x0080 | 92 81 04 07 89 0F 82 03 | 08 DA 0A 2F 01 C0 7F 26 | | 92 81 04 07 89 0F 82 03 | 08 A2.0A 2F 01 C0 7F 26 |
0x0090 | 78 FB 0C FE FF FF 5F 10 | 3D FC 4B 02 26 78 FD F4 | | 78 FB 0C FE FF FF 5F 10 | 3D FC 4B 02 26 78 FD F4 |
0x00A0 | 5E 00 5F 10 FD FE EA F1 | C1 61 A1 B8 FB FF FF B4 | | 5E 00 5F 10 FD FE EA F1 | C1 61 A1 B8 FB FF FF B4 |
0x00B0 | 01 A1 C0 61 A0 78 01 E4 | 56 00 4F 00 B4 5E 00 56 | | 01 A1 C0 61 A0 78 01 E4 | 56 00 4F 00 B4 5E 00 56 |
0x00C0 | 02 02 B3 02 40 FB F0 4E | 01 EA F1 8D 13 F1 F1 8D | | 02 02 B3 02 40 FB F0 4E | 01 EA F1 8D 13 F1 F1 8D |
0x00D0 | 13 37 94 1F 88 A6 18 23 | 00 8D 13 4A BB 1F D7 15 | | 13 37 94 1F 88 A6 18 23 | 00 8D 13 4A 94.1F D7 15 |
0x00E0 | 89 17 A1 4E E2 1F F6 FF | FF 84 10 8F 11 B5 53 05 | | 89 17 A1 4E 94.1F F6 FF | FF 84 10 8F 11 B5 53 05 |
0x00F0 | A7 01 B3 02 EF F0 4E 01 | 21 A7 16 CE 42 24 2F B4 | | A7 01 B3 02 EF F0 4E 01 | 21 A7 16 CE 42 24 2F B4 |
0x0100 | 53 0C DB 01 2F 01 3B 18 | 5F 07 25 C6 77 05 16 78 | | 53 0C A3.01 2F 01 8F.08.| 5F 94.15.C6 77 05 16 78 |
0x0110 | 8E 12 52 0F 64 02 0B 00 | 5E 88 15 E0 06 3D 07 77 | | 8E 12 52 0F 64 02 0B 00 | 5E 88 15 E0 06 3D 07 77 |
0x0120 | 07 88 77 2D E2 89 17 7F | 07 25 2C 24 85 00 0D 00 | | 07 88 77 2D E2 89 17 7F | 94.15.2C 24 85 00 0D 00 |
0x0130 | B0 42 7E 07 0A 35 1B DB | 00 CD 2F DF 29 11 7D 08 | | B0 42 7E 07 0A 89.0B.A3.| 00 CD 2F DF 29 11 7D 08 |
0x0140 | 81 10 35 1E 36 25 89 17 | FE F1 BE 1C 81 04 14 80 | | 81 10 89.0E.36 25 89 17 | FE F1 97.1C 81 04 14 80 |
0x0150 | DA 00 36 1B 89 17 87 00 | 26 2D EA F1 85 00 15 54 | | A2.00 8A.0B.89 17 87 00 | 26 2D EA F1 85 00 15 54 |
0x0160 | 35 1C 89 10 03 F8 14 02 | F8 1B 39 8F 25 A7 03 B3 | | 89.0C.89 10 03 F8 14 02 | F8 1B 39 53.05.A7 03 B3 | 
0x0170 | 02 5B 12 7F 06 16 35 1E | 1B 25 00 1B 25 1A FF 34 | | 02 5B 12 7F 06 16 89.0E.| 1B 25 00 1B 25 1A FF 34 |
0x0180 | 89 17 38 D3 3C 85 00 BD | 17 DA 06 58 58 58 40 EB | | 89 17 38 D3 3C 85 00 BD | 17 A2.06 58 58 58 40 EB |
0x0190 | F0 34 28 1F 01 42 40 1E | 01 78 EB F0 94 4C 01 EB | | F0 34 28 1F 01 42 40 1E | 01 78 EB F0 94 4C 01 EB |
0x01A0 | F0 55 EC EB F0 08 5E 00 | 1C EF F0 B0 EF F0 51 70 | | F0 55 EC EB F0 08 5E 00 | 1C EF F0 B0 EF F0 51 70 |
0x01B0 | EF F0 42 41 66 45 A4 EF | F0 EC EF F0 55 C0 67 44 | | EF F0 42 41 66 45 A4 EF | F0 EC EF F0 55 C0 67 44 |
0x01C0 | E0 EF F0 2C FB F0 60 FB | F0 A5 A4 FB F0 E8 C6 11 | | E0 EF F0 2C FB F0 60 FB | F0 A5 A4 FB F0 E8 9F.11 |
0x01D0 | EB F0 48 EB F0 64 2A EB | F0 80 EB F0 9C EB F0 C8 | | EB F0 48 EB F0 64 2A EB | F0 80 EB F0 9C EB F0 C8 |
0x01E0 | 5F 01 EB F0 55 10 5E 00 | 24 EF F0 B8 EF F0 F4 EF | | 5F 01 EB F0 55 10 5E 00 | 24 EF F0 B8 EF F0 F4 EF |
0x01F0 | F0 15 34 FB F0 68 FB F0 | AC FB F0 08 41 C6 41 84 | | F0 15 34 FB F0 68 FB F0 | AC FB F0 08 41 C6 41 64.|
0x0200 | FE 31 CA 41 1C FF 30 CE | 41 EC F3 67 01 7B 25 02 | | FE 31 CA 41 1C FF 30 CE | 41 00.00.EE.F1.96.67.01.|
0x0210 | 9E 41 02 ED F0 A2 41 03 | ED F0 A6 41 49 04 ED F0 | | 7B.02.9E.41.02.EB.40.A2.| 41.03.24.EB.40.A6.41.04.|
0x0220 | AA 41 05 ED F0 AE 41 06 | ED F0 92 B2 41 07 ED F0 | | EB.40.AA.41.05.EB.40.AE.| 41.49.06.EB.40.B2.41.07.|
0x0230 | BA 41 08 ED F0 BE 41 09 | 00 1B 51 ED 40 00 00 00 | | EB.40.BA.41.08.EB.40.FE.| BE.41.09.00.7B.02.F4.02.|
0x0240 |                         |                         | | 00                      |                         |
'''