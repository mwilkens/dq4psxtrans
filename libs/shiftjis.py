import io

ShiftJISLookup = {}

asciiMap = {
  ' ':0x8140,
  '{':0x816f,
  '}':0x8170,
  '.':0x8142,
  '\'':0x8166,
  '?':0x8148,
  '!':0x8149
}

def mapASCII( char ):
  # Uppercase Letters
  if( ord(char) >= 0x41 and ord(char) <= 0x5A ):
    char = ord(char) + 0x60 - 0x41 + 0x8200
    return decodeShiftJIS( char )
  # Lowercase Letters
  elif( ord(char) >= 0x61 and ord(char) <= 0x7A ):
    char = ord(char) + 0x81 - 0x61 + 0x8200
    return decodeShiftJIS( char )
  # Decimals
  elif( ord(char) >= 0x30 and ord(char) <= 0x39 ):
    char = ord(char) + 0x4f - 0x30 + 0x8200
    return decodeShiftJIS( char )
  # Map
  elif char in asciiMap:
    return decodeShiftJIS( asciiMap[char] )


def decodeShiftJIS( sjis ):
  return sjis.to_bytes(2,byteorder='big',signed=False).decode('cp932')

def encodeShiftJIS( ascii ):
  return mapASCII( ascii )