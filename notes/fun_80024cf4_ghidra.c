
int * FUN_80024cf4(int param_1,int **r8)

{
  byte bVar1;
  byte bVar2;
  byte bVar3;
  ushort uVar4;
  byte bVar5;
  int **ppiVar6;
  int iVar7;
  int svars_ptr;
  int *script_ptr;
  int *piVar8;
  int in_t5;
  byte byte3;
  byte byte3_2;
  char 2byte2bit;
  
  script_ptr = *(int **)(param_1 + 0xd4);
  2byte2bit = *(char *)(r8 + 1);
  svars_ptr = *(int *)(param_1 + 0x118);
  if (2byte2bit == '\0') {
    *r8 = (int *)0x0;
    return script_ptr;
  }
  if (2byte2bit == '\x01') {
    byte3 = *(byte *)script_ptr;
    piVar8 = (int *)((int)script_ptr + 1);
    switch(byte3) {
    case 0xa0:
    case 0xa6:
      script_ptr = (int *)(param_1 + 0xdc);
      break;
    case 0xa1:
      script_ptr = (int *)(param_1 + 0xe0);
      break;
    case 0xa2:
    case 0xa9:
      script_ptr = (int *)(param_1 + 0xe4);
      break;
    case 0xa3:
    case 0xa8:
      script_ptr = (int *)(param_1 + 0xe8);
      break;
    case 0xa4:
      script_ptr = (int *)(param_1 + 0xec);
      break;
    case 0xa5:
      script_ptr = (int *)(param_1 + 0xf0);
      break;
    case 0xa7:
      script_ptr = (int *)(param_1 + 0xdd);
      break;
    default:
      script_ptr = (int *)0x0;
    }
    *r8 = script_ptr;
    if (1 < (byte)(byte3 + 0x5a)) {
      script_ptr = (int *)0x1;
      if (byte3 == 0xa9) goto LAB_800250ec;
      if (byte3 != 0xa8) goto LAB_800250e8;
    }
    script_ptr = (int *)0x1;
  }
  else {
    if (2byte2bit == '\x02') {
      bVar5 = *(byte *)script_ptr;
      bVar1 = *(byte *)((int)script_ptr + 1);
      bVar2 = *(byte *)((int)script_ptr + 2);
      bVar3 = *(byte *)((int)script_ptr + 3);
      *r8 = (int *)(r8 + 3);
      r8[2] = (int *)0x7;
LAB_80024e78:
      r8[3] = (int *)CONCAT13(bVar3,CONCAT12(bVar2,CONCAT11(bVar1,bVar5)));
      return script_ptr + 1;
    }
    if (2byte2bit == '\x03') {
      bVar5 = *(byte *)script_ptr;
      *r8 = (int *)(r8 + 3);
      r8[2] = (int *)0x1;
      r8[3] = (int *)(uint)bVar5;
      return (int *)((int)script_ptr + 1);
    }
    if (2byte2bit == '\x04') {
      uVar4 = *(ushort *)script_ptr;
      *r8 = (int *)(r8 + 3);
      r8[2] = (int *)0x2;
      r8[3] = (int *)(uint)uVar4;
      return (int *)((int)script_ptr + 2);
    }
    if (2byte2bit == '\x05') {
      bVar5 = *(byte *)script_ptr;
      bVar1 = *(byte *)((int)script_ptr + 1);
      bVar2 = *(byte *)((int)script_ptr + 2);
      bVar3 = *(byte *)((int)script_ptr + 3);
      *r8 = (int *)(r8 + 3);
      r8[2] = (int *)0x3;
      goto LAB_80024e78;
    }
    if (2byte2bit != '\x06') {
      return script_ptr;
    }
    byte3_2 = *(byte *)script_ptr;
    bVar5 = byte3_2 & 7;
    piVar8 = (int *)((int)script_ptr + 1);
    if ((byte3_2 & 7) == 0) {
      *r8 = *(int **)(param_1 + 0xcc);
    }
    else {
      if (bVar5 == 1) {
        bVar5 = *(byte *)piVar8;
        piVar8 = (int *)((int)script_ptr + 2);
        switch(bVar5) {
        case 0xa0:
        case 0xa6:
          ppiVar6 = (int **)(param_1 + 0xdc);
          break;
        case 0xa1:
          ppiVar6 = (int **)(param_1 + 0xe0);
          break;
        case 0xa2:
        case 0xa9:
          ppiVar6 = (int **)(param_1 + 0xe4);
          break;
        case 0xa3:
        case 0xa8:
          ppiVar6 = (int **)(param_1 + 0xe8);
          break;
        case 0xa4:
          ppiVar6 = (int **)(param_1 + 0xec);
          break;
        case 0xa5:
          ppiVar6 = (int **)(param_1 + 0xf0);
          break;
        case 0xa7:
          ppiVar6 = (int **)(param_1 + 0xdd);
          break;
        default:
          ppiVar6 = (int **)0x0;
        }
        *r8 = *ppiVar6;
      }
      else {
        if (bVar5 == 2) {
          svars_ptr = *(int *)(svars_ptr + 0x34);
          iVar7 = (uint)*(ushort *)piVar8 << 0x10;
        }
        else {
          if (bVar5 != 3) {
            if (bVar5 == 4) {
              piVar8 = (int *)((int)script_ptr + 3);
              *r8 = (int *)0x0;
            }
            else {
              if (bVar5 == 5) {
                iVar7 = (uint)*(ushort *)piVar8 << 0x10;
                svars_ptr = *(int *)(svars_ptr + 0x38);
                goto LAB_80024fc4;
              }
            }
            goto LAB_80024fdc;
          }
          svars_ptr = *(int *)(svars_ptr + 0x3c);
          iVar7 = (uint)*(ushort *)piVar8 << 0x10;
        }
LAB_80024fc4:
        piVar8 = (int *)((int)script_ptr + 3);
        *r8 = *(int **)((iVar7 >> 0xe) + svars_ptr);
      }
    }
LAB_80024fdc:
    bVar5 = byte3_2 & 0xc0;
    if ((byte3_2 & 0xc0) == 0) {
      in_t5 = 0;
    }
    else {
      if (bVar5 == 0x40) {
        in_t5 = (int)(char)*(byte *)piVar8;
        piVar8 = (int *)((int)piVar8 + 1);
      }
      else {
        if (bVar5 == 0x80) {
          uVar4 = *(ushort *)piVar8;
          piVar8 = (int *)((int)piVar8 + 2);
          in_t5 = (int)(short)uVar4;
        }
        else {
          if (bVar5 == 0xc0) {
            in_t5 = *piVar8;
            piVar8 = piVar8 + 1;
          }
        }
      }
    }
    if ((byte3_2 & 7) == 0) {
      script_ptr = *r8 + in_t5;
    }
    else {
      script_ptr = (int *)((int)*r8 + in_t5);
    }
    bVar5 = byte3_2 & 0x38;
    *r8 = script_ptr;
    if ((byte3_2 & 0x38) == 0) {
      r8[2] = (int *)0x0;
      return piVar8;
    }
    script_ptr = (int *)0x1;
    if ((((bVar5 == 8) || (script_ptr = (int *)0x2, bVar5 == 0x10)) ||
        (script_ptr = (int *)0x3, bVar5 == 0x18)) ||
       (((script_ptr = (int *)&DAT_00000004, bVar5 == 0x20 ||
         (script_ptr = (int *)0x5, bVar5 == 0x28)) ||
        (script_ptr = (int *)&DAT_00000006, bVar5 == 0x30)))) goto LAB_800250ec;
    if (bVar5 != 0x38) {
      return piVar8;
    }
LAB_800250e8:
    script_ptr = (int *)0x7;
  }
LAB_800250ec:
  r8[2] = script_ptr;
  return piVar8;
}

