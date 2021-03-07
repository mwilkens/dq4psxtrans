# Does nothing for now

'''
Sample ASM from Markus:

Begins with a jump from 0x8008EBA4 to 0x8001D4CC

      address  opcode   fun   args                comment
      -------------------------------------------------------------------
      8001D4CC 8E170058 mov   r23,[r16+58h]     ; r23 = [r16 + 0x58]        ; r16 is the start of the dialog textbox, not sure whats going on 58h bytes ahead
      8001D4D0 0017BA00 shl   r23,8h            ; r23 = r23 >> 8
      8001D4D4 0017BA02 shr   r23,8h            ; r23 = r23 << 8            ; EQV r23 = r23 & 0x00FFFFFF
      8001D4D8 3C158000 mov   r21,80000000h     ; r21 = 0x80000000          ; pointer base
      8001D4DC 02F5B825 or    r23,r21           ; r23 = r23 | r21           ; r23 is now a full pointer
      8001D4E0 02E5B823 sub   r23,r5            ; r23 = r23 - r5
      8001D4E4 8CB60004 mov   r22,[r5+4h]       ; r22 = [r5 + 0x04]         ; r5 is the dialog scene ID pointer, so r22 is the scene ID

Here's whats going on
Before:
r16 = 0x800F4DE8
r5  = 0x8018D768
@CC -> r23 = [0x800F4E40] (dialog pointer) = 0x5AD91815 (technically 0x1518D95A)
@D4 -> r23 = 0x0018D95A
@D8 -> r21 = 0x80000000
@DC -> r23 = 0x8018D95A


; Start of the outter if/else loop

      8001D4E8 3415006C mov   r21,6Ch           ; r21 = 0x006C              ; r21 = first scene dialogue pointer
------8001D4EC 16B60037 jne   r21,r22,8001D5CCh ; jump to the next scene    ; Only moves on if r22 != 0x6C
|
; This is the start of the inner if/else loop
|
|     8001D4F0 34150018 + mov r21,18h           ; r21 = 0x0018              ; Check byte distance
|  ---8001D4F4 16B70003 jne   r21,r23,8001D504h ; jump to the next dialog
|  |  8001D4F8 3C160500 + mov r22,5000000h      ; r22 = 0x05000000
|  |  8001D4FC 34170018 mov   r23,18h           ; r23 = r23 + 0x18
|  |  8001D500 08007575 jmp   8001D5D4h         ; jump to end + cleanup
|  |->8001D504 34150047 + mov r21,47h           ; r21 = 0x0047
|  ---8001D508 16B70003 jne   r21,r23,8001D518h ; jump if r21 != r23
|  |  8001D50C 3C161500 + mov r22,15000000h     ; r22 = 0x15000000
|  |  8001D510 34170020 mov   r23,20h           ; r23 = 0x0020
|  |  8001D514 08007575 jmp   8001D5D4h         ; jump to end + cleanup
|  |->8001D518 34150056 + mov r21,56h           ; r21 = 0x0056
|     8001D51C 16B70003 jne   r21,r23,8001D52Ch ; jump if r21 != r23
|
|     ...
|
|     8001D5B8 341501F2 + mov r21,1F2h          ; r21 = 0x01F2
|     8001D5BC 16B70003 jne   r21,r23,8001D5BCC ;
|     8001D5C0 3C162500 + mov r22,25000000h     ; bitIndex = 2
|     8001D5C4 34170069 mov   r23,69h           ; bitDist = 0x0069
|     8001D5C8 08007575 jmp   8001D5D4          ; jump to end + cleanup
|
; Ending if we didn't find any results, would also be the place for additional
; scenes
|
|---->8001D5CC ---      nop?
      8001D5D0 08023AEA jmp   8008EBA8h         ; jump back to after the nop

; Ending with a bit more cleanup
    
      8001D5D4 ---      nop?
      8001D5D8 00B7B821 add   r23,r5,r23        ; r23 = r5 + r23
      8001D5DC 0017BA00 shl   r23,8h            ; 
      8001D5E0 0017BA02 shr   r23,8h            ; r23 &= 0x00FFFFFF
      8001D5E4 02F6B825 or    r23,r22           ; r23 = r23 | r22
      8001D5E8 AE170058 mov   [r15+58h],r23     ;
      8001D5EC 08023AEA jmp   8008EBA8h         ; jump back to after the nop


== -- One Dialog ASM Chunk -- ==
+ mov r21,{{DIALOG_ID}}       
jne   r21,r23,{{NEXT_DIALOG_ADDR}}
+ mov r22,{{BIT_INDEX}}5000000h
mov   r23,{{BYTE_DIST}}h
jmp   {{END_POINTER}}
repeat...

== -- One Scene ASM Chunk -- ==
mov   r21,{{SCENE_ID}}
jne   r21,r22,{{NEXT_SCENE_ADDR}}
...Dialog ASM Chunks for scene...
repeat...

-- if we don't find anything make sure to go back unchanged
jmp   8008EBA8h

'''

