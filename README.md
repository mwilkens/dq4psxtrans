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

### D Blocks

While understanding these further might be necessary, for now these are being tabled. You can read more in [dblock.md](dblock.md).

## DQ Scripting Language

There is a sort of scripting language found in sub-blocks with type 39. A lot of these are compressed with DQ's variant of LZS.

These blocks contain commands that start with `c021a0` and are followed by two 2-byte arguments, a bit offset in the huffman code and the scene ID they're associated with. In an ideal world we could just change these and hope for the best but I want to dig deeper.

Here are my current thoughts on this scripting language.

Each section starts with `b1` <3 bytes> and ends with `b2` <3 bytes>. Within each section there are "lines of commands" starting with `00` and separated by `b4`, these lines are further grouped by the `b3` keyword.

That means each section looks like so:
```
b1 <3 bytes>
        00 <commands>
        b4 <commands>
        ...
        b4 <commands> <e-type command>
    b3 <4 bytes>
        00 <commands>
        ... etc
b2 <3 bytes>
    00 434343 (or more generally 00 xyxyxy, etc unclear what these 3 repeated bytes are)
```

Here is an example of a [full script](26046-6.txt).


Subblocks might only contain part of a script, as some end in non-terminated `b1` blocks. Full scripts end in a long series of 4-byte integers.

Finally here's my updated list of opcodes and keywords and my notes on them.

### Opcodes:

**-- Functions --**
| OpCode | Arguments | Notes |
| ------ | --------- | ----- |
| `c01678` | `<1 bytes>` | <a0> keyword always follows, maybe starts a loop or conditional? |
| `c021a0` | `<2 bytes> <2 bytes>` | Used with dialog pointers, but definitely not always |
| `c02678` | `<1 byte> <1 byte> <1 byte> <2 bytes>` | |
| `c02639` | `<3 bytes>` | only seen 1 of these, related to `c211a1` |
| `c0263b` | `<4 bytes>` | only seen 1 of these, related to `c02639` |
| `c061a0` | `<2 bytes>` | always seen after `c021a0` with dialog info |
| `c161a1` | `<3 bytes>` | some kind of address, often `b8fbff` or `b8faff` |
| `c211a1` | `<1 bytes>` | only seen 1 of these, related to `c02639` |
| `c40678` | `<1 bytes>` | only seen 1 of these |
| `c821a0` | `<2 bytes> <2 bytes>` | related to `c40678` probably |

**-- Subsection Commands --**
| OpCode | Arguments | Notes |
| ------ | --------- | ----- |
| `e0063d` | `<2 bytes>` | |
| `e10300` | `<no arg>` | |
| `e10301` | `<no arg>` | |
| `e10302` | `<no arg>` | |
| `e10303` | `<no arg>` | |
| `e10305` | `<no arg>` | |

**-- Jump Commands --**
| OpCode | Arguments | Notes |
| ------ | --------- | ----- |
| `f1063a` | `<2 bytes>` | absolutely related to the b keywords
| `f421a0` | `<4 bytes> <2 bytes>` | 2nd argument increases throughout script, goto command?
| `f761a0` | `<2 bytes> <2 bytes>` | similar to `f421a0` but 1st command is much larger

-- Non-standard --
| OpCode | Arguments | Notes |
| ------ | --------- | ----- |
| `434343` | | called between b1 and b2 keywords |
| `585858` | | called between b1 and b2 keywords |

### Keywords:

| Keyword | Arguments | Notes |
| ------ | --------- | ----- |
`b0` | None | usually but not always seen with f1063a
`b1` | `<3 bytes>` | start of major section
`b2` | `<3 bytes>` | end of major section
`b3` | `<4 bytes>` | separater of minor sections
`b4` | None | some sort of separator, always followed by 01aX
`a0` | None | found with c01678, seen in a lot of op-codes too so not sure about this one
`01a0` | None | always found between commands
`01a1` | None | always found between commands

## Credits

This effort is based on the work of Markus Schroeder, I hardly take credit for this, I just love Dragon Quest and want to see this game translated.

Links to his documentation:
* http://markus-projects.net/dragon-hackst-iv/
* https://www.romhacking.net/forum/index.php?topic=31357.0