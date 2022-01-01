# Script for Working With DQ4 Data
from libs.blockDefs import *
from libs.parsing import *
from autoTranslator import getTranslation
import io

if __name__ == '__main__':
    for b in parseHBD1('HBD1PS1D.Q41'):
        for sb in parseBlock(b):
            if sb.type == 40 or sb.type == 42:
                tb = TextBlock(sb)
                tb.printBlockInfo()
                tb.parse()
                validDialog = False
                for line in tb.decText:
                    if "ダミー{7f0b}{0000}" in line["text"] or line["text"] == "{0000}":
                        ''' bad sign if dialog is only these '''
                    else:
                        validDialog = True
                
                if validDialog:
                    with io.open( './jdialog/%04X.csv' % tb.uuid, mode="w", encoding="utf-8") as dcsv:
                        for line in tb.decText:
                            dcsv.write( "|" + "|".join(line.values()) + "\n")
                
                # There are certain text blocks repeated over the coarse of the
                # resource file. If you want to extract these individually
                # you can uncomment this code, its not particularly interesting though
                '''
                if validDialog and tb.uuid in [0x20,0x21,0x22,0x23,0x24,0x25,0x26]:
                    with io.open( './2X/%d-%d-%04X.csv' % (b.id, sb.id, tb.uuid), mode="w", encoding="utf-8") as dcsv:
                        for line in tb.decText:
                            dcsv.write( "\"\"," + ",".join(line.values()) + "\n")
                '''