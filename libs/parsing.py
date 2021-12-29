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
def parseHBD1(filename):
    with open(filename, "rb") as dq4b:
        # Nothing useful to us in the first sector
        dq4b.seek(0x800)

        # 319,436,800 total bytes
        while dq4b:
            b = Block()
            b.parseHeader(dq4b.read(16))

            if b.numSubBlocks > 1000 or b.zeroBytes != 0:
                dq4b.read(2048-16)
                continue
            
            if b.length == 0:
                break

            dataLeft = 2048 * b.sectors - 16
            b.data = dq4b.read(dataLeft)

            yield b

def parseBlock(block):
    dataOffset = block.numSubBlocks*16
    lengths = []
    for i in range(block.numSubBlocks):
        sb = SubBlock(i+1) # no need to zero-index this
        sb.parseHeader( block.data[(i*16):((i+1)*16)] )
        off = dataOffset+sum(lengths)
        sb.data = block.data[off:off+sb.compLength]
        lengths.append(sb.compLength)
        yield sb