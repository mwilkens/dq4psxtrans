from itertools import count
from libs.huffman import *
from libs.helpers import *
from libs.shiftjis import decodeShiftJIS
from libs.lzs import decompress, compress

# Data Class for 2048 byte blocks
class Block:
    #TODO: Add data offset
    headerLen = 16
    _ids = count(0)
    def __init__(self, _id, sb=0, s=0, l=0, zb=0):
        self.id = _id
        self.valid = True
        self.offset = 0
        self.numSubBlocks = sb
        self.subBlocks = []
        self.sectors = s
        self.length = l
        self.zeroBytes = zb
        self.header = 0
        self.data = 0
    
    def parseHeader(self, header):
        self.header = header # save byte version
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
    headerLen = 16
    def __init__(self, _id=0):
        self.id = _id
        self.offset = 0
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

    def recalculateHeader(self):
        header = self.compLength
        header |= self.length << (32*1)
        header |= self.unknown << (32*2)
        header |= self.flags << (32*3)
        header |= self.type << (32*3 + 16)
        return header.to_bytes(16, byteorder='little')

    
    def printBlockInfo(self):
        print( "-- SUBBLOCK #%02d: CL(%6d) L(%6d) U(%08X) F(%4d) T(%4d)" % \
            (self.id, self.compLength, \
            self.length, self.unknown, self.flags, \
            self.type ) )

