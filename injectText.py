# Script for Working With DQ4 Data
from libs.blockDefs import *
from libs.parsing import *
import io

if __name__ == '__main__':
    for b in parseHBD1('HBD1PS1D.Q41'):
        for sb in parseBlock(b):
            if sb.type == 40 or sb.type == 42:
                tb = TextBlock(sb)
                tb.parse()
                validDialog = False
                for line in tb.decText:
                    if "ダミー{7f0b}{0000}" in line["text"] or line["text"] == "{0000}":
                        ''' bad sign if dialog is only these '''
                    else:
                        validDialog = True

                if validDialog:
                    with io.open( './jdialog/%04X.csv' % tb.uuid, mode="r", encoding="utf-8") as dcsv:
                        tdialog = [getTranslation(line) for line in dcsv]
                        buffer = tb.encodeTranslation( ''.join(tdialog) )
            if sb.type == 39:
                scb = ScriptBlock(sb)
                ''' not entirely sure what to do here yet '''