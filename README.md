# Dragon Quest 4 PSX Translation
Attempt at Python tooling for the Dragon Quest 4 PSX Translation

My goal here is to get at least an accessible foundation for translation started. I'm fairly new to rom hacking but I'm comfortable with reverse engineering so this should be a fun project :)

## Progess:

* [DONE] Parse Data File Blocks
* [DONE] Parse Data File SubBlocks
* [DONE] Parse Text SubBlocks
* [DONE] Extract Text Huffman Coding Data
* [DONE] Decode Huffman Encoded Text
* [DONE] Extract Japanese Script from File
* [DONE] Convert Android English Text to Correct Format
* [WIP] Create script that guesses translation based on text similarity
* [DONE] Write Huffman Encode Functionality
* [WIP] Write Textblock Modification Functionality
* ~~Calculate Pointer Mod Values~~
* ~~[WIP] Write ASM Generator for Pointer Redirection~~
* ~~Write Binary Patcher for SLPM_869.16~~
* Figure out DQ scripting language structure
* Actually patch all the dialog in DQ4 :)
* [DONE] Write DQ LZS Decompression
* Write DQ LZS Compression
* Extract all TIM Files
* Write Patcher for TIM Files
* Figure out where every other bit of dialog is
* ... TBD
* Make a cute intro

## DQ4 PSX Quirks

* Dialog has different pitches per character speaking.

## Auto Translation

The auto-translator works really well. As can be seen below, the dialog is matched near perfectly for the most part. The big issue is the English dialog is not formatted the same way as the Japanese dialog which is incredibly annoying.

```
Line:
{7f04}{7f25}「夢というのは　人の思いが{7f02}眠っている人の意識に{7f02}入りこんでくるものだと言います。{7f0a}{7f02}{7f04}{7f25}「そのおかしな夢というのも{7f02}もしかして　だれかの強い思いが{7f02}影響してるのかもしれませんね。{0000}        
Matched Line:
{7f04}{7f25}「夢というのは　人の思いが{7f02}眠っている人の意識に{7f02}入りこんでくるものだと言います。{7f0a}{7f02}{7f04}{7f25}「そのおかしな夢というのも{7f02}もしかして　だれかの強い思いが{7f02}影響してるのかもしれませんね。
Translated from b0532000.mpt (Confidence: 99.60%):
In dreams, the ideas and thoughts of others are entering the consciousness of those sleeping.{7f0a}{7f02}If people are 
having strange dreams, it may mean some powerful force is casting a shadow over their hearts...{0000}
+====================================+

Line:
{7f04}{7f24}「私　夢って{7f02}あんまり　見ないんですよ。{7f02}眠りが　深いのでしょうかな？{0000}
Matched Line:
{7f04}{7f24}「私　夢って　{7f02}あんまり　見ないんですよ。{7f02}眠りが　深いのでしょうかな？
Translated from b0532000.mpt (Confidence: 98.25%):
I never remember me dreams, so I don't. Maybe it's 'cause I'm fast asleep...{0000}
+====================================+

Line:
{7f04}{7f23}「まったく　夢ごときで{7f02}大さわぎになるとは{7f02}平和な村ですな。{0000}
Matched Line:
{7f04}{7f23}「まったく　夢ごときで{7f02}大さわぎになるとは{7f02}平和な村ですな。
Translated from b0533000.mpt (Confidence: 99.03%):
So main concern of populace is dream? Truly this is peaceful town...{0000}
+====================================+
```

### Control Characters

**General Notes:**

`{7f04}{7fXX}` comes at the beginning of each named dialog. Below is a list of names I've figured out.

**Control Code Table**

