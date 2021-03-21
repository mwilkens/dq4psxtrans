
from libs.shiftjis import decodeShiftJIS, encodeShiftJIS
from libs.helpers import printHex

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

def genFreqTable( text ):
    ft = {}
    isControl = False
    ctrlBuff = ''
    for char in text:
        if char == '{':
            isControl = True
            continue
        elif char == '}':
            isControl = False
            if ctrlBuff in ft:
                ft[ctrlBuff] += 1
            else:
                ft[ctrlBuff] = 1
            ctrlBuff = ''
            continue
        
        if isControl:
            ctrlBuff += char
            continue

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
    bStr = b''
    byt = ''
    for bit in s:
        byt += bit
        if len(byt) == 8:
            bStr += bytes([int(byt[::-1],2)])
            byt = ''
    if byt != '':
        byt = byt.ljust(8,'0')
        bStr += bytes([int(byt[::-1],2)])
    return bStr

def encTree( node, offset, tree, nodeNum=None ):
    # if we're the root node
    if nodeNum == None:
        nodeNum = [*node][0]
        node = node[nodeNum]
        tree[-4] = nodeNum
        tree[-3] = 0x80
    idx1 = nodeNum*2
    idx2 = nodeNum*2 + offset

    leafs = [*node]
    if type(node[leafs[0]]) == dict:
        tree[idx1] = leafs[0]
        tree[idx1+1] = 0x80
        tree = encTree( node[leafs[0]], offset, tree, nodeNum=leafs[0] )
    elif len(leafs[0]) == 4:
        tree[idx1] = int(leafs[0][2:],16)
        tree[idx1+1] = int(leafs[0][:2],16)
    else:
        val = encodeShiftJIS( leafs[0] )
        tree[idx1] = val[0]
        tree[idx1+1] = val[1]
    if len(leafs) > 1:
        if type(node[leafs[1]]) == dict:
            tree[idx2] = leafs[1]
            tree[idx2+1] = 0x80
            tree = encTree( node[leafs[1]], offset, tree, nodeNum=leafs[1] )
        elif len(leafs[1]) == 4:
            tree[idx2] = int(leafs[1][2:],16)
            tree[idx2+1] = int(leafs[1][:2],16)
        else:
            val = encodeShiftJIS( leafs[1] )
            tree[idx2] = val[0]
            tree[idx2+1] = val[1]
    return tree

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
                rt[n] = unpack(nodes[n])
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
    codeList = traverse( list(ft.values())[0], '' )
    
    # Actually encode the string with our new codes
    huffmanStr = ''
    isControl = False
    ctrlBuff = ''
    for char in text:
        if char == '{':
            isControl = True
            continue
        elif char == '}':
            isControl = False
            huffmanStr += codeList[ctrlBuff]
            ctrlBuff = ''
            continue
        if isControl:
            ctrlBuff += char
            continue
        huffmanStr += codeList[char]
    huffmanCode = bitStr2Bytes( huffmanStr )

    # Create the encoded huffman tree
    rootNode = [*ft][0] + 1
    tree = encTree( ft, rootNode*2, bytearray(rootNode*4) ) + b'\x00\x00'

    return [huffmanCode, tree]

'''
sampleText = "Ye can't turn me down like that! Please!{7f0a}{7f02}'Tis forbidden to enter into the castle at night.{0000}"
[encText, encTree] = encodeHuffman( sampleText )
tree = makeHuffTree( encTree )
text = decodeHuffman( 0, encText, tree )
print( text )
'''