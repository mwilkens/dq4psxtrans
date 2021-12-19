# D Section - Probably not useful!!

The D section is very interesting. First of all, it only exists when the "one" value of the text block header is 1, otherwise there's no d-block. The begining of the D section is a header that's 28 bytes long. 

| Start | Length | Comment |
| ----- | ------ | ------- |
| 0x00 | 8 | Always 0x01 |
| 0x04 | 8 | Offset for first data section, we'll call it "d1" |
| 0x08 | 8 | Offset for second data section, we'll call it "d2" |
| 0x0C | 4 | Number of 2-byte ints read in beginning of d1 |
| 0x0E | 4 | Always 0x02 |
| 0x10 | 4 | Always 0x02 |
| 0x12 | 4 | Roughly the number of "entries" of d1 |
| 0x14 | 4 | Always 0x10 |
| 0x16 | 4 | Always 0x10 |

The first data section (D1 Block) looks very structured. Every bit in the 0x07, 0x08, 0x0E and 0x0F position is zero. It nearly always ends in 8 bytes of padding. Using the 4th value of the d section header, we can read a list of offsets which gradually increase. The first offset is where the data starts, and if we account for the 16 bytes of termination, we can count the number of 8-byte (or 32-bit) entries which have a similar structure. The 7th entry of the d section header is exactly the number of entries if the 4th value is 2. It is slightly less otherwise. The offsets always correspond to an area of all 0's in the section.

The D1 block can be parsed partially by reading the starting offsets one by one and extracting the data in each block. Each subblock of the D1 block is further seperated into "entries" which contain a 4-byte integer and a 4-byte chunk of data. Each subblock is padded with 8-bytes of zeros. The 4-byte integers of each entry gradually decends until it finally reaches zero. The other bit of information is interesting and likely represents some kind of instruction. A large chunk of them begin with 0x0D0C. It is possible that the 4-byte integers represent bit level offsets in the D2 block, however since the sections of D1 have counters that start over, I have reason to suspect that.

The second section (D2 Block) is fairly random. Consistently there seem to be a lot of occurances of 0x55, but that could be coincidence.

The "dummy" (ダミー) blocks have d sections that are just zero'd out stubs and don't follow either of the above rules.

## Example
```Text Block Hex Offset 0x004D6020
Dialog #3CE:
a = 0x0390
c = 0x0018
e = 0x00BC
d = 0x01FC
e's = [00C6,0160,4C]
Huffman Tree Length = 0x0136
Encoded Data Length = 0x00A4
D HEADER:
O  = 0x0001
D1 = 0x0218
D2 = 0x0264
D Vals = [02,02,02,08,10,10]

== D1 Block ==
0x0000 | 04 00 00 00 17 04 00 00 | CA 97 0C 0D 74 03 00 00 |
0x0010 | 68 96 0C 0D DC 02 00 00 | 84 94 0C 0D 4D 02 00 00 |
0x0020 | 58 93 0C 0D BC 01 00 00 | 84 8E 0C 0D 30 01 00 00 |
0x0030 | 64 8F 0C 0D A4 00 00 00 | EC 8D 0C 0D 00 00 00 00 |
0x0040 | E4 8C 0C 0D 00 00 00 00 | 00 00 00 00
== D2 Block ==
0x0000 | 14 C4 AC 50 55 C1 C1 F5 | 1D 74 DF D0 0D 0A 55 DD |
0x0010 | 45 F7 DD D0 54 D0 0D 1D | F4 DD D0 DD 90 0D DD 59 |
0x0020 | 4F 5D 79 63 C3 0F CD 33 | 4D 14 C6 D8 A0 33 E8 50 |
0x0030 | 55 14 AC D0 BF 0D C1 8D | 39 0D 55 D4 DC 3F 34 37 |
0x0040 | 37 57 51 73 FF D0 DC DC | DC 0C 33 8C 4C C6 64 E5 |
0x0050 | 63 55 55 85 6A EA 4F 7D | 1F 43 55 35 F7 7D 73 55 |
0x0060 | 35 C3 F7 CF 55 15 D3 F7 | 4F 55 55 15 FD FF FF 58 |
0x0070 | 8C D5 0F 31 DC D8 0C 8D | 8D 55 51 F3 FD 3A 57 14 |
0x0080 | 8C 9A 41 73 D0 EB 10 DE | 10 0C 8D AD 97 62 57 F0 |
0x0090 | 8D C3 8F 33 C5 54 55 55 | D4 FF FF 43 63 4C 8D 55 |
0x00A0 | D8 D8 3F 35 36 43 57 55 | D8 FD DF D4 CD 0D 7A 73 |
0x00B0 | 43 5F 55 4D D3 FF 0F 0C | 31 56 55 85 FF FD 8F 55 |
0x00C0 | 15 D3 FF 4F 55 55 15 F4 | F0 F0 37 0C 51 3C 46 31 | 
0x00D0 | EA D0 0C 06 43 53 90 30 | 59 C1 F0 FC 0F 55 18 F7 |
0x00E0 | 4D 71 AB 55 05 DD 70 FF | 77 53 8F AD 54 15 34 34 |
0x00F0 | F4 77 43 43 53 B7 AE D8 | 1D 1C 4C DD 70 30 E9 0D |
0x0100 | C1 54 30 4C F3 03 55 55 | 0C FD DF 5C 55 CD FD DF |
0x0110 | 54 55 55 D1 AA EA 4F 7D | DF 5C 55 CD 7D DF 5C 55 |
0x0120 | CD F0 FD 53 55 55 45 FF | FF 3F 00 00
```