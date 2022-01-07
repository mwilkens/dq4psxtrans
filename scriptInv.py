from libs.parsing import *
from libs.helpers import *
from libs.blockDefs import *
import io

select = 117

# script blocks
# 39, 31

if __name__ == '__main__':
    for b in parseHBD1('HBD1PS1D.Q41'):
        b.printBlockInfo()
        for sb in parseBlock(b):
            if (sb.type == 40):
                tb = TextBlock(sb)
                tb.printBlockInfo()
            if ('''sb.type == 39 or sb.type == 31 or ''' == True or sb.type == 44):
                sb.printBlockInfo()
                scb = ScriptBlock(sb)
                
                #for line in scb.script:
                #    if line['name'] == 'c021a0' and line['data'][1] != bytearray(2):
                #        print(line['raw'].hex())