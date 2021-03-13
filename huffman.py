from shiftjis import decodeShiftJIS
from helpers import printHex

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

#TODO: Deal with {7fxx} characters here smh
def genFreqTable( text ):
    ft = {}
    for char in text:
        if char in ft:
            ft[char] += 1
        else:
            ft[char] = 1
    return ft

def createNode( ft, num ):
    # Get the first minimum
    min1k = min( ft, key=ft.get )
    min1v = ft[min1k]
    del ft[min1k]
    # Get the second minimum
    min2k = min( ft, key=ft.get )
    min2v = ft[min2k]
    del ft[min2k]
    # Create node
    node = {min1k:min1v,min2k:min2v}
    ft[num] = min1v + min2v
    return [ft,node]

def bitStr2Bytes(s):
    return int(s, 2).to_bytes((len(s) + 7) // 8, byteorder='big')

def encodeHuffman( text ):
    huffTree = ""
    nodes = {}
    # Generate character frequency table
    ft = genFreqTable( text )
    # Create nodes using min-heap
    nn = 0
    while len(ft) != 1:
        [ft,nodes[nn]] = createNode(ft, nn)
        nn += 1
    
    # Building Huffman Tree (using recursion)
    def unpack(branch):
        rt = {}
        for n in [*branch]:
            if type(n) == int:
                rt[nn - n - 1] = unpack(nodes[n])
            else:
                rt[n] = branch[n]
        return rt
    ft = unpack(ft)

    # Create codes for each character
    def traverse(branch, curCode):
        codeList = {}
        stem = [*branch]
        if type(stem[0]) == int:
            codeList.update( traverse(branch[stem[0]],curCode + '0') )
        else:
            codeList[stem[0]] = curCode + '0'

        if type(stem[1]) == int:
            codeList.update( traverse(branch[stem[1]],curCode + '1') )
        else:
            codeList[stem[1]] = curCode + '1'
        return codeList
    codeList = traverse( ft[0], '' )
    
    # Actually encode the string with our new codes
    huffmanStr = ''
    for char in text:
        huffmanStr += codeList[char]
    huffmanCode = bitStr2Bytes( huffmanStr )
    
    printHex( huffmanCode )


sampleText = "Ye can't turn me down like that! Please!{7f0a}{7f02}'Tis forbidden to enter into the castle at night.{0000}"

encodeHuffman( sampleText )