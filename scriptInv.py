from libs.parsing import *
from libs.helpers import *
from libs.blockDefs import *
import io
import numpy as np

select = 462

#select = 1128
select = 26046

dmax = 0
dmaxid = None
totalDiff = 0
totalNum = 0

if __name__ == '__main__':
    for b in parseHBD1('HBD1PS1D.Q41'):
        for sb in parseBlock(b):
            if sb.type == 39:
                #b.printBlockInfo()
                #sb.printBlockInfo()
                scb = ScriptBlock(sb)
                if sb.flags == 1280:
                    oldraw = scb.raw
                    #with open("%d.bin"%select, 'wb') as fh:
                    #    fh.write(scb.raw)
                    #scb.replaceOffset( 0x6C, 0xF91, 0xF87 )
                    old = sb.data
                    comp = scb.compress()
                    #compHex( old, comp )
                    print( f"Old Len: {len(old)}\tNew Len: {len(comp)}")