# Data Class for SubBlocks within Blocks
class TextBlock:
    #TODO: Add data offset
    headerLen = 24
    def __init__(self, subblock):

        self.id = subblock.id
        self.parent = subblock

        self.header = subblock.data[:24]
        self.body = subblock.data # data is header + body

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
        self.d1len = 0
        self.d2len = 0
        self.d_var = [0,0,0,0,0,0]
        self.d1_pages = []

        # Decoded Outputs of the TextBlock
        self.hufftree = []
        self.encHuffTree = 0
        self.decText = {}

        self.parseHeader()
    
    def parseHeader(self):
        header = int.from_bytes(self.header,byteorder='little')
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
        self.d_entries = ( dheader & 0xFFFF )
        dheader = dheader >> 16

        # 5 vars come after
        for i in range(5):
            self.d_var[i] = ( dheader & 0xFFFF )
            dheader = dheader >> 16
    
    def printDHeader(self):
        print("-- -- -- D BLOCK O(%08X) D1(%08X) D2(%08X) DE[%04X] DV[%04X,%04X,%04X,%04X,%04X]" % ( \
            self.one, self.d1_off, self.d2_off, self.d_entries, \
            self.d_var[0],self.d_var[1],self.d_var[2],self.d_var[3],self.d_var[4]) )
        print( "D1 Length: %04X, D2 Length: %04X" % (self.d1len, self.d2len ))

    def parse( self ):
        # Calculate A, this will be the same as a_off if everything worked right :)
        self.a = byteRead( self.body, self.a_off, 2, decode=False )
        # This is the text itself, but huffman encoded
        self.encData = byteSlice( self.body, self.huff_c, self.huff_e, decode=False )
        # Not sure what these are, but they could be important
        self.e1 = byteRead( self.body, self.huff_e, 4 )
        self.e2 = byteRead( self.body, self.huff_e+4, 4 )
        self.e3 = byteRead( self.body, self.huff_e+8, 2 )
        
        # Occasionally d is zero, which means we need to set d to a
        self.d_a = None
        if self.huff_d == 0:
            self.huff_d = self.a_off
        else:
            # If we do have d, we can extract this range, not sure what it is though
            self.d_a = byteSlice( self.body, self.huff_d, self.a_off, decode=False )
            self.dheader = byteRead( self.body, self.huff_d, 28 )

            self.d1len = self.d2_off - self.d1_off
            self.d2len = self.a_off - self.d2_off

            self.parseDHeader( self.dheader )

            self.d1 = byteSlice( self.body, self.d1_off, self.d2_off, decode=False )
            self.d2 = byteSlice( self.body, self.d2_off, self.a_off, decode=False )

            '''if( self.d2_off - self.d1_off < 0x50 ):
                print("D1 Block")
                printHex( self.d1 )
                print("D2 Block")
                printHex( self.d2 )'''

            if self.d_var[2] > 0:
                idx = 0
                self.d1_offs = []
                for doff in range(self.d_entries):
                    o = int.from_bytes( self.d1[idx:idx+2], byteorder='little' )
                    self.d1_offs.append( o )
                    idx+=2

                idx = self.d1_offs[0]
                if idx == 0:
                    idx = 4
                self.d1_pages = []
                total_entries = 0
                page = []
                while True:
                    ent = self.d1[idx:idx+8]
                    if ent == bytearray(8):
                        if total_entries == self.d_var[2]:
                            self.d1_pages.append(page)
                            break
                        else:
                            self.d1_pages.append(page)
                            page = []
                            idx+=8
                            continue
                    dent = {
                        'offset': int.from_bytes(self.d1[idx:idx+4],byteorder='little'),
                        'value': decodeShiftJIS(int.from_bytes(self.d1[idx+4:idx+6],byteorder='little')),
                        'flag1': int.from_bytes(self.d1[idx+6:idx+7],byteorder='little'),
                        'flag2': int.from_bytes(self.d1[idx+7:idx+8],byteorder='little')
                    }
                    page.append( dent )
                    total_entries += 1
                    idx+=8
                for p in self.d1_pages:
                    last_o = -1
                    for e in p:
                        # Make sure pages have offsets that are strictly decreasing
                        if last_o != -1 and last_o < e['offset']:
                            raise("ENTRY NOT DECREASING")
                        
                        # Make sure offsets are always less than d2len*4
                        if e['offset'] > (self.d2len*4):
                            raise("D1 OFFSET TOO BIG")
                        
                        # Make sure value is always valid shift-jis
                        if e['value'] == '':
                            raise("D1 VALUE NOT VALID SHIFTJIS")

                        if e['flag1'] < 5 or e['flag2'] < 8:
                            print(e['flag1'])
                            print(e['flag2'])
                            raise("FLAG LESS THAN THRESH")
                        
                        if e['flag1'] > 13 or e['flag2'] > 14:
                            print(e['flag1'])
                            print(e['flag2'])
                            raise("FLAG GREATER THAN THRESH")

                        # This one is not true
                        # if e['flag1'] > e['flag2']:
                        #     print(e['flag1'])
                        #     print(e['flag2'])
                        #     raise("FLAG1 GREATER THAN FLAG2")
                        
                        last_o = e['offset']
        
        # Read to the end of the block
        self.end_counter = byteRead( self.body, self.a_off+4, 4 )
        self.end_block = byteRead( self.body, self.a_off+8, self.end_counter * 8, decode=False )
        
        # This is the actual huffman tree
        self.encHuffTree = byteSlice( self.body, self.huff_e+10, self.huff_d, decode=False )
        
        self.hufftree = makeHuffTree( self.encHuffTree )
        self.decText = decodeHuffman( self.huff_c, self.encData, self.hufftree )

        #print( "a:%02X, e's: [%04X,%04X,%02X], htlen:%04X, edlen:%04X" %
        #    (self.a[0], self.e1, self.e2, self.e3, len(self.encHuffTree), len(self.encData)) )
    
    def printDBlockPages(self):
        for p in self.d1_pages:
            print("==========NEW PAGE============")
            for e in p:
                print("%d\t%s\t%d\t%d" % (e['offset'],e['value'],e['flag1'],e['flag2']))

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

        #print("encText")
        #printHex(encText)
        #print("encTree")
        #printHex(encTree)

        ## Structure: ##
        # 1. Header (24 Bytes)
        # 2. Huffman Code (codeLen Bytes)
        codeLen = len(encText)
        # 3. E Section (10 Bytes)
        # 4. Huffman Tree (treeLen Bytes)
        treeLen = len(encTree)
        # 5. D Section Header (28 Bytes)
        # 6. D1 Block (d1Len Bytes)
        # 7. D2 Block (d2Len Bytes)
        dLen = (self.a_off - self.huff_d)
        # 8. Counter (4 bytes)
        # 9. Num End Blocks (4 bytes)
        # 10. Everything else (counter*8 bytes)

        if codeLen%4 != 0:
            raise("Huffman code length not a multiple of 4")

        # Create the array
        buffer = bytearray()

        #######################
        ## Create new header ##
        #######################

        # A Offset (4 bytes) = header + code + e + tree + d
        new_a_off = 24 + codeLen + 10 + treeLen + dLen
        buffer.extend( new_a_off.to_bytes( 4, 'little' ) )

        # Dialog ID (4 bytes)
        buffer.extend( self.uuid.to_bytes( 4, 'little' ) )

        # Huff C (4 bytes) (always 0x18)
        buffer.extend( self.huff_c.to_bytes( 4, 'little' ) )

        # Huff D (3 bytes) = A off - huff d
        new_huff_d = new_a_off - dLen
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
        buffer.extend( new_a_off.to_bytes(4,'little') )
        buffer.extend( self.end_counter.to_bytes(4,'little') )
        buffer.extend( self.end_block)

        self.parent.length = new_a_off + 8 + self.end_counter*8
        self.parent.compLength = self.parent.length

        return buffer

