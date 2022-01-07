from libs.parsing import *
from libs.helpers import *
from libs.blockDefs import *
import os
import io

if __name__ == '__main__':
    os.makedirs('./hbd1ps1dq1', exist_ok=True)
    os.makedirs('./scripts', exist_ok=True)
    for b in parseHBD1('HBD1PS1D.Q41'):

        # blocks with one subblock are my enemy
        count = 0
        for sb in parseBlock(b):
            count += 1
        if count == 0:
            continue

        os.makedirs('./hbd1ps1dq1/%d' % b.id, exist_ok=True)
        for sb in parseBlock(b):
            # Default to binary filetype
            filetype = 'bin'

            if sb.type == 8 or sb.type == 10:
                filetype = 'tim'
            
            if sb.type in [20,21,22,24]:
                filetype = 'qQES'
            
            if sb.type in [31,39,40,42]:
                filetype = 'txt'

            with io.open('./hbd1ps1dq1/%d/%d-%d.%s' % (b.id,sb.id,sb.type,filetype), 'wb') as fh:
                if sb.type == 39 or sb.type == 31:
                    scb = ScriptBlock(sb)
                    script = bytes( scb.printScript(quiet=True), encoding='utf-8')
                    fh.write(script)
                elif sb.type == 40 or sb.type == 42:
                    tb = TextBlock(sb)
                    tb.parse()
                    for line in tb.decText:
                        fh.write( bytes(line['text'] + '\n','utf-8') )
                else:
                    if sb.flags == 1280:
                        sb.data = decompress( sb.data, sb.length )
                    fh.write(sb.data)
            
            # save tims to a diff directory
            if sb.type == 39 or sb.type == 31:
                with io.open('./scripts/%d-%d-%d.%s' % (b.id,sb.id,sb.type,filetype), 'wb') as fh:
                    scb = ScriptBlock(sb)
                    script = bytes( scb.printScript(quiet=True), encoding='utf-8')
                    fh.write(script)