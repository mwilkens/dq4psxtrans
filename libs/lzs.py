import math
from libs.helpers import printHex

import lzss

def decompress( in_data, d_size ):
    return lzss.decompress( in_data )

def compress( in_data ):
    return lzss.compress( in_data )