| Desc/Name | Control Code | Notes |
| ---- | ------------ | ----- |
| End of dialog | 0000 | Required to end dialog |
| New line + Tab | 7f02 | |
| Name decorator | 7f04 | Needs confirmation, always found at the beginning (italics maybe?) |
| Blinking Cursor | 7f0a | |
| EOL Signifier | 7f0b | Opposite of 7f0a |
| EOL Signifier | 7f0c | Comes in big groups like, 6 times in a row |
| Recieved gold | 7f15 | %a00520 in Android dialog |
| N/A | 7f16 | See 7f18 |
| N/A | 7f17 | e.g. "{7f17}なんだが", %a00100 in Android dialog |
| N/A | 7f18 | e.g. "{7f17}が　{7f15}本！{7f02}{7f18}が　{7f16}着！{7f02}たしかに　受け取ったぞ。" |
| ルーシア | 7f1a | Android translates to "Orifiela" |
| Player Name | 7f1f | %a00090 in Android dialog |
| ライアン | 7f20 | |
| アリーナ | 7f21 | Occasionally not translated in PSX | 
| クリフト | 7f22 | |
| ブライ | 7f23 | |
| トルネコ | 7f24 | |
| ミネア | 7f25 | |
| マーニャ | 7f26 | |
| スコット | 7f28 | |
| アレクス | 7f29 | |
| フレア | 7f2a | |
| ホイミン | 7f2b | |
| オーリン | 7f2c | |
| ホフマン | 7f2d | ホフマン is 7f2d but 7f2d is not always ホフマン |
| パノン | 7f2e | |
| ルーシア | 7f2f | |
| Person | 7f30 | %a00160 in Android dialog |
| ピサロ | 7f31 | Mostly seen as デス{7f31} i.e. adding Necro- to saro |
| ロザリー | 7f32 | |
| Person | 7f33 | %a00140 in Android dialog. エッグラ apologizes to this person |
| Some kind of custom name | 7f34 | %a00120 AND %a00140 in Android dialog |
| Some kind of town name | 7f42 | e.g "{7f42}は すでに世界で最大の町である。", %a00260 in Android dialog |
| Emphasis | 7f43 | Needs confirmation |
| Emphasis | 7f44 | Seems to be in sad places |
| Emphasis | 7f45 | Seen before デスピサロ's dialog sometimes |
| Noun | 7f4b | %a00120 in Android dialog e.g. "この上は　{7f4b}さんたちに頼るのみです。" |
| Name | 7f4c | %a00140 in Android dialog, same as 7f33?? |

**Names Without Control Chars**

*There's probably more here but w/e*

Name
* トム
* ドン・ガアデ
* シンシア

## Notes on Android Dialog Format

[Useful Forum Thread](https://www.romhacking.net/forum/index.php?topic=14879.20 )

Each English dialog starts with `@a@b`. Dialog with names starts with `@aName@b`. Each dialog ends with `@c0@`.

In hex these are:

> `40 61 40 62 | @a@b`

> `40 63 30 40 | @c0@`

The value `%a` actually represents the start of a name, so it can also be seen in dialog. The name is referenced by ID. An example of dialog referencing the hero is below.

`*: What's the matter, %a00090?\nHave you had enough?`

The Japanese files end with `@c0@`, `@c1@`, `@c2@` or `@c3@`. Not sure why. The name is also prefixed by a zero-padded 4 digit decimal i.e. `@a0001  王@b` (王 means King).

### Conditional Dialog in the Android English Script

In the Android english dialog there are a few places where there are control statements which display different text depending on which character you control. I'm generally not sure which to choose because I haven't played the game but the structure is as follows:

`%A, %B` - Basically a reverse if/else for names. An ID follows, i.e. `%A120` would mean "if you AREN'T Alena (アリーナ)". After the text in the example would be the "else" statement, with the same ID, i.e. `%B120`

`%X` begins a conditional text block and it is ended by `%Z`.

Putting this all together gives us a generic formula like so:

`%A{ID}%X{TEXT if not ID}%Z%B{ID}%X{TEXT if ID}%Z`

And an example from the script:

`%A120%XStill, if she were a boy—%Z%B120%XStill, if you were a boy—%Z`

Occasionally for plurals, there will be code like this:

`%H{ID}%X%Ys%Z`

where `ID` is some kind of relevant variable. e.g.

`Torneko receives %a00530 gold coin%H530%X%Ys%Z.`

Best guess is that the `%H` operator checks if something is greater than 1.

### Special Files

* 0020.csv seems to be mostly names.

### TO-DOs for the Auto-Translator
* [DONE] Replace names in beginning of dialog
* Add names at the beginning of English matched dialog
* Get rid of conditional lines
* [DONE] Figure out maximum number of characters per line
* Auto-place {7f02}s in appropriate places if translated lines are too long.

## Text Block Investigation

While Markus does a great job exploring the "Text Block" in his blog post I wanted to explore the block a little bit further.

First I looked into the "E" block. This contains two offsets which point us to the Huffman Tree and the D section.

**E Block**
| Name | Size | Description |
| ---- | ---- | ----------- |
| E1 | 4 bytes | Offset to Huffman Tree |
| E2 | 4 bytes | Length of Huffman Tree |
| E3 | 2 bytes | Number of Nodes in Huffman Tree |

### D Section - Probably not useful!!

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

**Example**
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

## DQ Scripting Language

There is a sort of scripting language found in sub-blocks with type 39. A lot of these are compressed with DQ's variant of LZS. Once decompressed the blocks have "commands" seperated typically by `0xB401`.

These blocks contain commands that start with `0x00C021A0` and are followed by two 2-byte arguments, a bit offset in the huffman code and the scene ID they're associated with.

Unfortunately these seem out of order and they don't always follow this pattern so more investigation is necessary.

## Credits

This effort is based on the work of Markus Schroeder, I hardly take credit for this, I just love Dragon Quest and want to see this game translated.

Links to his documentation:
* http://markus-projects.net/dragon-hackst-iv/
* https://www.romhacking.net/forum/index.php?topic=31357.0