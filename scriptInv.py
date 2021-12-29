from libs.parsing import *
from libs.helpers import *
from libs.blockDefs import *
import io

select = 374#1127

if __name__ == '__main__':
    for b in parseHBD1('HBD1PS1D.Q41'):
        for sb in parseBlock(b):
            if b.id == select and sb.type == 39:
                b.printBlockInfo()
                sb.printBlockInfo()
                scb = ScriptBlock(sb)
                printHex( scb.raw )
                comp = scb.compress( sb )
                compHex( sb.data, comp )