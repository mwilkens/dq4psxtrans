from itertools import count
from helpers import *
from huffman import *

# Data Class for 2048 byte blocks
class Block:
    #TODO: Add data offset
    headerLen = 16
    _ids = count(0)
    def __init__(self, sb=0, s=0, l=0, zb=0):
        self.id = next(self._ids)
        self.numSubBlocks = sb
        self.subBlocks = []
        self.sectors = s
        self.length = l
        self.zeroBytes = zb
        self.data = 0
    
    def parseHeader(self, header):
        header = int.from_bytes(header,byteorder='little')
        self.numSubBlocks = ( header & 0xFFFFFFFF )
        header = header >> 32
        self.sectors = ( header & 0xFFFFFFFF )
        header = header >> 32
        self.length = ( header & 0xFFFFFFFF )
        header = header >> 32
        self.zeroBytes = ( header & 0xFFFFFFFF )
    
    def printBlockInfo(self):
        print( "BLOCK #%d: SB(%d) S(%d) L(%d) ZB(%d)" % \
            (self.id, self.numSubBlocks, \
            self.sectors, self.length, self.zeroBytes) )
    
# Data Class for SubBlocks within Blocks
class SubBlock:
    #TODO: Add data offset
    headerLen = 16
    def __init__(self, _id=0):
        self.id = _id
        self.length = 0
        self.compLength = 0
        self.unknown = 0
        self.flags = 0
        self.type = 0
        self.data = 0
    
    def parseHeader(self, header):
        header = int.from_bytes(header,byteorder='little')
        self.compLength = ( header & 0xFFFFFFFF )
        header = header >> 32
        self.length = ( header & 0xFFFFFFFF )
        header = header >> 32
        self.unknown = ( header & 0xFFFFFFFF )
        header = header >> 32
        self.flags = ( header & 0xFFFF )
        header = header >> 16
        self.type = ( header & 0xFFFF )
    
    def printBlockInfo(self):
        print( "-- SUBBLOCK #%02d: CL(%6d) L(%6d) U(%08X) F(%4d) T(%4d)" % \
            (self.id, self.compLength, \
            self.length, self.unknown, self.flags, \
            self.type ) )

# Data Class for SubBlocks within Blocks
class TextBlock:
    #TODO: Add data offset
    headerLen = 24
    def __init__(self, _id=0):
        self.a = 0
        self.a_off = 0
        self.uuid = 0
        self.huff_c = 0
        self.huff_d = 0
        self.huff_e = 0
        self.zero = 0
    
    def parseHeader(self, header):
        header = int.from_bytes(header,byteorder='little')
        self.a_off = ( header & 0xFFFFFFFF )
        header = header >> 32
        self.uuid = ( header & 0xFFFFFFFF )
        header = header >> 32
        self.huff_c = ( header & 0xFFFFFFFF )
        header = header >> 32
        self.huff_d = ( header & 0xFFFFFFFF )
        header = header >> 32
        self.huff_e = ( header & 0xFFFFFFFF )
        header = header >> 32
        self.zero = ( header & 0xFFFFFFFF )

    def parseBody( self, body ):
        # Calculate A, this will be the same as a_off if everything worked right :)
        self.a = byteRead( body, self.a_off, 2, decode=False )
        # This is the text itself, but huffman encoded
        self.encData = byteSlice( body, self.huff_c, self.huff_e, decode=False )
        # Not sure what these are, but they could be important
        self.e1 = byteRead( body, self.huff_e, 4)
        self.e2 = byteRead( body, self.huff_e+4, 4)
        self.e3 = byteRead( body, self.huff_e+8, 2)
        
        # Occasionally d is zero, which means we need to set d to a
        self.d_a = None
        if( self.huff_d == 0):
            self.huff_d = self.a_off
        else:
            # If we do have d, we can extract this range, not sure what it is though
            self.d_a = byteSlice( body, self.huff_d, self.a_off, decode=False )
        
        # This is the actual huffman tree
        self.huffTree = byteSlice( body, self.huff_e+10, self.huff_d, decode=False )
        
        if( self.uuid == 0x006C ):
            tree = makeHuffTree( self.huffTree )
            text = decodeHuffman( self.encData, tree )
            for line in text:
                print( line )
    
    def printBlockInfo(self):
        print( "-- -- TEXTBLOCK #%08X: A(%08X) HB(%08X) HT(%08X) HE(%08X) Z(%08X)" % \
            (self.uuid, self.a_off, \
            self.huff_c, self.huff_d, self.huff_e, \
            self.zero ) )
