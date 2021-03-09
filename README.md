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
* Write Huffman Encode Functionality
* Write Textblock Modification Functionality
* Calculate Pointer Mod Values
* [WIP] Write ASM Generator for Pointer Redirection
* Write Binary Patcher for SLPM_869.16
* Actually patch all the dialog in DQ4 :)
* Write DQ LZS Algorithm
* Extract all TIM Files
* Write Patcher for TIM Files 
* Figure out where every other bit of dialog is
* ... TBD
* Make a cute intro

## Notes on Android Dialog Format

[Useful Forum Thread](https://www.romhacking.net/forum/index.php?topic=14879.20 )

Each English dialog starts with `@a@b`. Dialog with names starts with `@aName@b`. Each dialog ends with `@c0@`.

In hex these are:

> `40 61 40 62 | @a@b`

> `40 63 30 40 | @c0@`

The value `%a` actually represents the start of a name, so it can also be seen in dialog. The name is referenced by ID. An example of dialog referencing the hero is below.

`*: What's the matter, %a00090?\nHave you had enough?`

The Japanese files end with `@c0@`, `@c1@`, `@c2@` or `@c3@`. Not sure why. The name is also prefixed by a zero-padded 4 digit decimal i.e. `@a0001  王@b` (王 means King).

## Auto Translation

The auto-translator works fairly well as of right now. It can very accurately match dialog but the PSX dialog comes in bigger chunks than the Android dialog, so occasionally some portions of the dialog go unmatched. Additionally some control characters are lost in translation. Below is an example of both the performance and the shortcomings mentioned above.

```
Line:
デスピサロ……不吉な名前じゃ。{7f0b}{0000}
Matched Line:
デスピサロ……不吉な名前じゃ。{0000}
Translated from b0016000.mpt (Confidence: 19.28%):
*: Psaro the Manslayer... The name alone gives me the willies.{0000}
+====================================+
Line:
王様と　姫さまは　{7f02}すでに　お休みでございます。{7f0b}{0000}
Matched Line:
王様と　姫さまは{7f02}すでに　お休みでございます。{0000}
Translated from b0016000.mpt (Confidence: 90.67%):
*: King Norman and Princess Veronica have already retired to their chambers.{0000}
+====================================+
Line:
お父さまが　みなに{7f02}約束をしたため　私は優勝者と{7f02}結婚しなくてはなりません。{7f0a}{7f02}でも　 
もし優勝者が{7f02}女の人だったら　私は　無理な{7f02}結婚をしなくても　すむでしょう。{7f0a}{7f02}お願い 
でございます。{7f02}どうか　武術大会に{7f02}出てくださいまし！{7f0a}{7f02}アリーナ姫さま。{7f02}私は　 
自由に生きている{7f02}あなたを　うらやましく思いますわ。　{7f0b}{0000}
Matched Line:
でも　もし優勝者が{7f02}女の人だったら　私は　無理な{7f02}結婚をしなくても　すむでしょう。{0000}       
Translated from b0016000.mpt (Confidence: 5.48%):
But if the winner were a woman, then the whole thing would surely have to be called off.{0000}
```

### Names and their Mappings in the PSX Script

`{7f04}{7fXX}` comes at the beginning of each named dialog. Below is a list of names I've figured out.

Name Table
| Name | Control Code | Notes |
| ---- | ------------ | ----- |
| ライアン | 7f20 | |
| アリーナ | 7f21 | Occasionally not translated in PSX | 
| クリフト | 7f22 |
| ブライ | 7f23 |
| トルネコ | 7f24 |
| ミネア | 7f25 |
| マーニャ | 7f26 |
| パノン | 7f2e |
| ピサロ | 7f31 | Mostly seen as デス{7f31} i.e. adding Necro- to saro

### Conditional Dialog in the Android English Script

In the Android english dialog there are a few places where there are control statements which display different text depending on which character you control. I'm generally not sure which to choose because I haven't played the game but the structure is as follows:

`%A, %B` - Basically a reverse if/else for names. An ID follows, i.e. `%A120` would mean "if you AREN'T Alena (アリーナ)". After the text in the example would be the "else" statement, with the same ID, i.e. `%B120`

`%X` begins a conditional text block and it is ended by `%Z`.

Putting this all together gives us a generic formula like so:

`%A{ID}%X{TEXT if not ID}%Z%B{ID}%X{TEXT if ID}%Z`

And an example from the script:

`%A120%XStill, if she were a boy—%Z%B120%XStill, if you were a boy—%Z`

### TO-DOs for the Auto-Translator
* Somehow replace names in beginning of dialog
* Get rid of conditional lines
* Figure out maximum number of characters per line
* Auto-place {7f02}s in appropriate places if translated lines are too long.

## Credits

This effort is based on the work of Markus Schroeder, I hardly take credit for this, I just love Dragon Quest and want to see this game translated.

Links to his documentation:
* http://markus-projects.net/dragon-hackst-iv/
* https://www.romhacking.net/forum/index.php?topic=31357.0