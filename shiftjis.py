import io

ShiftJISLookup = {}

def loadShiftJIS( file ):
  with io.open(file, mode="r", encoding="utf-8") as sjis_fh:
    for line in sjis_fh:
      line = line.split(' ')
      base = line[0]
      offset = line[1]
      lookup = [x.strip('\n') for x in line[3:]]
      if lookup[0:3] == ['','','']:
        lookup = lookup[2:]
      if base not in ShiftJISLookup:
        ShiftJISLookup[base] = {}
      ShiftJISLookup[base][offset] = lookup

def decodeShiftJIS( sjis ):
    if ShiftJISLookup == {}:
      loadShiftJIS( 'kanji_codes.sjis.txt' )
    byte = sjis & 0xFF
    base = "%x" % ((sjis & 0xFF00) >> 8)
    if base in ShiftJISLookup:
        for offset in ShiftJISLookup[base]:
          i_off = int(offset, 16)
          if byte >= i_off:
            prevOffset = offset
        # No more offsets to parse
        i_off = int( prevOffset, 16 )
        if( byte-i_off < len(ShiftJISLookup[base][prevOffset])):
          return ShiftJISLookup[base][prevOffset][byte - i_off]
    print( "Ignored Byte: %s%02x" % (base,byte))
    return ''