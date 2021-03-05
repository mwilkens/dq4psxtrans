from shiftjis import decodeShiftJIS

def parseTree( switch, offset, curNode, bytes):
    print("Node %d, Offset %d" % (curNode, offset))
    index = curNode * 2 + ( offset if switch else 0 )
    hByte = bytes[ index + 1 ]
    lByte = bytes[ index ]

    print("Byte: %02X%02X" % (hByte, lByte))

    # If we have a node
    if( (hByte&0xF0) == 0x80 ):
        node = (hByte << 8) + lByte - 0x8000
        # Create a new node
        temp = [None,None]
        temp[0] = parseTree( 0, offset, node, bytes)
        temp[1] = parseTree( 1, offset, node, bytes)
        return temp
    elif( hByte == 0x7F or (hByte == 0 and lByte == 0) ):
        return "{%02x%02x}" % (hByte, lByte)
    else:
        hByte += 0x80
        encLetter = (hByte << 8) + lByte
        return decodeShiftJIS( encLetter )


def makeHuffTree( rawHuff ):
    root = [None,None]
    # Last two bytes are just zeros
    rawHuff = list(rawHuff)[:-2]
    raw_length = len(rawHuff)
    half = int(raw_length / 2)

    # Calculate the root node
    lByte = rawHuff[ raw_length - 2 ] + ( rawHuff[ raw_length - 1 ] << 8 )
    rootNode = 1 + lByte - 0x8000

    root[0] = parseTree( 0, half, rootNode,  rawHuff )
    root[1] = parseTree( 1, half, rootNode,  rawHuff )

    return root