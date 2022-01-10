// 8008EB80 I think
void display_dialog() {
	more but who cares
	// breakpoint for normal NPC dialog
	//8008EBA4
	while r2 != 0 {
		//8008EBB0
		fun_80072210() // display 2 characters to screen
		//8008EBB8 - return address is here when we need to fill more text
		r2 = *(r16+0x7F)
	}
	// At this point every line of dialog is written
	
	// This is the scene and offset of what was just written
	r16 = *(sp+10) // 0690015F (dialog id and offset)
	return *(sp+14) // 80128B74 at end of prologue
}

void fun_idk() {
	// more
	fun_8002F4B0()
	display_dialog()
	// some useless move operation
	
	r16 = *(sp+0x10) //0x800F921C
	return *(sp+0x14) // 800252E8
}

void process_script() {
	// something
	
	switch ( maybe ? ) {
		case idk:
			// r8 = ?
			r7 = r7 & r2 // + and
			r4 = *r8
			r8 += 0x4
			r5 = *r8
			r6 = *(r8+0x4)
			fun_idk()
			break
		case idk2:
			...
			fun_idk()
			break
	}
	
	//8002549C
	*r16 = r7 // r7 = 0
	r16 = *(sp+0x28) // FFFFFFFF
	return *(sp+0x2C) // 800256B0
}

//800254B0
void idk(){
	// more
	while_or_switch(){
		// more
		// 800256B0
		break
	}
	// 80026758
	return *(sp+0x18) // 80024A98
}

void idk2(){

	fun_800250F8()
	//80024A84
	r4 = r17 // + mov
	r4 = r17
	idk()
	//80024A98
	// r2 == 0, r6 is an address
	// r6 = 800DB74C - nothing interesting
	// r17 = 800F9140 - 555555 sections, idk!
	if r2 != r6 {
		*(sp+2C) = r2 // + mov
		if r2 != 0 {
			*(r17+0x0D4) = r2	
		}
		r2 = *r17
		r3 = *(r17+0x0D4)
		r2 &= 0x1
		if r2 != 0 {
			goto 80024A84
		}
		*(r17+0x0D0) = r2
	}
	// 80024AC0
	r4 = -2
	r2 = *r17
	r3 = *(r17+0x0DC)
	r3 = r3 & r4
	*r17 = r3
}

// 800250F8
// script_addr -> r6
void fun_800250F8(){
	sp -= 0x28
	*(sp+0x18) = r18 // 0xC00
	r18 = r4 // 800F9140
	*(sp+0x10) = r16 // FFFFFFFF
	r16 = r18 + 0x8 // 800F9148 <- contains the offset to the script code
	*(sp+0x20) = ra // 80024A8C
	*(sp+0x1C) = r19 // 0
	*(sp+0x14) = r17 // 800F9140
	// C8 == 200
	script_addr = *(r16+0xC8) // 8018FB9D <- script code!!!
	r19 = *(r18+0x118) // 8018F3F0
	r3 = *script_addr // C0 (start of C021A0 command)
	r17 = r3 & 0x0FF
	
	if r17 != 0x0B0 {
		script_addr += 1
		if r17 != 0x0B1 & r17 != 0x0B2 {
			r2 = r3 + 0x4F
			goto 80025180
		}
		// Process b-type command
		r2 = *(script_addr+0)
		r3 = *(script_addr+1)
		r4 = *(script_addr+2)
		r5 = *(script_addr+3)
		script_addr += 4
		r3 = r3 << 8
		r2 = r2 | r3
		r4 = r4 << 16
		r2 = r2 | r4
		r5 = r5 << 24
		r2 = r2 | r5
		*(r16+0x0F8) = r2
		goto 8002520C
		
		// 80025180
		r2 = r2 & 0x0FF // 0x10F
		// r2 = 0xF at this point
		if r2 >= 0x48 {
			r2 = 0
			goto 80025210
		} else {
			r4 = r18
		}
		r3 = *script_addr // r3 = 0x21 now
		script_addr += 1
		r5 = r18 + 0x0F4 // not sure what this is doing
		*(r16+0xCC) = script_addr
		r2 = r3 & 0xF // r2 = 1
		r3 = r3 & 0xFF
		r3 = r3 >> 4 // r3 = 2
		*(r16+0xF0) = r2
		*(r16+0x100) = r3
		// ok so at this point we have this around r16
		// at 0xCC we have a pointer to the last portion of the opcode
		// at 0xF0 we have the "1" from 0x21
		// not sure when this happened but also this
		// at 0x100 we have the "2" from 0x21
		fun_80024C54()
		
		r4 = r18
		r5 = r4 + 0x104
		fun_80024C54()
		*(r16+0xCC) = r2
		script_addr = r2
		if r17 >= 0xF3 {
			*(r16+0xCC) = script_addr
			r3 = *(script_addr+1)
			r2 = *script_addr
			r3 = r3 << 8
			r2 = r2 | r3
			r2 = r2 << 16
			r3 = *(r19+0x34)
			r2 = r2 ??? 0x0E // sar
			r2 = r2 + r3
			r2 = *r2
			script_addr += 2
			*(r16+0x10C) = r2
		}
	}
	// 80025210
	r2 = script_addr
	
}

