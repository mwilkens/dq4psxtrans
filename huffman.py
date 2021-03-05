from shiftjis import decodeShiftJIS

def makeHuffTree( rawHuff ):
    huffTree = {}
    rawHuff = list(rawHuff)
    raw_length = len(rawHuff)
    for i in range( raw_length >> 1 ):
        firstByte = rawHuff.pop()
        secondByte = rawHuff.pop()
        if( firstByte == 0 and secondByte == 0 ):
            print("null")
            continue
        # If we have a node
        if( (firstByte&0xF0) == 0x80 ):
            node = (firstByte << 8) + secondByte - 0x8000
            print( "Node: %X" % node )
        elif( firstByte == 0x7F ):
            print( "Control: %02X" % secondByte )
        else:
            firstByte += 0x80
            encLetter = (firstByte << 8) + secondByte
            decLetter = decodeShiftJIS( encLetter )
            print( "Leaf: %04X " % encLetter, decLetter )

'''
== Encoded ==
7D 02 00 00 

== Decoded ==
ダミーnu

== Tree ==
Node:  2
Node:  1
Leaf: 837E  ミ
Control: 0B
Node:  0
Leaf: 835F  ダ
Leaf: 815B  ー
null

'''