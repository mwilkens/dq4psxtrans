import math
from libs.helpers import printHex

import lzss

def decompress( in_data, d_size ):
    data = lzss.decompress( in_data )
    return data[:d_size]

def compress( in_data, c_size ):
    data = lzss.compress( in_data )
    l = len(data)
    while l % 4 != 0:
        l += 1
    l = l - len(data)
    return data + bytes(l)