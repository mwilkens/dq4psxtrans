from libs.parsing import *
from libs.helpers import *
from libs.blockDefs import *
import io

select = None

# script blocks
# 39, 31

dialogID = 0x0392

if __name__ == '__main__':
    for b in parseHBD1('HBD1PS1D.Q41'):
        for sb in parseBlock(b):
        
            if (sb.type == 39):
                #sb.printBlockInfo()
                scb = ScriptBlock(sb)
                good = 0
                fffo = 0
                for l in scb.script:
                    if l['name'] == 'c021a0' and l['data'][1] == b' 9':
                        print(f"Found {dialogID:04X} in script {b.id}/{sb.id} RAW {l['raw'].hex()}")
                    if l['name'] == 'c021a0' and l['data'][1] == b'\xf0\xff':
                        print(f"Found {dialogID:04X} in script {b.id}/{sb.id} RAW {l['raw'].hex()}")