def byteRead( data, offset, length, decode=True ):
    rData = data[ offset : offset + length ]
    if( decode ):
        return int.from_bytes( rData, byteorder='little')
    else:
        return rData

def byteSlice( data, start, end, decode=True ):
    rData = data[ start : end ]
    if( decode ):
        return int.from_bytes( rData, byteorder='little')
    else:
        return rData

def printHex( hex ):
    idx = 0
    print( "0x0000 | ", end='')
    for v in list(hex):
        print( "%02X " % v, end='')
        idx+=1
        if( idx%8==0 ):
            print("| ", end='')
        if( idx%16==0 ):
            print("\n0x%04X | " % idx, end='')
    print('')

def writeHex( fh, hex ):
    idx = 0
    fh.write( "0x0000 | ")
    for v in list(hex):
        fh.write( "%02X " % v)
        idx+=1
        if( idx%8==0 ):
            fh.write("| ")
        if( idx%16==0 ):
            fh.write("\n0x%04X | " % idx)
    fh.write('\n')

ccMap = {
    '{0000}': '{END}',
    '{7f02}': '\n',
    '{7f04}': '', # This is italics, probably not worth rendering
    '{7f0a}': '',
    '{7f0b}': '',
    '{7f0c}': '',
    '{7f15}': '{GOLD}',
    '{7f1a}': 'ルーシア',
    '{7f1f}': '{HERO}',
    '{7f20}': 'ライアン',
    '{7f21}': 'アリーナ', # Alena 
    '{7f23}': 'ブライ',  # Brey / Borya
    '{7f22}': 'クリフト', # Cristo / Kiryl
    '{7f23}': 'ブライ',
    '{7f24}': 'トルネコ',
    '{7f25}': 'ミネア',
    '{7f26}': 'マーニャ',
    '{7f28}': 'スコット',
    '{7f29}': 'アレクス',
    '{7f2a}': 'フレア',
    '{7f2b}': 'ホイミン',
    '{7f2c}': 'オーリン',
    '{7f2d}': 'ホフマン',
    '{7f2e}': 'パノン',
    '{7f2f}': 'ルーシア',
    '{7f31}': 'ピサロ', # Saro
    '{7f32}': 'ロザリー',
    '{7f34}': '{NAME}',
    '{7f42}': '{TOWN}'
}

def humanReadableCC( text ):
    for cc in ccMap:
        text = text.replace(cc,ccMap[cc])
    return text