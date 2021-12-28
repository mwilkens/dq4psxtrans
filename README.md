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

While understanding these further might be necessary, for now these are being tabled. You can read more in [dblock.md](notes/dblock.md).

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

Here is an example of a [full script](notes/26046-6.txt).


Subblocks might only contain part of a script, as some end in non-terminated `b1` blocks. Full scripts end in a long series of 4-byte integers.

Finally here's my updated list of opcodes and keywords and my notes on them.

### Opcodes:

There are a few types of op-codes that I've identified. They are listed below with notes:

| Type | Example | Notes |
| ---- | ------- | ----- |
| b-type | `B401A0` | These usually structure the code, not always 3-bytes in length |
| c-type | `C021A0 <2 byte> <2 byte>` | These seem to relate to actual functions called (i.e. put dialog on screen) | 
| d-type | `D021A0 <2 byte> <2 byte>` | VERY rare |
| e-type | `E10301` | These normally begin the code blocks structured with `B3` |
| f-type | `F421A0 <4 bytes> <2 byte label>` | These provide basic scripting structures "goto"/"if" |
| weird | `434343` | Between `B2` and `B1` structure labels, I have no clue |

### Dialog Portion Analysis

Looking at a few places where dialog is placed on the screen there is a certain pattern that emerges:

```
C021A0 <bit offset> <dialog id>
B401A0
C061A0 <unknown> # usually 0x7801 or 0x78FA
B401A0
C021A0 <1FF> <0>
B401A0
```

This has been true of every dialog I've seen thus far, however I could be wrong.

Additionally looking at the script code for the first line of dialog, we see a different block following.
This I believe triggers the yes or no dialog box that appears after that line. The code looks like so:

```
C021A0 <1F7> <0>
B401A0
```

Ok~ with that in mind, now we have a branch "yes" (はい) or "no" (いいえ).

Lets dissect the dialog flow then look at the script with that in mind.

Here's what this looks like:

```
Dialog 0xF91 (どうした？　Name。もう　降参かい？)
Yes/No Box Shown.
If Yes:
     Dialog 0xEF9 (そうだな。今日は　このくらいに...)
     Dialog 0xD0E (私の役目は　はやく　お前を...)
If No:
     Dialog 0xC28 (おお！！　なかなか頑張るな。)
     Dialog 0xD0E (私の役目は　はやく　お前を...)
```

Ok then the code (simplified):

```
C021A0 <F91> <6C0> 
C061A0 <FA78>
C021A0 <1FF> <0> # Shows (どうした？　Name。もう　降参かい？)
C021A0 <1F7> <0> # Shows yes/no box
F421A0 <61A9> <1A> # Marker 1A + Goto Operation
C021A0 <EF9> <6C0> 
C061A0 <FA78>
C021A0 <1FF> <0> # Shows (そうだな。今日は　このくらいに...)
F1063A <1B> # Marker 1B
C021A0 <C28> <6C0>
C061A0 <FA78>
C021A0 <1FF> <0> # Shows (おお！！　なかなか頑張るな。)
C021A0 <D0E> <6C0>
C061A0 <FA78>
C021A0 <1FF> <0> # Shows (私の役目は　はやく　お前を...)
```

While I'm not entirely sure how this works, it seems that the F-type commands are jump/choice commands.

The F-type commands have a second argument that have unique (usually increasing) values throughout the script.
I suspect these are goto operations.

## Credits

This effort is based on the work of Markus Schroeder, I hardly take credit for this, I just love Dragon Quest and want to see this game translated.

Links to his documentation:
* http://markus-projects.net/dragon-hackst-iv/
* https://www.romhacking.net/forum/index.php?topic=31357.0