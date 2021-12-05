from itertools import count
from libs.huffman import *
from libs.helpers import *

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

        self.header = 0
        self.body = 0

        # Main Block
        self.a = 0
        self.a_off = 0
        self.uuid = 0
        self.huff_c = 0
        self.huff_d = 0
        self.huff_e = 0
        self.zero = 0

        # D Blocks
        self.one = 0
        self.d1_off = 0
        self.d2_off = 0
        self.d_var = [0,0,0,0,0,0]

        # Decoded Outputs of the TextBlock
        self.hufftree = []
        self.encHuffTree = 0
        self.decText = {}
    
    def parseHeader(self, header):
        self.header = header # save the byte version
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
    
    def parseDHeader(self, dheader):
        self.one = ( dheader & 0xFFFFFFFF )
        dheader = dheader >> 32
        self.d1_off = ( dheader & 0xFFFFFFFF )
        dheader = dheader >> 32
        self.d2_off = ( dheader & 0xFFFFFFFF )
        dheader = dheader >> 32
        # 6 vars come after
        for i in range(6):
            self.d_var[i] = ( dheader & 0xFFFF )
            dheader = dheader >> 16
    
    def printDHeader(self):
        print("-- -- -- D BLOCK O(%08X) D1(%08X) D2(%08X) DV[%04X,%04X,%04X,%04X,%04X,%04X]" % ( \
            self.one, self.d1_off, self.d2_off, \
            self.d_var[0],self.d_var[1],self.d_var[2],self.d_var[3],self.d_var[4],self.d_var[5]) )
        print( "D1 Length: %04X, D2 Length: %04X" % (self.d2_off - self.d1_off, self.a_off - self.d2_off ))

    def parseBody( self, body ):
        self.body = body
        # Calculate A, this will be the same as a_off if everything worked right :)
        self.a = byteRead( body, self.a_off, 2, decode=False )
        # This is the text itself, but huffman encoded
        self.encData = byteSlice( body, self.huff_c, self.huff_e, decode=False )
        # Not sure what these are, but they could be important
        self.e1 = byteRead( body, self.huff_e, 4 )
        self.e2 = byteRead( body, self.huff_e+4, 4 )
        self.e3 = byteRead( body, self.huff_e+8, 2 )
        
        # Occasionally d is zero, which means we need to set d to a
        self.d_a = None
        if self.huff_d == 0:
            self.huff_d = self.a_off
        else:
            # If we do have d, we can extract this range, not sure what it is though
            self.d_a = byteSlice( body, self.huff_d, self.a_off, decode=False )
            self.dheader = byteRead( body, self.huff_d, 28 )
            self.parseDHeader( self.dheader )
            #self.printDHeader()

            self.d1 = byteSlice( body, self.d1_off, self.d2_off, decode=False )
            self.d2 = byteSlice( body, self.d2_off, self.a_off, decode=False )

            '''if( self.d2_off - self.d1_off < 0x50 ):
                print("D1 Block")
                printHex( self.d1 )
                print("D2 Block")
                printHex( self.d2 )'''
        
        # Read to the end of the block
        self.end_counter = byteRead( body, self.a_off+4, 4 )
        self.end_block = byteRead( body, self.a_off+8, self.end_counter * 8, decode=False )
        
        # This is the actual huffman tree
        self.encHuffTree = byteSlice( body, self.huff_e+10, self.huff_d, decode=False )
        
        self.hufftree = makeHuffTree( self.encHuffTree )
        self.decText = decodeHuffman( self.huff_c, self.encData, self.hufftree )

        #print( "a:%02X, e's: [%04X,%04X,%02X], htlen:%04X, edlen:%04X" %
        #    (self.a[0], self.e1, self.e2, self.e3, len(self.encHuffTree), len(self.encData)) )
    
    def printBlockInfo(self):
        print( "-- -- TEXTBLOCK #%08X: A(%08X) HC(%08X) HE(%08X) HD(%08X) Z(%08X)" % \
            (self.uuid, self.a_off, \
            self.huff_c, self.huff_e, self.huff_d, \
            self.zero ) )
    
    def encodeTranslation(self, translatedText):
        # If we don't have text, don't translate
        if translatedText == None or translatedText == "":
            return
        
        # Otherwise encode the text
        [encText, encTree] = encodeHuffman( translatedText )

        ## Structure: ##
        # 1. Header (24 Bytes)
        # 2. Huffman Code (hLen Bytes)
        codeLen = length(encText)
        # 3. E Section (10 Bytes)
        # 4. Huffman Tree (tLen Bytes)
        encTree = length(encTree)
        # 5. D Section Header (28 Bytes)
        # 6. D1 Block (d1Len Bytes)
        # 7. D2 Block (d2Len Bytes)
        dLen = (self.a_off - self.huff_d)
        # 8. Counter (4 bytes)
        # 8. Everything else (counter*8 bytes)

        # Create the array
        buffer = bytearray()

        #######################
        ## Create new header ##
        #######################

        # A Offset (4 bytes) = header + code + e + tree + d
        new_a_off = 24 + codeLen + 10 + treeLen + dLen
        buffer.extend( new_a_off.to_bytes( 4, 'little' ) )

        # Dialog ID (4 bytes)
        buffer.extend( self.uuid )

        # Huff C (4 bytes) (always 0x18)
        buffer.extend( self.huff_c )

        # Huff D (3 bytes) = A off - huff d
        new_huff_d = new_huff_a - dLen
        buffer.extend( new_huff_d.to_bytes( 4, 'little' ) )

        # Huff E (4 bytes) = header + code
        new_huff_e = 24 + codeLen
        buffer.extend( new_huff_e.to_bytes( 4, 'little' ) )

        # Zero (4 bytes)
        buffer.extend( (0).to_bytes( 4,'little' ) )

        #######################
        ##  Insert New Body  ##
        #######################
        buffer.extend( encText )

        #######################
        ##      E Block      ##
        #######################

        # e1 (4 bytes) = tree offset
        new_e1 = 24 + codeLen + 10
        buffer.extend( new_e1.to_bytes( 4,'little' ) )

        # e1 (4 bytes) = tree length
        buffer.extend( treeLen.to_bytes( 4,'little' ) )

        # e3 (2 bytes) - number of nodes
        new_e3 = encTree[-4] + 1
        buffer.extend( new_e3.to_bytes( 2, 'little' ) )

        #######################
        ##  Insert New Tree  ##
        #######################
        buffer.extend( encTree )

        #######################
        ## Preserved Ending  ##
        #######################
        if self.huff_d != 0:
            buffer.extend( self.d_a )
        buffer.extend( self.a_off.to_bytes(4,'little') )
        buffer.extend( self.end_counter.to_bytes(4,'little') )
        buffer.extend( self.end_block)

        return buffer