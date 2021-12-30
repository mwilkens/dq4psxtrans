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

    # At a given index and position, just iterate through to see how long our match is
    def findMatch(buff, idx, data, pos):
        l = 0
        while True:
            # length can't extend beyond the data we're trying to compress
            if (pos+l) >= len(data):
                break
            # length can't be greater than 18
            if l >= 0x12:
                break
            # buffer cycles at 4096, this allows us to
            # use the beginning of the data with leading zeros if we need
            if buff[(idx+l)%0xFFF] == data[pos+l]:
                l += 1
            else:
                break
        # if our match was less than two, then we failed
        if l < 3:
            return -1
        return l

    # here's my best emulation of the algorithm heartbeat uses
    def findLongestMatch( data, pos ):
        # "best" distance and length, start with a best of 2
        bdist = -1
        blen = 2

        # Create a 4096 buffer
        buffer = bytearray(4096)

        # we need the data we've written plus some "lookahead"
        # since occasionally we match to data we've already "written"
        # I'm using just 18 bytes of lookahead and I'm pretty sure we could
        # go shorter
        if pos < 0x12:
            lookahead = pos # no lookahead in the first 18 bytes
        elif pos >= len(data)-0xF:
            lookahead = len(data) # this is just to not break things
        else:
            lookahead = pos+0xF
        for i in range(0,lookahead):
            if i < len(data):
                buffer[i%0xFFF] = data[i]

        l = -1
        # first we start by looking at the last 18 bytes of the buffer
        # we go backwards so our best match will be the closest to the
        # end as possible, which is how HeartBeat does it
        # A really smart person will notice that this is actually the last 17 bytes
        # and they'd be right, but for some reason HeartBeat does this too
        for i in range( 0xFFF, 0xFFF-0x12, -1):
            # look for the longest match at the current pos
            l = findMatch(buffer,i,data,pos)
            # if its better than the last, save it
            if l > blen:
                bdist = i+1
                blen = l
        
        # now we can go through the data, from index 0 to our current pos
        # same deal here tho, if we find a match and its longer than the last
        # save it.
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

    while idx < len(in_data):
        cbuf = 0
        dbuf = []
        # We need to find 8 matches or raw bytes
        for i in range( 0, 8, 1 ):
            # check to see if we can find a match at the current index
            match = findLongestMatch( in_data, idx )
            # if we found something, our distance will not be -1
            if match[0] != -1:
                # no need to do anything to cbuf, 0 already there :)

                # First byte is length minus 3, second is offset minus 18
                b1 = (match[1] - 3) | ((match[0]-18) & 0xF00) >> 4
                b2 = (match[0]-18) & 0xFF
                dbuf.append( b2 )
                dbuf.append( b1 )

                # skip however many bytes we found
                idx += match[1]
            else:
                cbuf |= 1 << i
                try:
                    dbuf.append( in_data[idx] )
                except Exception as e:
                    ''' do nothing '''
                idx += 1
        comp.append(cbuf)
        [ comp.append(v) for v in dbuf ]

    return comp