# Data Class for SubBlocks within Blocks
class ScriptBlock:
    def __init__(self, subblock):
        self.headerLen = 92
        self.parent = subblock

        self.raw = None
        self.header = None
        self.body = None

        # Header Info
        self.info = []
        
        # Body Script Tree
        self.script = []

        if self.parent.flags == 1280:
            self.raw = decompress( self.parent.data, self.parent.length )
        else:
            self.raw = self.parent.data

        self.opCodes = {
            'b401a0': {'name': '', 'raw': None, 'data': [], 'dataLen': [0]  },
            'b401a1': {'name': '', 'raw': None, 'data': [], 'dataLen': [0]  },
            'b501a3': {'name': '', 'raw': None, 'data': [], 'dataLen': [0]  },

            'c01678': {'name': '', 'raw': None, 'data': [], 'dataLen': [2]  },
            'c01639': {'name': '', 'raw': None, 'data': [], 'dataLen': [1]  }, # followed by a0
            'c0163b': {'name': '', 'raw': None, 'data': [], 'dataLen': [2]  }, # followed by a0
            'c0167b': {'name': '', 'raw': None, 'data': [], 'dataLen': [2,1]  }, # followed by a0
            'c021a0': {'name': '', 'raw': None, 'data': [], 'dataLen': [2,2] },
            'c021a1': {'name': '', 'raw': None, 'data': [], 'dataLen': [2,2] },
            'c021a2': {'name': '', 'raw': None, 'data': [], 'dataLen': [2,2] },
            'c021a3': {'name': '', 'raw': None, 'data': [], 'dataLen': [2,2] },
            'c02678': {'name': '', 'raw': None, 'data': [], 'dataLen': [1,1,1,2] },
            'c02639': {'name': '', 'raw': None, 'data': [], 'dataLen': [3] },
            'c0263b': {'name': '', 'raw': None, 'data': [], 'dataLen': [4,2] },
            'c0267b': {'name': '', 'raw': None, 'data': [], 'dataLen': [2,3,2] },
            'c026bb': {'name': '', 'raw': None, 'data': [], 'dataLen': [2,3,3] },
            'c061a0': {'name': '', 'raw': None, 'data': [], 'dataLen': [2] },
            'c061a2': {'name': '', 'raw': None, 'data': [], 'dataLen': [3] },            
            'c061a1': {'name': '', 'raw': None, 'data': [], 'dataLen': [2] }, # really not sure about this
            'c161a1': {'name': '', 'raw': None, 'data': [], 'dataLen': [3] },
            'c211a1': {'name': '', 'raw': None, 'data': [], 'dataLen': [1] }, # followed by a0
            'c21678': {'name': '', 'raw': None, 'data': [], 'dataLen': [1] }, # followed by a0
            'c221a1': {'name': '', 'raw': None, 'data': [], 'dataLen': [4] },
            'c2263b': {'name': '', 'raw': None, 'data': [], 'dataLen': [3,3] },
            'c22678': {'name': '', 'raw': None, 'data': [], 'dataLen': [2,3] },
            'c261a0': {'name': '', 'raw': None, 'data': [], 'dataLen': [2] },
            'c30db0': {'name': '', 'raw': None, 'data': [], 'dataLen': [1] },
            'c31678': {'name': '', 'raw': None, 'data': [], 'dataLen': [1] }, # followed by a0
            'c321a0': {'name': '', 'raw': None, 'data': [], 'dataLen': [2,2] },
            'c361a0': {'name': '', 'raw': None, 'data': [], 'dataLen': [2] },
            'c40639': {'name': '', 'raw': None, 'data': [], 'dataLen': [1] },
            'c4063b': {'name': '', 'raw': None, 'data': [], 'dataLen': [2] },
            'c40678': {'name': '', 'raw': None, 'data': [], 'dataLen': [1] },
            'c50678': {'name': '', 'raw': None, 'data': [], 'dataLen': [1] },
            'c611a0': {'name': '', 'raw': None, 'data': [], 'dataLen': [1] },
            'c661a0': {'name': '', 'raw': None, 'data': [], 'dataLen': [2] },
            'c711a0': {'name': '', 'raw': None, 'data': [], 'dataLen': [1] },
            'c821a0': {'name': '', 'raw': None, 'data': [], 'dataLen': [2,2] },
            'c921a0': {'name': '', 'raw': None, 'data': [], 'dataLen': [2,2] },

            'd021a0': {'name': '', 'raw': None, 'data': [], 'dataLen': [2,2] },
            'd02678': {'name': '', 'raw': None, 'data': [], 'dataLen': [2,3] },
            'd061a0': {'name': '', 'raw': None, 'data': [], 'dataLen': [2] },
            'd22678': {'name': '', 'raw': None, 'data': [], 'dataLen': [2,3] },

            'e0063d': {'name': '', 'raw': None, 'data': [], 'dataLen': [2] },
            'e01bc0': {'name': '', 'raw': None, 'data': [], 'dataLen': [9] }, # very weird one
            'e10300': {'name': '', 'raw': None, 'data': [], 'dataLen': [0] },
            'e10301': {'name': '', 'raw': None, 'data': [], 'dataLen': [0] },
            'e10302': {'name': '', 'raw': None, 'data': [], 'dataLen': [0] },
            'e10303': {'name': '', 'raw': None, 'data': [], 'dataLen': [0] },
            'e10304': {'name': '', 'raw': None, 'data': [], 'dataLen': [0] },
            'e10305': {'name': '', 'raw': None, 'data': [], 'dataLen': [0] },
            'e10306': {'name': '', 'raw': None, 'data': [], 'dataLen': [0] },
            'e20501': {'name': '', 'raw': None, 'data': [], 'dataLen': [1,2] },
            'e20502': {'name': '', 'raw': None, 'data': [], 'dataLen': [1,2] },
            'e20504': {'name': '', 'raw': None, 'data': [], 'dataLen': [1,2] },
            'e2050a': {'name': '', 'raw': None, 'data': [], 'dataLen': [1,2] },
            'e2050e': {'name': '', 'raw': None, 'data': [], 'dataLen': [1,2] },

            'f0063a': {'name': '', 'raw': None, 'data': [], 'dataLen': [2] },
            'f1063a': {'name': '', 'raw': None, 'data': [], 'dataLen': [2] },
            'f20639': {'name': '', 'raw': None, 'data': [], 'dataLen': [1] },
            'f20679': {'name': '', 'raw': None, 'data': [], 'dataLen': [2] },
            'f321a0': {'name': '', 'raw': None, 'data': [], 'dataLen': [4,2] },
            'f361a0': {'name': '', 'raw': None, 'data': [], 'dataLen': [2,2] },
            'f421a0': {'name': '', 'raw': None, 'data': [], 'dataLen': [4,2] },
            'f461a0': {'name': '', 'raw': None, 'data': [], 'dataLen': [2,2] },
            'f511a3': {'name': '', 'raw': None, 'data': [], 'dataLen': [2,1] },
            'f51678': {'name': '', 'raw': None, 'data': [], 'dataLen': [2,2] },
            'f521a0': {'name': '', 'raw': None, 'data': [], 'dataLen': [4,2] },
            'f561a0': {'name': '', 'raw': None, 'data': [], 'dataLen': [2,2] },
            'f711a3': {'name': '', 'raw': None, 'data': [], 'dataLen': [2,1] },
            'f71678': {'name': '', 'raw': None, 'data': [], 'dataLen': [2,2] },
            'f721a0': {'name': '', 'raw': None, 'data': [], 'dataLen': [4,2] },
            'f761a0': {'name': '', 'raw': None, 'data': [], 'dataLen': [2,2] },

#b206000000 88da93 ae0a00 88da93 ae8f49 97b90a 00 434343
#c0263b 0200 9005 0400 c0267b 0200 049405 0400 c021a0 9b05 0400
#b208000000 534e44 5f5341435f535f 5a41 5a41 0a00 434343
#b200000000 73636c 5f636d6d6e5f73616d706c655f3030 0a00

            # I don't think these commands are real
            '636e74': {'name': '', 'raw': None, 'data': [], 'dataLen': [3,2] },
            '88da93': {'name': '', 'raw': None, 'data': [], 'dataLen': [3] },
            '97b90a': {'name': '', 'raw': None, 'data': [], 'dataLen': [1] },

            # These seem more structural than anything else
            #'434343': {'name': '', 'raw': None, 'data': [], 'dataLen': [0] },
            #'585858': {'name': '', 'raw': None, 'data': [], 'dataLen': [0] },
        }

        self.keywords = {
            'b0':   {'name': '', 'raw': None, 'data': [], 'dataLen': [0] },
            'b1':   {'name': '', 'raw': None, 'data': [], 'dataLen': [4] }, # Technically 3 but I'll include the following 0x00
            'b2':   {'name': '', 'raw': None, 'data': [], 'dataLen': [4] }, # Technically 3 but I'll include the following 0x00
            'b3':   {'name': '', 'raw': None, 'data': [], 'dataLen': [5] }, # Similar story here
            # 'b4':   {'name': '', 'raw': None, 'data': [], 'dataLen': [0] },
            'b5':   {'name': '', 'raw': None, 'data': [], 'dataLen': [0] },
            'a0':   {'name': '', 'raw': None, 'data': [], 'dataLen': [0] },
            '01a0': {'name': '', 'raw': None, 'data': [], 'dataLen': [0] },
            '01a1': {'name': '', 'raw': None, 'data': [], 'dataLen': [0] },
            '01a4': {'name': '', 'raw': None, 'data': [], 'dataLen': [0] },
            '0000': {'name': '', 'raw': None, 'data': [], 'dataLen': [0] },
            '1000': {'name': '', 'raw': None, 'data': [], 'dataLen': [0] },
            '2000': {'name': '', 'raw': None, 'data': [], 'dataLen': [0] },
            '3000': {'name': '', 'raw': None, 'data': [], 'dataLen': [0] },
            'ffff': {'name': '', 'raw': None, 'data': [], 'dataLen': [0] },
            '43': {'name': '', 'raw': None, 'data': [], 'dataLen': [0] },
            '58': {'name': '', 'raw': None, 'data': [], 'dataLen': [0] },
            '00': {'name': '', 'raw': None, 'data': [], 'dataLen': [0] }
        }

        self.parseHeader( self.raw[:self.headerLen] )
        self.failed_comm = self.parseBody( self.raw[self.headerLen:] )
    
    def compress( self ):
        self.body = compress( self.raw, self.parent.compLength )
        return self.body
    
    def parseHeader(self, header):
        self.header = header # save the byte version
        data = [self.header[i:i+4] for i in range(0,len(self.header),4)]
        for raw in data:
            val = int.from_bytes(raw,byteorder='little')
            self.info.append(val)
    
    def printBlockInfo(self):
        print( "-- -- SCRIPTBLOCK ", end='')
        print( self.info )
    
    def replaceOffset(self, dialog, oldOff, newOff):
        # example c021a0 0e0d c006
        needle = bytearray([0xc0, 0x21, 0xa0,
                            oldOff&0xFF, (oldOff>>8)&0xFF,
                            (dialog<<4)&0xFF, (dialog>>4) ])
        new = bytearray([0xc0, 0x21, 0xa0,
                            newOff&0xFF, (newOff>>8)&0xFF,
                            (dialog<<4)&0xFF, (dialog>>4) ])
        if self.raw.find(needle) == -1:
            #print("Cannot find offset %04X for dialog %04X" % (oldOff, dialog))
            return False
        self.raw = self.raw.replace(needle,new)
        return True
            
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
        self.body = body

        buff = []

        # First two characters always 0x00
        #body = body[1:]

        fill = False
        filledBytes = 0
        entry = None

        offset = 0
        for x in body:
            #print(f'{x:02X}')

            # In this mode we scan for commands/keywords
            if not fill:
                buff.append(x)

                if len(buff) == 1 or len(buff) == 2:
                    found, kwd = self.checkKeyword(buff, self.keywords.keys())
                    if found:
                        #print( f"Found Keyword: {kwd}")
                        entry = self.keywords[kwd].copy()
                        entry['name'] = kwd
                        entry['data'] = []
                        entry['raw'] = bytearray(buff)
                        filledBytes = 0
                        if entry['dataLen'] == [0]:
                            self.script.append(entry)
                            #print(entry['name'])
                            fill = False
                        else:      
                            fill = True
                        buff = []
                    if len(buff) == 4 and not found:
                        buff = []
                if len(buff) == 3:
                    found, opc = self.checkKeyword(buff, self.opCodes.keys())
                    if found:
                        #print( f"Found OpCode: {opc}")
                        entry = self.opCodes[opc].copy()

                        # This is usually the end
                        # for now I'll just end things here
                        if opc == '585858':
                            return ''
                        
                        entry['name'] = opc
                        entry['data'] = []
                        entry['raw'] = bytearray(buff)
                        filledBytes = 0
                        if entry['dataLen'] == [0]:
                            self.script.append(entry)
                            #print(entry['name'])
                            fill = False
                        else:      
                            fill = True
                        buff = []
                    else:
                        if '0000' not in opc and '0100' not in opc and '0200' not in opc:
                            print( f"Invalid OpCode: {opc}", end='')
                            print( f" Following Bytes {body[offset-8:offset-2].hex()}",end=' ')
                            print( f"{body[offset-2:offset+1].hex()}",end=' ')
                            print( f"{body[offset+1:offset+24].hex()}")
                            return opc
                        return ''
                        buff = []
                if len(buff) > 3:
                    buff = []
                    print( f"Something went wrong: {buff}", end='')
                    return ''
            # Here we'll fill the data
            else:
                entry['raw'].append( x )
                filledBytes += 1

                # check to see if we've filled the raw data
                if filledBytes >= sum(entry['dataLen']):
                    idx = len(entry['name'])>>1
                    for i in entry['dataLen']:
                        entry['data'].append( entry['raw'][idx:idx+i] )
                        idx = idx+i
                    self.script.append(entry)
                    filledBytes = 0
                    fill = False
            offset += 1
        return ''
    
    def makeArgTable( self, command, init=None ):
        freqTable = []

        '''
        [ {'1FF':1,'17F':4}, {'0':100,...etc} ]
        '''

        if init == None:
            # create a dictionary for each argument
            for i in range(len(self.opCodes[command]['dataLen'])):
                freqTable.append({})
        else:
            freqTable=init

        for entry in self.script:
            if entry['name'] == command:
                for idx,e in enumerate(entry['data']):
                    arg = f"({int.from_bytes(e,byteorder='little'):X})"
                    if arg in freqTable[idx]:
                        freqTable[idx][arg] += 1
                    else:
                        freqTable[idx][arg] = 1
        return freqTable

    def printScript( self, quiet=False ):
        indentLevel = 0
        script = ''
        for entry in self.script:
            if entry['name'] == 'b2':
                indentLevel -= 2
            elif entry['name'] == 'b3':
                indentLevel -= 1
            for i in range(indentLevel):
                script += '\t'
            script += entry['name']
            for e in entry['data']:
                script += f"({int.from_bytes(e,byteorder='little'):X})"
            script += f" - {entry['raw'].hex()}\n"
            if entry['name'] == 'b1':
                indentLevel += 2
            elif entry['name'] == 'b3':
                indentLevel += 1
            entry = None
        
        # print unless specifically asked not to
        if not quiet:
            print(script)
        
        return script