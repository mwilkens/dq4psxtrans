def byteRead( data, offset, length, decode=True ):
    rData = data[ offset : offset + length ]
    if( decode ):
        return int.from_bytes( rData, byteorder='little')
    else:
        return rData

def byteSlice( data, start, end, decode=True ):
    rData = data[ start : end ]
    if( decode ):
        return int.from_bytes( rData, byteorder='little')
    else:
        return rData

def printHex( hex ):
    idx = 0
    print( "0x0000 | ", end='')
    for v in list(hex):
        print( "%02X " % v, end='')
        idx+=1
        if( idx%8==0 ):
            print("| ", end='')
        if( idx%16==0 ):
            print("\n0x%04X | " % idx, end='')
    print('')