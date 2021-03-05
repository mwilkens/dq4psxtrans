from shiftjis import decodeShiftJIS

def parseTree( switch, offset, curNode, bytes):
    index = curNode * 2 + ( offset if switch else 0 )
    hByte = bytes[ index + 1 ]
    lByte = bytes[ index ]

    # If we have a node
    if( (hByte&0xF0) == 0x80 ):
        node = (hByte << 8) + lByte - 0x8000
        # Create a new node
        temp = [None,None]
        temp[0] = parseTree( 0, offset, node, bytes)
        temp[1] = parseTree( 1, offset, node, bytes)
        return temp
    elif( hByte == 0x7F ):
        return "{%02x%02x}" % (hByte, lByte)
    elif(hByte == 0 and lByte == 0):
        return "{0000}"
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

def decodeHuffman( offset, code, huff ):
    dText = ""
    dialog = []
    tempTree = huff
    byte_idx = 0
    start = offset
    for byte in code:
        # Count down from the end
        for i in range(8):
            # extremely confusing bit of logic, but it just checks if the bit is a 1 or a 0
            code = 1 if (byte & (1 << i) > 0) else 0
            # if we have a list we have to go further...
            if( type(tempTree[code]) == list ):
                tempTree = tempTree[code]
            else:
                dText = ''.join([dText,tempTree[code]])
                if( tempTree[code] == '{0000}' ):
                    dialog.append( {'text':dText,'offset':'0x%04X' % start} ) 
                    dText = ""
                    start = byte_idx + offset
                tempTree = huff
        byte_idx += 1
    return dialog


'''

7D 02 00 00


'''