import math
from libs.helpers import printHex

def decompress( in_data, d_size, verbose=False ):
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
                print( f"{bit} - d - {in_data[offComp]:02X}" ) if verbose else ''

                offComp += 1
                offDecomp += 1
                offBuff += 1

                if offBuff >= maxOff:
                    print( "Flipped Buffer" ) if verbose else ''

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

                print( f"{bit} - d - {in_data[offComp]:02X}{in_data[offComp+1]:02X} {l} {off}" ) if verbose else ''

                for j in range(l):
                    literal = buffer[(off+j) % maxOff]
                    decomp[offDecomp] = literal
                    buffer[offBuff] = literal

                    offDecomp += 1
                    offBuff += 1

                    if offBuff >= maxOff:
                        print( "Flipped Buffer" ) if verbose else ''
                    
                    offBuff = offBuff % maxOff

                offComp += 2
            if offComp >= len(in_data):
                break
        #print(f"Comp: {offComp} - Decomp: {offDecomp} - Buff: {offBuff} - DSize: {d_size} - CSize: {len(in_data)}")
        if fullBreak:
            break
    return decomp

def compress( in_data, verbose=False ):

    buffer = bytearray(4096)
    comp = bytearray()

    # pretty sick of not having this function
    def lget(l, idx, default=None):
        try:
            return l[idx]
        except IndexError:
            return default

    def findLongestMatch( data, pos ):
        # track offset and blen
        bdist = -1
        blen = 2

        # look for a match starting from the end of the buffer
        for i in range(4095,-1,-1):
            if i == pos:
                continue
            if buffer[i] == data[pos]:
                # thats a match, lets see how far it goes
                l = 1
                #print( f"{buffer[(i+l)%4096]:02X} == {lget(data,pos+l):02X}" ) if pos == 0x8B else ''
                while buffer[(i+l)%4096] == lget(data,pos+l):
                    l+=1
                    #print( f"{buffer[(i+l)%4096]:02X} == {lget(data,pos+l):02X}" ) if pos == 0x8B else ''
                    if l>18:
                        l = 18
                        break
                
                if l > blen:
                    #print("Match") if pos == 0x8B else ''
                    bdist = i
                    blen = l

        return (bdist,blen)
    
    idx = 0
    while idx < len(in_data):
        cbuf = 0
        dbuf = []
        # We need to find 8 matches or raw bytes
        for i in range( 0, 8, 1 ):
            # make sure we aren't overprocessing data
            if idx >= len(in_data):
                break
            # put current byte into the buffer
            buffer[idx%4096] = in_data[idx]
            #printHex(buffer[:64])
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

                print( f"0 - c - {b2:02X}{b1:02X} {match[1]} {match[0]}" ) if verbose else ''

                # fill buffer with match
                for i in range(match[1]):
                    buffer[(idx+i)%4096] = lget(in_data,idx+i)
                # skip however many bytes we found
                idx += match[1]
            else:
                cbuf |= 1 << i
                dbuf.append( in_data[idx] )
                print( f"1 - c - {in_data[idx]:02X}") if verbose else ''
                idx += 1
        comp.append(cbuf)
        [ comp.append(v) for v in dbuf ]

    return comp