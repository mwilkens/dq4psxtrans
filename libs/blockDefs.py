from itertools import count
from libs.huffman import *
from libs.helpers import *
from libs.lzs import decompress, compress

# Data Class for 2048 byte blocks
class Block:
    #TODO: Add data offset
    headerLen = 16
    _ids = count(0)
    def __init__(self, sb=0, s=0, l=0, zb=0):
        self.id = next(self._ids)
        self.valid = True
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
        self.d_var = [0,0,0,0,0,0]

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
        # 6 vars come after
        for i in range(6):
            self.d_var[i] = ( dheader & 0xFFFF )
            dheader = dheader >> 16
    
    def printDHeader(self):
        print("-- -- -- D BLOCK O(%08X) D1(%08X) D2(%08X) DV[%04X,%04X,%04X,%04X,%04X,%04X]" % ( \
            self.one, self.d1_off, self.d2_off, \
            self.d_var[0],self.d_var[1],self.d_var[2],self.d_var[3],self.d_var[4],self.d_var[5]) )
        print( "D1 Length: %04X, D2 Length: %04X" % (self.d2_off - self.d1_off, self.a_off - self.d2_off ))

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
            self.parseDHeader( self.dheader )
            #self.printDHeader()

            self.d1 = byteSlice( self.body, self.d1_off, self.d2_off, decode=False )
            self.d2 = byteSlice( self.body, self.d2_off, self.a_off, decode=False )

            '''if( self.d2_off - self.d1_off < 0x50 ):
                print("D1 Block")
                printHex( self.d1 )
                print("D2 Block")
                printHex( self.d2 )'''
        
        # Read to the end of the block
        self.end_counter = byteRead( self.body, self.a_off+4, 4 )
        self.end_block = byteRead( self.body, self.a_off+8, self.end_counter * 8, decode=False )
        
        # This is the actual huffman tree
        self.encHuffTree = byteSlice( self.body, self.huff_e+10, self.huff_d, decode=False )
        
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

            'c01678': {'name': '', 'raw': None, 'data': [], 'dataLen': [1]  },
            'c01639': {'name': '', 'raw': None, 'data': [], 'dataLen': [1]  }, # followed by a0
            'c0163b': {'name': '', 'raw': None, 'data': [], 'dataLen': [2]  }, # followed by a0
            'c0167b': {'name': '', 'raw': None, 'data': [], 'dataLen': [2,1]  }, # followed by a0
            'c021a0': {'name': '', 'raw': None, 'data': [], 'dataLen': [2,2] },
            'c021a3': {'name': '', 'raw': None, 'data': [], 'dataLen': [2,2] },
            'c02678': {'name': '', 'raw': None, 'data': [], 'dataLen': [1,1,1,2] },
            'c02639': {'name': '', 'raw': None, 'data': [], 'dataLen': [3] },
            'c0263b': {'name': '', 'raw': None, 'data': [], 'dataLen': [4] },
            'c0267b': {'name': '', 'raw': None, 'data': [], 'dataLen': [2,2,3] },
            'c026bb': {'name': '', 'raw': None, 'data': [], 'dataLen': [2,3,3] },
            'c061a0': {'name': '', 'raw': None, 'data': [], 'dataLen': [2] },
            'c061a1': {'name': '', 'raw': None, 'data': [], 'dataLen': [2] }, # really not sure about this
            'c161a1': {'name': '', 'raw': None, 'data': [], 'dataLen': [3] },
            'c211a1': {'name': '', 'raw': None, 'data': [], 'dataLen': [1] }, # followed by a0
            'c21678': {'name': '', 'raw': None, 'data': [], 'dataLen': [1] }, # followed by a0
            'c221a1': {'name': '', 'raw': None, 'data': [], 'dataLen': [4] },
            'c22678': {'name': '', 'raw': None, 'data': [], 'dataLen': [2,3] },
            'c261a0': {'name': '', 'raw': None, 'data': [], 'dataLen': [2] },
            'c30db0': {'name': '', 'raw': None, 'data': [], 'dataLen': [1] },
            'c31678': {'name': '', 'raw': None, 'data': [], 'dataLen': [1] }, # followed by a0
            'c321a0': {'name': '', 'raw': None, 'data': [], 'dataLen': [4,4,2,1] },
            'c361a0': {'name': '', 'raw': None, 'data': [], 'dataLen': [2] },
            'c40678': {'name': '', 'raw': None, 'data': [], 'dataLen': [1] },
            'c611a0': {'name': '', 'raw': None, 'data': [], 'dataLen': [1] },
            'c661a0': {'name': '', 'raw': None, 'data': [], 'dataLen': [2] },
            'c821a0': {'name': '', 'raw': None, 'data': [], 'dataLen': [2,2] },
            'c921a0': {'name': '', 'raw': None, 'data': [], 'dataLen': [2,2] },

            'd021a0': {'name': '', 'raw': None, 'data': [], 'dataLen': [2,2] },

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

            'f1063a': {'name': '', 'raw': None, 'data': [], 'dataLen': [2] },
            'f321a0': {'name': '', 'raw': None, 'data': [], 'dataLen': [4,2] },
            'f421a0': {'name': '', 'raw': None, 'data': [], 'dataLen': [4,2] },
            'f461a0': {'name': '', 'raw': None, 'data': [], 'dataLen': [2,2] },
            'f511a3': {'name': '', 'raw': None, 'data': [], 'dataLen': [4,2] },
            'f521a0': {'name': '', 'raw': None, 'data': [], 'dataLen': [4,2] },
            'f561a0': {'name': '', 'raw': None, 'data': [], 'dataLen': [2,2] },
            'f711a3': {'name': '', 'raw': None, 'data': [], 'dataLen': [4,2] },
            'f721a0': {'name': '', 'raw': None, 'data': [], 'dataLen': [4,2] },
            'f761a0': {'name': '', 'raw': None, 'data': [], 'dataLen': [2,2] },

            '434343': {'name': '', 'raw': None, 'data': [], 'dataLen': [0] },
            '585858': {'name': '', 'raw': None, 'data': [], 'dataLen': [0] },
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
            '00': {'name': '', 'raw': None, 'data': [], 'dataLen': [0] }
        }

        self.parseHeader( self.raw[:self.headerLen] )
        self.parseBody( self.raw[self.headerLen:] )
    
    def compress( self ):
        self.parent.length = len(self.raw)
        comp = compress( self.raw )
        self.parent.compLength = len(comp)
        self.parent.data = comp
        return comp
    
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
                            oldOff&0xFF, oldOff>>8,
                            (dialog<<4)&0xFF, (dialog>>4) ])
        new = bytearray([0xc0, 0x21, 0xa0,
                            newOff&0xFF, newOff>>8,
                            (dialog<<4)&0xFF, (dialog>>4) ])
        
        self.raw = self.raw.replace(needle,new)
            
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
                        #if opc == '585858':
                        #    return
                        
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
                        #print( f"Invalid OpCode: {opc}", end='')
                        #print( f" Following Bytes {body[offset-18:offset+18].hex()}")
                        return
                        buff = []
                if len(buff) > 3:
                    buff = []
                    print( f"Something went wrong: {buff}", end='')
                    return
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

    def printScript( self ):
        indentLevel = 0
        for entry in self.script:
            if entry['name'] == 'b2':
                indentLevel -= 2
            elif entry['name'] == 'b3':
                indentLevel -= 1
            for i in range(indentLevel):
                print('\t',end='')
            print(entry['name'], end='')
            for e in entry['data']:
                print( f" ({int.from_bytes(e,byteorder='little'):X})", end='' )
            print(f" - {entry['raw'].hex()}")
            if entry['name'] == 'b1':
                indentLevel += 2
            elif entry['name'] == 'b3':
                indentLevel += 1
            entry = None
