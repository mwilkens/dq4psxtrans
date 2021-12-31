from libs.parsing import *
from libs.helpers import *
from libs.blockDefs import *
import io

select = 26045#462

if __name__ == '__main__':
    for b in parseHBD1('HBD1PS1D.Q41'):
        for sb in parseBlock(b):
            if b.id == select and sb.type == 39:
                b.printBlockInfo()
                sb.printBlockInfo()
                scb = ScriptBlock(sb)
                oldraw = scb.raw
                #scb.replaceOffset( 0x6C, 0xF91, 0xF87 )
                old = sb.data
                comp = scb.compress()
                compHex( old, comp )