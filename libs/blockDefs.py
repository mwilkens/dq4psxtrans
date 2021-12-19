from itertools import count
from libs.huffman import *
from libs.helpers import *
from libs.lzs import decompress

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

# Data Class for SubBlocks within Blocks
class ScriptBlock:
    def __init__(self, _id=0):
        self.headerLen = 92

        self.opCodes = {
            'c01678': { 'raw': None, 'data': [], 'dataLen': [1], 'mod': None },
            'c021a0': { 'raw': None, 'data': [], 'dataLen': [2,2], 'mod': None },
            'c02678': { 'raw': None, 'data': [], 'dataLen': [3], 'mod': None },
            'c02639': { 'raw': None, 'data': [], 'dataLen': [3], 'mod': None },
            'c0263b': { 'raw': None, 'data': [], 'dataLen': [4], 'mod': None },
            'c061a0': { 'raw': None, 'data': [], 'dataLen': [2], 'mod': None },
            'c161a1': { 'raw': None, 'data': [], 'dataLen': [3], 'mod': None },
            'c211a1': { 'raw': None, 'data': [], 'dataLen': [1], 'mod': None },
            'c40678': { 'raw': None, 'data': [], 'dataLen': [1], 'mod': None },
            'c821a0': { 'raw': None, 'data': [], 'dataLen': [2], 'mod': None },
            
            'e0063d': { 'raw': None, 'data': [], 'dataLen': [6], 'mod': None },
            'e10300': { 'raw': None, 'data': [], 'dataLen': [4], 'mod': None },
            'e10301': { 'raw': None, 'data': [], 'dataLen': [4], 'mod': None },
            'e10302': { 'raw': None, 'data': [], 'dataLen': [4], 'mod': None },
            'e10303': { 'raw': None, 'data': [], 'dataLen': [4], 'mod': None },
            'e10305': { 'raw': None, 'data': [], 'dataLen': [4], 'mod': None },

            'f1063a': { 'raw': None, 'data': [], 'dataLen': [2], 'mod': None },
            'f421a0': { 'raw': None, 'data': [], 'dataLen': [6], 'mod': None },
            'f761a0': { 'raw': None, 'data': [], 'dataLen': [4], 'mod': None },
        }
        '''
        Opcodes:
        -- Functions --
        <c01678> <1 bytes> (<a0> keyword always follows, maybe starts a loop or conditional?)
        <c021a0> <2 bytes> <2 bytes>
        <c02678> <1 byte> <1 byte> <1 byte> <2 bytes>
        <c02639> <3 bytes> (only seen 1 of these, related to c211a1)
        <c0263b> <4 bytes> (only seen 1 of these, related to c02639)
        <c061a0> <2 bytes> (always seen after c021a0 with dialog info)
        <c161a1> <3 bytes> (some kind of address, often b8fbff or b8faff)
        <c211a1> <1 bytes> (only seen 1 of these, related to c02639)
        <c40678> <1 bytes> (only seen 1 of these)
        <c821a0> <2 bytes> <2 bytes> (related to c40678 probably)
        -- Subsection Commands --
        <e0063d> <2 bytes>
        <e10300> <no arg> 
        <e10301> <no arg> 
        <e10302> <no arg> 
        <e10303> <no arg> 
        <e10305> <no arg> 
        -- Jump Commands --
        <f1063a> <2 bytes> (absolutely related to the b keywords)
        <f421a0> <4 bytes> <2 bytes> (2nd argument increases throughout script, goto command?)
        <f761a0> <2 bytes> <2 bytes> (similar to f421a0 but 1st command is much larger)
        -- Non-standard --
        <434343> (called between b1 and b2 keywords)

        Keywords:
        <b0> (usually but not always seen with f1063a)
        <b1> (start of major section)
        <b2> (end of major section)
        <b3> (separator of minor sections)
        <b4> (some sort of separator, always followed by 01aX)
        <a0> (found with c01678, seen in a lot of op-codes too so not sure about this one)
        <01a0> (always found between commands)
        <01a1> (always found between commands)
        '''
        self.keywords = [
            'b0', 'b1', 'b2', 'b3', 'b4', 'a0', '01a0', '01a1'
        ]

        self.header = 0
        self.body = 0

        # Header Info
        self.info = []
        
        # Body Script Tree
        self.script = {}
    
    def parse(self, rawBlock, parent):
        if parent.flags == 1280:
            self.body = decompress( rawBlock, parent.length)
        else:
            self.body = rawBlock
        self.parseHeader( self.body[:self.headerLen] )
        self.parseBody( self.body[self.headerLen:] )
    
    def parseHeader(self, header):
        self.header = header # save the byte version
        data = [self.header[i:i+4] for i in range(0,len(self.header),4)]
        for raw in data:
            val = int.from_bytes(raw,byteorder='little')
            self.info.append(val)
    
    def checkKeyword(self, buff, kwds):
        strbuff = ''
        for c in buff:
            strbuff += f"{c:02x}"
        for kwd in kwds:
            invalidChar = False
            if len(strbuff) != len(kwd):
                continue
            for i in range(len(strbuff)):
                invalidChar = invalidChar or (strbuff[i]!=kwd[i] and kwd[i]!='*')
            if not invalidChar:
                return True,kwd
        return False,strbuff

    def parseBody(self, body):
        return
        self.body = body
        print( len(body) )

        buff = []

        # First two characters always 0x00
        body = body[1:]

        for x in body:
            print(f'{x:02X}')
            buff.append(x)
            if len(buff) == 1 or len(buff) == 2:
                found, kwd = self.checkKeyword(buff, self.keywords)
                if found:
                    print( f"Found Keyword: {kwd}")
                    buff = []
                if len(buff) == 4 and not found:
                    buff = []
            if len(buff) == 3:
                print( buff )
                found, opc = self.checkKeyword(buff, self.opCodes.keys())
                if found:
                    print( f"Found OpCode: {opc}")
                    buff = []
                else:
                    print( f"Invalid OpCode: {opc}")
                    buff = []
            if len(buff) > 3:
                buff = []
                return