'''

Decompressed
B9
0x0000 | 7B 02 00 00 0C 00 00 00 | 00 00 00 00 F0 03 00 00 | {#..#.......##..
0x0010 | 18 00 00 00 0E 00 00 00 | 00 00 00 00 00 00 00 00 | #...#...........
0x0020 | 0D 00 00 00 00 00 00 00 | 00 00 00 00 00 00 00 00 | #...............
0x0030 | 5C 00 00 00 4C 04 00 00 | AC 04 00 00 E4 04 00 00 | \...L#..##..##..
0x0040 | E4 04 00 00 00 00 00 00 | 00 00 00 00 00 00 00 00 | ##..............
0x0050 | 00 00 00 00 00 00 00 00 | 00 00 00 00 B1 00 00 00 | ............#...
0x0060 | 00 C0 21 A0 C6 00 00 00 | B4 01 A0 E1 03 00 B3 02 | .#!##...#####.##
0x0070 | 01 00 00 00 F4 21 A0 01 | 00 00 00 01 00 C0 21 A0 | #...#!##...#.#!#
0x0080 | B9 00 00 00 B4 01 A0 E1 | 03 00 B3 02 01 00 00 00 | #...#####.###...
0x0090 | C0 21 A0 01 00 00 00 F1 | 06 3A 00 00 B2 00 00 00 | #!##...##:..#...
0x00A0 | 00 43 43 43 B1 00 00 00 | 00 C0 21 A0 01 00 00 00 | .CCC#....#!##...
0x00B0 | F1 06 3A 03 00 B0 B0 B0 | B2 00 00 00 00 43 43 43 | ##:#.####....CCC
0x00C0 | B1 00 00 00 00 C0 21 A0 | 01 00 00 00 F1 06 3A 04 | #....#!##...##:#
0x00D0 | 00 B0 B0 B0 B2 00 00 00 | 00 43 43 43 B1 00 00 00 | .####....CCC#...
0x00E0 | 00 C0 21 A0 01 00 00 00 | F1 06 3A 05 00 B0 B0 B0 | .#!##...##:#.###
0x00F0 | B2 00 00 00 00 43 43 43 | B1 00 00 00 00 C0 21 A0 | #....CCC#....#!#
0x0100 | CD 00 00 00 B4 01 A0 E1 | 03 00 B3 02 01 00 00 00 | #...#####.###...
0x0110 | C0 21 A0 01 00 00 00 F1 | 06 3A 06 00 B2 00 00 00 | #!##...##:#.#...
0x0120 | 00 43 43 43 B1 00 00 00 | 00 C0 21 A0 CF 00 00 00 | .CCC#....#!##...
0x0130 | B4 01 A0 E1 03 00 B3 02 | 01 00 00 00 C0 21 A0 01 | #####.###...#!##
0x0140 | 00 00 00 F1 06 3A 07 00 | B2 00 00 00 00 43 43 43 | ...##:#.#....CCC
0x0150 | B1 00 00 00 00 C0 21 A0 | 01 00 00 00 F1 06 3A 08 | #....#!##...##:#
0x0160 | 00 B0 B0 B0 B2 00 00 00 | 00 43 43 43 B1 04 00 00 | .####....CCC##..
0x0170 | 00 C0 26 78 FB 0C FE FF | FF C0 26 78 FC 00 00 00 | .#&x######&x#...
0x0180 | 00 C0 26 78 FD F4 01 00 | 00 C0 26 78 FE 00 00 00 | .#&x###..#&x#...
0x0190 | 00 C1 61 A1 B8 FB FF B4 | 01 A1 C0 61 A0 78 01 B4 | .#a########a#x##
0x01A0 | 01 A0 C0 21 A0 B4 01 00 | 00 B4 01 A0 E1 03 02 B3 | ###!###..#######
0x01B0 | 02 03 00 00 00 C0 21 A0 | 00 00 00 00 B4 01 A0 C0 | ##...#!#....####
0x01C0 | 21 A0 00 0C 00 00 B4 01 | A0 C0 21 A0 37 01 00 00 | !#.#..####!#7#..
0x01D0 | B4 01 A0 E1 03 02 B3 02 | 03 00 00 00 C0 21 A0 00 | #########...#!#.
0x01E0 | 00 00 00 B4 01 A0 C0 21 | A0 00 04 00 00 B4 01 A0 | ...####!#.#..###
0x01F0 | C0 21 A0 4A 01 00 00 B4 | 01 A0 E1 03 02 B3 02 03 | #!#J#..#########
0x0200 | 00 00 00 C0 21 A0 00 04 | 00 00 B4 01 A0 C0 61 A0 | ...#!#.#..####a#
0x0210 | 78 01 B4 01 A0 C0 21 A0 | A1 01 00 00 B4 01 A0 E1 | x#####!###..####
0x0220 | 03 02 B3 02 03 00 00 00 | C0 21 A0 F6 FF FF FF B4 | #####...#!######
0x0230 | 01 A0 C0 21 A0 B5 00 00 | 00 B4 01 A0 E1 03 01 B3 | ###!##...#######
0x0240 | 02 02 00 00 00 C0 21 A0 | 21 00 00 00 B4 01 A0 C0 | ##...#!#!...####
0x0250 | 21 A0 CE 00 00 00 B4 01 | A0 E1 03 01 B3 02 02 00 | !##...#########.
0x0260 | 00 00 C0 21 A0 B4 00 00 | 00 B4 01 A0 E1 03 00 B3 | ..#!##...#####.#
0x0270 | 02 01 00 00 00 B0 B0 B0 | B2 04 00 00 00 43 43 43 | ##...#####...CCC
0x0280 | B1 00 00 00 00 C0 21 A0 | 5F 01 00 00 B4 01 A0 E1 | #....#!#_#..####
0x0290 | 03 00 B3 02 01 00 00 00 | C0 16 78 01 A0 C0 21 A0 | #.###...##x###!#
0x02A0 | C6 00 00 00 B4 01 A0 E1 | 03 00 B3 02 01 00 00 00 | #...#####.###...
0x02B0 | F4 21 A0 01 00 00 00 0B | 00 C0 61 A0 78 01 B4 01 | #!##...#.#a#x###
0x02C0 | A0 E0 06 3D 07 00 B3 02 | 01 00 00 00 C0 21 A0 88 | ###=#.###...#!##
0x02D0 | 01 00 00 B4 01 A0 E1 03 | 00 B3 02 01 00 00 00 C0 | #..#####.###...#
0x02E0 | 61 A0 78 01 B4 01 A0 C0 | 21 A0 7F 01 00 00 B4 01 | a#x#####!###..##
0x02F0 | A0 E1 03 01 B3 02 02 00 | 00 00 F1 06 3A 0D 00 B0 | #######...##:#.#
0x0300 | C0 21 A0 01 00 00 00 F1 | 06 3A 0A 00 B2 00 00 00 | #!##...##:#.#...
0x0310 | 00 43 43 43 B1 00 00 00 | 00 B0 B0 B0 C0 61 A0 78 | .CCC#....####a#x
0x0320 | 01 B4 01 A0 C0 21 A0 7F | 01 00 00 B4 01 A0 E1 03 | #####!###..#####
0x0330 | 01 B3 02 02 00 00 00 F1 | 06 3A 11 00 C0 21 A0 01 | ####...##:#.#!##
0x0340 | 00 00 00 F1 06 3A 10 00 | B2 00 00 00 00 43 43 43 | ...##:#.#....CCC
0x0350 | B1 00 00 00 00 C0 21 A0 | 21 00 00 00 B4 01 A0 C0 | #....#!#!...####
0x0360 | 61 A0 78 01 B4 01 A0 C0 | 21 A0 18 00 00 00 B4 01 | a#x#####!##...##
0x0370 | A0 E1 03 02 B3 02 03 00 | 00 00 C0 21 A0 01 00 00 | #######...#!##..
0x0380 | 00 F1 06 3A 14 00 B0 B0 | B2 00 00 00 00 43 43 43 | .##:#.###....CCC
0x0390 | B1 00 00 00 00 C0 61 A0 | 78 01 B4 01 A0 C0 21 A0 | #....#a#x#####!#
0x03A0 | 3A 00 00 00 B4 01 A0 E1 | 03 01 B3 02 02 00 00 00 | :...#########...
0x03B0 | C0 21 A0 00 00 00 00 F1 | 06 3A 15 00 B2 00 00 00 | #!#....##:#.#...
0x03C0 | 00 43 43 43 B1 00 00 00 | 00 C0 61 A0 78 03 B4 01 | .CCC#....#a#x###
0x03D0 | A0 C0 61 A0 78 02 B4 01 | A0 C0 61 A0 78 01 B4 01 | ##a#x#####a#x###
0x03E0 | A0 C0 21 A0 39 00 00 00 | B4 01 A0 E1 03 03 B3 02 | ##!#9...########
0x03F0 | 04 00 00 00 C0 21 A0 01 | 00 00 00 F1 06 3A 16 00 | #...#!##...##:#.
0x0400 | B2 00 00 00 00 43 43 43 | B1 00 00 00 00 C0 21 A0 | #....CCC#....#!#
0x0410 | 1B 00 FF FF B4 01 A0 C0 | 21 A0 1A 00 FF FF B4 01 | #.######!##.####
0x0420 | A0 C0 61 A0 78 01 B4 01 | A0 C0 21 A0 38 00 00 00 | ##a#x#####!#8...
0x0430 | B4 01 A0 E1 03 03 B3 02 | 04 00 00 00 F1 06 3A 17 | #########...##:#
0x0440 | 00 B0 B0 B0 B2 00 00 00 | 00 58 58 58 40 00 00 00 | .####....XXX@...
0x0450 | 34 00 00 00 4C 4C 4C 4C | 5C 00 00 00 78 00 00 00 | 4...LLLL\...x...
0x0460 | 94 00 00 00 C0 00 00 00 | EC 00 00 00 08 01 00 00 | #...#...#...##..
0x0470 | 1C 02 00 00 B0 02 00 00 | 70 02 00 00 4C 4C 4C 4C | ##..##..p#..LLLL
0x0480 | 70 02 00 00 4C 4C 4C 4C | A4 02 00 00 EC 02 00 00 | p#..LLLL##..##..
0x0490 | C0 02 00 00 4C 4C 4C 4C | E0 02 00 00 2C 03 00 00 | ##..LLLL##..,#..
0x04A0 | 60 03 00 00 A4 03 00 00 | E8 03 00 00 00 00 00 00 | `#..##..##......
0x04B0 | 48 00 00 00 64 00 00 00 | 80 00 00 00 9C 00 00 00 | H...d...#...#...
0x04C0 | C8 00 00 00 F4 00 00 00 | 10 01 00 00 24 02 00 00 | #...#...##..$#..
0x04D0 | B8 02 00 00 F4 02 00 00 | 34 03 00 00 68 03 00 00 | ##..##..4#..h#..
0x04E0 | AC 03 00 00 1A 00 FF FF | 34 03 00 00 1B 00 FF FF | ##..#.##4#..#.##
0x04F0 | 68 03 00 00 1C 00 FF FF | AC 03 00 00 00 00 7B 02 | h#..#.####....{#
0x0500 | 00 00 00 00 01 00 7B 02 | 48 00 00 00 02 00 7B 02 | ....#.{#H...#.{#
0x0510 | 64 00 00 00 03 00 7B 02 | 80 00 00 00 04 00 7B 02 | d...#.{##...#.{#
0x0520 | 9C 00 00 00 05 00 7B 02 | C8 00 00 00 06 00 7B 02 | #...#.{##...#.{#
0x0530 | F4 00 00 00 07 00 7B 02 | 24 02 00 00 08 00 7B 02 | #...#.{#$#..#.{#
0x0540 | B8 02 00 00 09 00 7B 02 | F4 02 00 00

'''