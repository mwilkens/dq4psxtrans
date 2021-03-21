try:
    from libs.shiftjis import decodeShiftJIS, encodeShiftJIS
    from libs.helpers import printHex
except:
    from shiftjis import decodeShiftJIS, encodeShiftJIS
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
    return int(s, 2).to_bytes((len(s) + 7) // 8, byteorder='big')

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

    print( ft )

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
            huffmanStr += codeList[char]
            ctrlBuff = ''
        if isControl:
            ctrlBuff += char
            continue
        huffmanStr += codeList[char]
    huffmanCode = bitStr2Bytes( huffmanStr )
    rootNode = [*ft][0] + 1
    tree = encTree( ft, rootNode*2, bytearray(rootNode*4) ) + b'\x00\x00'

    return [huffmanCode, tree]


sampleText = "Ye can't turn me down like that! Please!{7f0a}{7f02}'Tis forbidden to enter into the castle at night.{0000}"

[encText, encTree] = encodeHuffman( sampleText )

printHex( encTree )

tree = makeHuffTree( encTree )

print( tree )

text = decodeHuffman( 0, encText, tree )

print( text )

'''

{28: 
    {26: {22: {17: {10: {3: {'7f0a': 1, '7f02': 1}, 4: {'T': 1, 'f': 1}}, 11: {5: {'b': 1, 'g': 1}, 6: {'.': 1, '0000': 1}}}, 'e': 10}, 23: {18: {'a': 5, 'i': 5}, 't': 11}},
     27: {24: {19: {12: {'r': 3, 'd': 3}, 13: {'l': 3, 'h': 3}}, 20: {14: {'s': 3, '}': 3}, 'n': 7}}, 25: {' ': 15, 21: {15: {'o': 4, 7: {'c': 2, "'": 2}}, 16: {8: {'!': 2, 0: {'Y': 1, 'u': 1}}, 9: {1: {'m': 1, 'w': 1}, 2: {'k': 1, 'P': 1}}}}}}}}

Index: 56
Found Node: 26
.-Index: 52
.-Found Node: 22
.-.-Index: 44
.-.-Found Node: 17
.-.-.-Index: 34
.-.-.-Found Node: 10
.-.-.-.-Index: 20
.-.-.-.-Found Node: 3
.-.-.-.-.-Index: 6
BAD SHIFTJIS: 0x8A7F
.-.-.-.-.-Found Letter:
BAD SHIFTJIS: 0x8A7F
.-.-.-.-.-Index: 64
BAD SHIFTJIS: 0x827F
.-.-.-.-.-Found Letter:
BAD SHIFTJIS: 0x827F
.-.-.-.-Index: 78
.-.-.-.-Found Node: 4
.-.-.-.-.-Index: 8
.-.-.-.-.-Found Letter: Ｔ
.-.-.-.-.-Index: 66
.-.-.-.-.-Found Letter: ｆ
.-.-.-Index: 92
.-.-.-Found Node: 11
.-.-.-.-Index: 22
.-.-.-.-Found Node: 5
.-.-.-.-.-Index: 10
.-.-.-.-.-Found Letter: ｂ
.-.-.-.-.-Index: 68
.-.-.-.-.-Found Letter: ｇ
.-.-.-.-Index: 80
.-.-.-.-Found Node: 6
.-.-.-.-.-Index: 12
.-.-.-.-.-Found Letter: 。
.-.-.-.-.-Index: 70
.-.-.-.-.-Found control char: 0000
.-.-Index: 102
.-.-Found Letter: ｅ
.-Index: 110
.-Found Node: 23
.-.-Index: 46
.-.-Found Node: 18
.-.-.-Index: 36
.-.-.-Found Letter: ａ
.-.-.-Index: 94
.-.-.-Found Letter: ｉ
.-.-Index: 104
.-.-Found Letter: ｔ
Index: 114
Found Node: 27
.-Index: 54
.-Found Node: 24
.-.-Index: 48
.-.-Found Node: 19
.-.-.-Index: 38
.-.-.-Found Node: 12
.-.-.-.-Index: 24
.-.-.-.-Found Letter: ｒ
.-.-.-.-Index: 82
.-.-.-.-Found Letter: ｄ
.-.-.-Index: 96
.-.-.-Found Node: 13
.-.-.-.-Index: 26
.-.-.-.-Found Letter: ｌ
.-.-.-.-Index: 84
.-.-.-.-Found Letter: ｈ
.-.-Index: 106
.-.-Found Node: 20
.-.-.-Index: 40
.-.-.-Found Node: 14
.-.-.-.-Index: 28
.-.-.-.-Found Letter: ｓ
.-.-.-.-Index: 86
.-.-.-.-Found Letter: ｝
.-.-.-Index: 98
.-.-.-Found Letter: ｎ
.-Index: 112
.-Found Node: 25
.-.-Index: 50
.-.-Found Letter: 　
.-.-Index: 108
.-.-Found Node: 21
.-.-.-Index: 42
.-.-.-Found Node: 15
.-.-.-.-Index: 30
.-.-.-.-Found Letter: ｏ
.-.-.-.-Index: 88
.-.-.-.-Found Node: 7
.-.-.-.-.-Index: 14
.-.-.-.-.-Found Letter: ｃ
.-.-.-.-.-Index: 72
.-.-.-.-.-Found Letter: ’
.-.-.-Index: 100
.-.-.-Found Node: 16
.-.-.-.-Index: 32
.-.-.-.-Found Node: 8
.-.-.-.-.-Index: 16
.-.-.-.-.-Found Letter: ！
.-.-.-.-.-Index: 74
.-.-.-.-.-Found Node: 0
.-.-.-.-.-.-Index: 0
.-.-.-.-.-.-Found Letter: Ｙ
.-.-.-.-.-.-Index: 58
.-.-.-.-.-.-Found Letter: ｕ
.-.-.-.-Index: 90
.-.-.-.-Found Node: 9
.-.-.-.-.-Index: 18
.-.-.-.-.-Found Node: 1
.-.-.-.-.-.-Index: 2
.-.-.-.-.-.-Found Letter: ｍ
.-.-.-.-.-.-Index: 60
.-.-.-.-.-.-Found Letter: ｗ
.-.-.-.-.-Index: 76
.-.-.-.-.-Found Node: 2
.-.-.-.-.-.-Index: 4
.-.-.-.-.-.-Found Letter: ｋ
.-.-.-.-.-.-Index: 62
.-.-.-.-.-.-Found Letter: Ｐ

0x0000 | 40 01 58 03 04 7F 67 03 | 49 01 7E 03 05 80 00 80 |
0x0010 | 00 00 63 01 04 80 08 80 | 06 80 07 80 0A 80 0D 80 |
0x0020 | 0E 80 0B 7F 02 7F 5F 03 | 7D 03 75 01 4B 03 01 80 |
0x0030 | 5B 01 02 80 03 80 93 03 | 8F 03 8B 03 09 80 0C 80 |
0x0040 | 0B 80 0F 80 00 00

Algorithm Description:

1. Remove last two bytes
2. Calculate node from new last two bytes
3. Add one to node num
4. Go through

'''