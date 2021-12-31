from libs.parsing import *
from libs.helpers import *
from libs.blockDefs import *
import io

#select = 462

select = 1128
select = 26046
#select = 1197
#select = 465

smax = 0
smaxid = None
smin = 9999
sminid = None

if __name__ == '__main__':
    for b in parseHBD1('HBD1PS1D.Q41'):
        for sb in parseBlock(b):
            if b.id == select and sb.type == 39:
                b.printBlockInfo()
                sb.printBlockInfo()
                scb = ScriptBlock(sb)
                oldraw = scb.raw
                with open("%d.bin"%select, 'wb') as fh:
                    fh.write(scb.raw)
                #scb.replaceOffset( 0x6C, 0xF91, 0xF87 )
                old = sb.data
                comp = scb.compress()
                compHex( old, comp )
                printHex( oldraw )
                #compHex( oldraw, scb.raw )
            if sb.type == 39:
                if sb.compLength > smax:
                    smax = sb.compLength
                    smaxid = b.id
                if sb.compLength < smin:
                    smin = sb.compLength
                    sminid = b.id

    print(f"Max@{smaxid}={smax} - Min@{sminid}={smin}")