from libs.parsing import *
from libs.helpers import *
from libs.blockDefs import *
import io

select = None

# script blocks
# 39, 31

dialogID = 0x65

if __name__ == '__main__':
    for b in parseHBD1('HBD1PS1D.Q41'):
        subblocks = []
        offsets = []
        for sb in parseBlock(b):
            if (sb.type == 40 or sb.type == 42):
                tb = TextBlock(sb)
                if tb.uuid == dialogID:
                    select = b.id
                    tb.parse()
                    for i in range(len(tb.decText)):
                        offsets.append( int( tb.decText[i]['offset'], 16 ) )

            subblocks.append(sb)
        
        if b.id == select:
            b.printBlockInfo()
            for sb in subblocks:
                if (sb.type == 39):
                    sb.printBlockInfo()
                    scb = ScriptBlock(sb)
                    total = len(offsets)
                    good = 0
                    for o in offsets:
                        if scb.replaceOffset(dialogID, o, 0x00):
                            good += 1
                    print(f"Found {good} out of {total} offsets")