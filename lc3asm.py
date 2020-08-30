#Written by Joseph Long 


import numpy as np

# file = ['.orig x3000', 'HELLO:',' ADD R1, R1, #5', 'LD R1, ascii','BRnz HELLO',' ADD R1, R1, #5','HALT','ascii: .FILL x30', 'list: .BLKW 4', 'ascii2: .FILL x30', '.END']
file = ['.orig x3000', 'AND R0, R0, #0', 'ADD R0, R0, #1', 'LD R1, ascii', 'ADD R0, R0, R1', 'OUT', 'HALT', 'ascii: .FILL x30', '.END']
out = {}
currentPath = ''

symTable = {}
pc = np.int16(0)

def parseNum(str):
    if str[0] == 'x':
        return int(str[1:], base=16)
    elif str[0] == '#':
        return int(str[1:], base=10)
    elif str in symTable:
        return symTable[str]

def moveSign(num, bits):
    if num < 0:
        num|=1<<(bits-1)
    else:
        num&=~(1<<(bits-1))
    return num

def origPsOp (instruct):
    global pc
    pc = parseNum(instruct[1])
    print("[LC3asm.py] PC assigned as " + str(hex(pc)))

def fillPsOp (instruct):
    global pc
    out[pc] = parseNum(instruct[1])
    pc+=1

def blkwPsOp (instruct):
    global pc
    pc+=int(instruct[1])

def stringzOp (instruct):
    global pc
    for c in bytes(instruct[1:-1], "utf-8").decode("unicode_escape"):
        out[pc] = ord(c)
        pc+=1
    
    out[pc] = 0
    pc+=1

def trapPsOp (instruct):
    global pc
    bina = 0b1111000000000000
    bina |= trapPs_ops[instruct[0].lower()]&0b11111111
    out[pc] = bina
    pc+=1

def addOp (instruct):
    bina = 0b0001000000000000
    bina |= int(instruct[1][1])<<9
    bina |= int(instruct[2][1])<<6
    if instruct[3][0] != 'R':
        bina |= 1<<5
        bina |= moveSign(parseNum(instruct[3]), 5)&0b11111
    else: 
        bina |= int(instruct[3][1])
    return bina

def andOp (instruct):
    bina = 0b0101000000000000
    bina |= int(instruct[1][1])<<9
    bina |= int(instruct[2][1])<<6
    if instruct[3][0] != 'R':
        bina |= 1<<5
        bina |= moveSign(parseNum(instruct[3]), 5)&0b11111
    else: 
        bina |= int(instruct[3][1])
    return bina

def brOp (instruct):
    bina = 0b0000000000000000
    if 'n' in instruct[0]:
        bina |= 1<<11
    if 'z' in instruct[0]:
        bina |= 1<<10
    if 'p' in instruct[0]:
        bina |= 1<<9
    if instruct[1] not in symTable:
        print('[LC3asm.py] Undeclared label in branch.')
        return -1
    else:
        bina|=moveSign(symTable[instruct[1]] - pc, 9)&0b111111111
    return bina

def jmpOp (instruct):
    bina = 0b1100000000000000
    bina |= int(instruct[1][1])<<6
    return bina

def jsrOp (instruct):
    bina = 0b0100000000000000
    if instruct[1][0] != 'R':
        bina |= 1<<11
        if instruct[1] not in symTable:
            print('[LC3asm.py] Undeclared label in jsr.')
            return -1
        else:
            bina |= moveSign(symTable[instruct[1]] - pc, 11)&0b11111111111
    else:
        bina |= int(instruct[1][1])<<6
    return bina

def ldOp (instruct):
    bina = 0b0010000000000000
    bina |= int(instruct[1][1])<<9
    if instruct[2] not in symTable:
        print('[LC3asm.py] Undeclared label in ld.')
        return -1
    else:
        bina |= moveSign(symTable[instruct[2]] - pc, 9)&0b111111111
    return bina

def ldiOp (instruct):
    bina = 0b1010000000000000
    bina |= int(instruct[1][1])<<9
    if instruct[2] not in symTable:
        print('[LC3asm.py] Undeclared label in ld.')
        return -1
    else:
        bina |= moveSign(symTable[instruct[2]] - pc, 9)&0b111111111
    return bina

def ldrOp (instruct):
    bina = 0b0110000000000000
    bina |= int(instruct[1][1])<<9
    bina |= int(instruct[2][1])<<6
    bina |= moveSign(parseNum(instruct[3]), 6)&0b111111
    return bina

def leaOp (instruct):
    bina = 0b1110000000000000
    bina |= int(instruct[1][1])<<9

    bina |= moveSign(symTable[instruct[2]] - pc, 9)&0b111111111
    return bina

def notOp (instruct):
    bina = 0b1001000000111111
    bina |= int(instruct[1][1])<<9
    bina |= int(instruct[2][1])<<6
    return bina

def retOp (instruct):
    return 0b1100000111000000

def rtiOp (instruct):
    return 0b1000000000000000

def stOp (instruct):
    bina = 0b0011000000000000
    bina |= int(instruct[1][1])<<9
    if instruct[2] not in symTable:
        print('[LC3asm.py] Undeclared label in st.')
        return -1
    else:
        bina |= moveSign(symTable[instruct[2]] - pc, 9)&0b111111111
    return bina