//80024C54
void fun_80024C54(){
	r8 = r5 //r5 is 800F9234
	r5 = r4 + 0x8 // r4 is 800F9140
	
	r7 = *(r5+0xCC) // 
	r3 = *(r8+0x4)  //
	r4 = *(r4+0x118) //
	
	if r3==0 {
		*r8 = 0
		goto 800250F0
	} else if r3 == 1 {
		r6 = *r7
		r3 = r6 - 0xA0
		r2 = r3 < 0xA
		if r2 != 0 {
			r7 += 1
			r2 = *(80018D58)
			r3 = r3 << 2
			r3 += r2
			r2 = *r3
			// r2 will be an address, this is for clarity
			switch( r2 ?? ) {
				case 1:
					r4 = r5 + 0xD4
					break;
				case 2:
					r4 = r5 + 0xD5
					break;
				case 3:
					r4 = r5 + 0xE0
					break;
				case 4:
					r4 = r5 + 0xE4
					break;
				case 5:
					r4 = r5 + 0xE8
					break;
				default:
					r2 = 0
			}
		}
		
		// 800024D94
		r2 = r6 + 0x5A
		r2 = r2 & 0xFF
		r2 = r2 < 2
		if r2 == 0 {
			r3 = r6 & 0xFF
			r2 = 0xA9
			if r3 == r2 {
				r2 = 1 
				goto 800250EC
			}
			r2 = 0xA8
			if r3 != r2 {
				goto 800250E8
			}
		} else {
			*r8 = r4
		}
		r2 = 1
		goto 800250EC
	} else if r3 == 2 {
		r3 = *(r7+0)
		r4 = *(r7+1)
		r5 = *(r7+2)
		r6 = *(r7+3)
		r7 += 4
		r2 = r8 + 0x0C
		*r8 = r2
		r2 = 0x7
		*(r8+8) = r2
		goto 80024E78
	} else if r3 == 3 {
		r3 = *r7
		r7 += 1
		r2 = r8 + 0x0C
		*r8 = r2
		*(r8+0x8) = r6
		*(r8+0x0C) = r3
		goto 800250F0
	} else if r3 == 4 {
		r4 = *(r7+0)
		r3 = *(r7+1)
		r7 += 2
		r2 = r8 + 0x0C
		*r8 = r2
		*(r8+8) = r9
		r3 = r3 << 8
		r4 = r4 | r3
		*(r8+0xC) = r4
		goto 800250F0
	} else if r3 == 5 {
		r3 = *(r7+0)
		r4 = *(r7+1)
		r5 = *(r7+2)
		r6 = *(r7+3)
		r7 += 4
		r2 = r8 + 0x0C
		*r8 = r2
		*(r8+8) = r10
		r4 = r4 << 8
		r3 = r3 | r4
		r5 = r5 << 16
		r3 = r3 | r5
		r6 = r6 << 24
		r3 = r3 | r6
		*(r8+0xC) = r3
		goto 800250F0
	} else if r3 == 6 {
		r14 = *r7
		r2 = r14 & 0x7
		if r2 == 0 {
			r2 = *(r5+0xC4)
			*r8 = r2
			goto 80024FD8
		} else {
			r7 += 1
		}
		
		if r2 == r6 {
			r6 = *r7
			r3 = r6 - 0xA0
			if r3 < 0x0A {
				r2 = 80018D80
				r3 = r3 << 2
				r3 += r2
				r2 = *r3
				switch( r2 ?? ) {
					case 1:
						r2 = r5 + 0xD4
						break;
					case 2:
						r2 = r5 + 0xD5
						break;
					case 3:
						r2 = r5 + 0xE0
						break;
					case 4:
						r2 = r5 + 0xE4
						break;
					case 5:
						r2 = r5 + 0xE8
						break;
					default:
						r2 = 0
				}
			} else {
				r7 += 1
			}
			r2 = *r2
			*r8 = r2
			goto 80024FD8
		}
		if r2 == r9 {
			r3 = *(r7+1)
			r2 = *(r7+0)
			r3 = r3 << 8
			r2 = r2 | r3
			r3 = *(r4+0x34)
			r2 = r2 << 16
			goto 80024FC4
		}
		if r2 == r10 {
			r3 = *(r7+1)
			r2 = *(r7+0)
			r3 = r3 << 8
			r2 = r2 | r3
			r3 = *(r4+0x3C)
			r2 = r2 << 16
			goto 80024FC4
		} // 80024F90
		if r2 == r12 {
			r7 += 2
			*r8 = 0
			goto 80024FD8
		}
		if r2 == r11 {
			r3 = *(r7+1)
			r2 = *(r7+0)
			r3 = r3 << 8
			r2 = r2 | r3
			r3 = *(r4+0x38)
			r2 = r2 sar 0x0E
			r2 += r3
			r2 = *r2
			r7 += 2
			*r8 = r2
			// 80024FD8
			r3 = r14 & 0x0C0
		} else {
			r3 = r14 & 0x0C0
		}
		if r3 == 0 {
			r13 = 0
			goto 8002505C
			// 800250E8
			r2 = 7
		} else {
			r2 = 0x40
		} //80024FEC
		if r3 == r2 {
			r13 = *r7
			r7 += 1
			goto 8002505C
		} else {
			r2 = 0x80
		}
		
		if r3 == r2 {
			r3 = *(r7+0)
			r2 = *(r7+1)
			r7 += 2
			r2 = r2 << 8
			r3 = r3 | r2
			r3 = r3 << 16
			r13 = r3 sar 0x10
			goto 8002505C
		} else {
			r2 = 0xC0
		}
		
		if r3 == r2 {
			r4 = *(r7+0)
			r2 = *(r7+1)
			r3 = *(r7+2)
			r5 = *(r7+3)
			r7 += 4
			r2 = r2 << 8
			r4 = r4 | r2
			r3 = r3 << 16
			r4 = r4 | r3
			r5 = r5 << 24
			r4 = r4 | r5
		}
		
		r2 = r14 & 0x7
		if r2 == 0 {
			r2 = *r8
			r2 += r3
			goto 80025080
		} else {
			r3 = r13 << 2
		} // 80025074
		r2 = *r8
		r2 += r13
		
		// 80025080
		r3 = r14 & 0x38
		if r3 == 0 {
			*(r8+0x8) = 0
			goto 800250F0
		} else {
			*r8 = r2
		}
		
		switch( r3 ){
			case 0x08:
				r2 = 1
				break
			case 0x10:
				r2 = 2
				break
			case 0x18:
				r2 = 3
				break
			case 0x20:
				r2 = 4
				break
			case 0x28:
				r2 = 5
				break
			case 0x30:
				r2 = 6
				break
			case 0x38:
				r2 = 7
				break
			default:
				return
		}
		// 800250EC
		*(r8+8) = r2
	}
	return
}