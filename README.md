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

### Names and their Mappings in the PSX Script

`{7f04}{7fXX}` comes at the beginning of each named dialog. Below is a list of names I've figured out.

Name Table
| Name | Control Code | Notes |
| ---- | ------------ | ----- |
| ライアン | 7f20 | |
| アリーナ | 7f21 | Occasionally not translated in PSX | 
| クリフト | 7f22 | |
| ブライ | 7f23 | |
| トルネコ | 7f24 |
| ミネア | 7f25 | |
| マーニャ | 7f26 |
| ホフマン | 7f2d | ホフマン is 7f2d but 7f2d is not always ホフマン |
| パノン | 7f2e | |
| ピサロ | 7f31 | Mostly seen as デス{7f31} i.e. adding Necro- to saro |
| トム | N/A | |
| ドン・ガアデ | N/A | |
| シンシア | N/A | |

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

### Other Control Codes

| Control Code | Android Code | Best Guess |
| ------------ | ------------ | ---------- |
| 7f17 | %a00100 | Some kind of relevant item |
| 7f15 | %a00750 or %a00620 or %a00530 | Gold amount for item, probably not consistent in Android |
| 7f43 | N/A | Used for emphasis, needs testing. |

### Special Files

* 0020.csv seems to be mostly names.

### TO-DOs for the Auto-Translator
* [DONE] Replace names in beginning of dialog
* Add names at the beginning of English matched dialog
* Get rid of conditional lines
* Figure out maximum number of characters per line
* Auto-place {7f02}s in appropriate places if translated lines are too long.

## Credits

This effort is based on the work of Markus Schroeder, I hardly take credit for this, I just love Dragon Quest and want to see this game translated.

Links to his documentation:
* http://markus-projects.net/dragon-hackst-iv/
* https://www.romhacking.net/forum/index.php?topic=31357.0