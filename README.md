# Dragon Quest 4 PSX Translation
Attempt at Python tooling for the Dragon Quest 4 PSX Translation

My goal here is to get at least an accessible foundation for translation started. I'm fairly new to rom hacking but I'm comfortable with reverse engineering so this should be a fun project :)

Progess:

* [DONE] Parse Data File Blocks
* [DONE] Parse Data File SubBlocks
* [DONE] Parse Text SubBlocks
* [DONE] Extract Text Huffman Coding Data
* [DONE] Decode Huffman Encoded Text
* [DONE] Extract Japanese Script from File
* Convert Android English Text to Correct Format
* Map Android Textblock UUIDs to PSX Textblock UUIDs
* Write Huffman Encode Functionality
* Write Textblock Modification Functionality
* Calculate Pointer Mod Values
* Write ASM Generator for Pointer Redirection
* Write Binary Patcher for SLPM_869.16
* Actually patch all the dialog in DQ4 :)
* Write DQ LZS Algorithm
* Extract all TIM Files
* Write Patcher for TIM Files 
* Figure out where every other bit of dialog is
* ... TBD
* Make a cute intro

This effort is based on the work of Markus Schroeder, I hardly take credit for this, I just love Dragon Quest and want to see this game translated.

Links to his documentation:
* http://markus-projects.net/dragon-hackst-iv/
* https://www.romhacking.net/forum/index.php?topic=31357.0