def stiOp (instruct):
    bina = 0b1011000000000000
    bina |= int(instruct[1][1])<<9
    if instruct[2] not in symTable:
        print('[LC3asm.py] Undeclared label in st.')
        return -1
    else:
        bina |= moveSign(symTable[instruct[2]] - pc, 9)&0b111111111
    return bina

def strOp (instruct):
    bina = 0b0111000000000000
    bina |= int(instruct[1][1])<<9
    bina |= int(instruct[2][1])<<6
    bina |= moveSign(parseNum(instruct[3]), 6)&0b111111
    return bina

def trapOp (instruct):
    bina = 0b1111000000000000
    bina |= parseNum(instruct[1])&0b11111111
    return bina

op_codes = {
    'add':addOp,
    'and':andOp,
    'br':brOp,
    'jmp':jmpOp,
    'jsr':jsrOp,
    'jsrr':jsrOp,
    'ld': ldOp,
    'ldi':ldiOp,
    'ldr':ldrOp,
    'lea':leaOp,
    'not':notOp,
    'ret':retOp,
    'rti':rtiOp,
    'st':stOp,
    'sti':stiOp,
    'str':strOp,
    'trap':trapOp
}

psuedo_ops = {
    '.orig' : origPsOp,
    '.end' : (lambda x: None),
    '.stringz' : stringzOp,
    '.fill' : fillPsOp,
    '.blkw' : blkwPsOp,
    'getc' : trapPsOp,
    'out' : trapPsOp,
    'puts' : trapPsOp,
    'in' : trapPsOp,
    'halt' : trapPsOp
}

trapPs_ops = {
    'getc' :0x20,
    'out'  :0x21,
    'puts' :0x22,
    'in'   :0x23,
    'halt' :0x25
}

def loadFile(path):
    global file, currentPath
    currentPath = path.partition('.')[0]
    f = open(path, "r")
    f = f.read()
    file = f.splitlines()

def firstPass():
    global pc, out, symTable
    for l in file:
        instruct = l.partition(';')[0]
        instruct = instruct.split(',')
        instruct = instruct[0].split(' ') + instruct[1:]
        instruct = [c.strip('\t ') for c in instruct if c not in ['', ' ', '\t', '\n']]
        if len(instruct) == 0:
            continue

        if instruct[0][-1:] == ':':
            if len(instruct[0]) <= 20:
                #label
                symTable[instruct[0][:-1]] = pc
                print("[LC3asm.py] Label " + instruct[0][:-1] + " defined at " + str(hex(pc)))
                instruct = instruct[1:]
                if len(instruct) == 0:
                    continue
            else:
                print("[LC3asm.py] Label " + instruct[0][:-1] + " at " + str(hex(pc)) + " invalid.")
                return -1
            
        if instruct[0].lower() not in op_codes:
            if instruct[0].lower() not in psuedo_ops:
                if instruct[0][:2].lower() == 'br':
                    pc+=1 
                    continue
                return -1
            else:
                if instruct[0].lower() == '.stringz':
                    psuedo_ops[instruct[0].lower()]('"'+l.partition(';')[0].partition('"')[2].rstrip())
                else:
                    psuedo_ops[instruct[0].lower()](instruct)
        else:
            pc+=1 

    out = {}
    pc = np.uint16(0)


def secondPass():
    global pc

    lstFile = open(currentPath+".lst", 'w')
    lstFile.write("PC\t\tHEX\t\tSOURCE\n")
    for l in file:
        instruct = l.partition(';')[0]
        instruct = instruct.split(',')
        instruct = instruct[0].split(' ') + instruct[1:]
        instruct = [c.strip('\t ') for c in instruct if c not in ['', ' ', '\t', '\n']]
        if len(instruct) == 0:
            continue

        if instruct[0][-1:] == ':':
            if len(instruct[0]) <= 20:
                #label
                # symTable[instruct[0][:-1]] = pc
                # print("Label " + instruct[0][:-1] + " defined at " + str(hex(pc)))
                instruct = instruct[1:]
                if len(instruct) == 0:
                    continue
            # else:
            #     print("Label " + instruct[0][:-1] + " at " + str(hex(pc)) + " invalid.")
            #     return -1
            
        if instruct[0].lower() not in op_codes:
            if instruct[0].lower() not in psuedo_ops:
                if instruct[0][:2].lower() == 'br':
                    pc+=1 
                    out[pc-1] = op_codes['br'](instruct)
                    continue
                print("[LC3asm.py] Invalid operands " + l + " at " + str(hex(pc)))
                return -1
            else:
                if instruct[0].lower() == '.stringz':
                    psuedo_ops[instruct[0].lower()]('"'+l.partition(';')[0].partition('"')[2].rstrip())
                else:
                    psuedo_ops[instruct[0].lower()](instruct)
        else:
            pc+=1 
            out[pc-1] = op_codes[instruct[0].lower()](instruct)
        if pc-1 in out:
            lstFile.write(format(pc-1, '#06X')[2:] + "\t" + format(out[pc-1], '#06X')[2:] + "\t" + l + "\n")
        else:
            lstFile.write("\t\t\t\t" + l + "\n")


def asm():
    print("[LC3asm.py] Pass #1 failed.") if firstPass() == -1 else print("[LC3asm.py] Pass #1 complete.")
    print("[LC3asm.py] Pass #2 failed.") if secondPass() == -1 else print("[LC3asm.py] Pass #2 complete.")

def printOut():
    for k,l  in out.items():                  
        print(str(hex(k)) + " : b" + format(l, '016b') + " x" + format(l, '#06X')[2:])