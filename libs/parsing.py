from libs.blockDefs import *

'''
Example:

if __name__ == '__main__':
    for b in parseHBD1('HBD1PS1D.Q41'):
        b.printBlockInfo()
        for sb in parseBlock(b):
            sb.printBlockInfo()
            if sb.type == 40 or sb.type == 42:
                tb = TextBlock(sb)
                tb.printBlockInfo()
            elif sb.type == 39:
                scb = ScriptBlock(sb)
                scb.printBlockInfo()
'''


# Generators for Parsing Blocks
def parseHBD1(filename, yield_invalid=False):
    with open(filename, "rb") as dq4b:
        # Nothing useful to us in the first sector
        if yield_invalid:
            b = Block(0)
            b.valid = False
            b.parseHeader(dq4b.read(16))
            b.data = dq4b.read(2048-16)
            yield b
        else:
            dq4b.seek(0x800)

        # 319,436,800 total bytes
        blockid = 1
        while dq4b:
            b = Block(blockid)
            b.parseHeader(dq4b.read(16))
            b.offset = dq4b.tell()-16

            if b.numSubBlocks > 1000 or b.zeroBytes != 0:
                b.data = dq4b.read(2048-16)
                b.valid = False
                blockid += 1
                if yield_invalid:
                    yield b
                continue
            
            if b.length == 0:
                b.data = dq4b.read()
                b.valid = False
                blockid += 1
                if yield_invalid:
                    yield b
                break

            dataLeft = 2048 * b.sectors - 16
            b.data = dq4b.read(dataLeft)

            blockid += 1
            yield b

def parseBlock(block):
    dataOffset = block.numSubBlocks*16
    lengths = []
    for i in range(block.numSubBlocks):
        sb = SubBlock(i+1) # no need to zero-index this
        sb.parseHeader( block.data[(i*16):((i+1)*16)] )
        off = dataOffset+sum(lengths)
        sb.offset = off + block.offset
        sb.data = block.data[off:off+sb.compLength]
        lengths.append(sb.compLength)
        yield sb