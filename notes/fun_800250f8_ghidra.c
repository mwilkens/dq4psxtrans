
undefined4 * FUN_800250f8(int param_1)

{
  byte bVar1;
  ushort uVar2;
  undefined4 arg1_addr;
  byte *script_addr;
  undefined4 *puVar3;
  int iVar4;
  byte opcode_1;
  
  script_addr = *(byte **)(param_1 + 0xd0);
  iVar4 = *(int *)(param_1 + 0x118);
  opcode_1 = *script_addr;
  puVar3 = (undefined4 *)(script_addr + 1);
  if (opcode_1 != 0xb0) {
    if ((opcode_1 == 0xb1) || (opcode_1 == 0xb2)) {
      arg1_addr = *puVar3;
      puVar3 = (undefined4 *)(script_addr + 5);
      *(undefined4 *)(param_1 + 0x100) = arg1_addr;
    }
    else {
      if ((byte)(opcode_1 + 0x4f) < 0x48) {
        bVar1 = *(byte *)puVar3;
        *(byte **)(param_1 + 0xd4) = script_addr + 2;
        *(byte *)(param_1 + 0xf8) = bVar1 & 0xf;
        *(byte *)(param_1 + 0x108) = bVar1 >> 4;
        arg1_addr = FUN_80024cf4(param_1,param_1 + 0xf4);
        *(undefined4 *)(param_1 + 0xd4) = arg1_addr;
        puVar3 = (undefined4 *)FUN_80024cf4(param_1,param_1 + 0x104);
        *(undefined4 **)(param_1 + 0xd4) = puVar3;
        if (0xf2 < opcode_1) {
          uVar2 = *(ushort *)puVar3;
          puVar3 = (undefined4 *)((int)puVar3 + 2);
          *(undefined4 *)(param_1 + 0x114) =
               *(undefined4 *)(((int)((uint)uVar2 << 0x10) >> 0xe) + *(int *)(iVar4 + 0x34));
        }
      }
      else {
        puVar3 = (undefined4 *)0x0;
      }
    }
  }
  return puVar3;
}

