#Written by Joseph Long 


import numpy as np
import lc3asm

#2^16 16bit memory address's
memory = np.uint16([0]*0xFFFF)
#registers
reg = np.uint16([0]*8)
pc = np.int16(0x0200)
psr = 0xFFFC
halt = True
#special memory ptrs
kbsr_ptr = 0xFE00
kbdr_ptr = 0xFE02
dsr_ptr = 0xFE04
ddr_ptr = 0xFE06
mcr_ptr = 0xFFFE

#from stackoverflow
#   https://stackoverflow.com/questions/32030412/twos-complement-sign-extension-python/32031543
def sign_extend(value, bits):
    sign_bit = 1 << (bits - 1)
    return (value & (sign_bit - 1)) - (value & sign_bit)

def logSign(num):
    n = sign_extend(num, 16)
    memory[psr]&=0b1111111111111000

    if n == 0:
        memory[psr]|=0b10
    elif n < 0:
        memory[psr]|=0b100
    elif n > 0:
        memory[psr]|=0b1

def getSign():
    if (memory[psr]&0b100)>>2 == 0b1:
        return -1
    elif (memory[psr]&0b10)>>1 == 0b1:
        return 0
    elif memory[psr]&0b1 == 0b1:
        return 1

def addOp(instruct):
    ans = reg[(instruct>>6)&0b111]
    if (instruct>>5)&0b1 == 0b0:
        ans+=reg[instruct&0b111]
    else:
        ans+=sign_extend(instruct&0b11111, 5)
    logSign(ans)
    reg[(instruct>>9)&0b111] = ans

def andOp(instruct):
    ans = reg[(instruct>>6)&0b111]
    if (instruct>>5)&0b1 == 0b0:
        ans&=reg[instruct&0b111]
    else:
        ans&=sign_extend(instruct&0b11111, 5)
    logSign(ans)
    reg[(instruct>>9)&0b111] = ans

def brOp(instruct):
    global pc
    if (instruct >> 11) & 0b1 == 0b1 and getSign() == -1:
        pc+=sign_extend(instruct&0b111111111, 9)
        return
    elif (instruct >> 10) & 0b1 == 0b1 and getSign() == 0:
        pc+=sign_extend(instruct&0b111111111, 9)
        return
    elif (instruct >> 9) & 0b1 == 0b1 and getSign() == 1:
        pc+=sign_extend(instruct&0b111111111, 9)


def jmpOp(instruct):
    pc = reg[(instruct>>6)&0b111]

def jsrOp(instruct):
    reg[7] = pc
    if (instruct>>11)&0b1 == 0b1:
        pc = sign_extend(instruct&0b11111111111, 11)+pc
    else:
        pc = reg[(instruct>>6)&0b111]

def ldOp(instruct):
    ans = memory[sign_extend(instruct&0b111111111, 9) + pc]
    logSign(ans)
    reg[(instruct>>9)&0b111] = ans

def ldiOp(instruct):
    ad = memory[sign_extend(instruct&0b111111111, 9) + pc]
    ans = memory[ad]
    logSign(ans)
    reg[(instruct>>9)&0b111] = ans

def ldrOp(instruct):
    ans = memory[sign_extend(instruct&0b111111, 6) + reg[(instruct>>6)&0b111]]
    logSign(ans)
    reg[(instruct>>9)&0b111] = ans

def leaOp(instruct):
    ans = pc+sign_extend(instruct&0b111111111, 9)
    logSign(ans)
    reg[(instruct>>9)&0b111] = ans

def notOp(instruct):
    ans = ~reg[(instruct>>6)&0b111]
    logSign(ans)
    reg[(instruct>>9)&0b111] = ans

def retOp(instruct):
    pc = reg[7]

def rtiOp(instruct):
    pass

def stOp(instruct):
    ans = reg[(instruct>>9)&0b111]
    memory[sign_extend(instruct&0b111111111, 9) + pc] = ans

def stiOp(instruct):
    ad = memory[sign_extend(instruct&0b111111111, 9) + pc]
    memory[ad] = reg[(instruct>>9)&0b111]

def strOp(instruct):
    memory[sign_extend(instruct&0b111111, 6) + reg[(instruct>>6)&0b111]] = reg[(instruct>>9)&0b111]

def trapOp(instruct):
    global halt
    if instruct&0b11111111 == 0x21:
        print(chr(reg[0]), end='')
    if instruct&0b11111111 == 0x25:
        halt = True
    if instruct&0b11111111 == 0x22:
        ptr = reg[0]
        str = ''
        while memory[ptr] != 0:
            str += chr(memory[ptr])
            ptr+=1
        str = bytes(str, "utf-8").decode("unicode_escape")
        print(str)

op_codes = {
    0b0001: addOp,
    0b0101: andOp,
    0b0000: brOp,
    0b1100: jmpOp,
    0b0100: jsrOp,
    0b0010: ldOp,
    0b1010: ldiOp,
    0b0110: ldrOp,
    0b1110: leaOp,
    0b1001: notOp,
    0b1100: retOp,
    0b1000: rtiOp,
    0b0011: stOp,
    0b1011: stiOp,
    0b0111: strOp,
    0b1111: trapOp
}

def parse(instruct, debug):
    op_code = (instruct >> 12) & 0b1111
    if op_code in op_codes:
        if debug:
            print(op_codes[op_code])
        op_codes[op_code](instruct)
    else:
        print("NOP")

def loadIn():
    for ad, bina in lc3asm.out.items():
        memory[ad] = bina

def run(debug = True):
    global pc, halt
    halt = False
    while not halt:
        c = input("\n>") if debug else ''
        if c == "r":
            for i in range(0, 8):
                print("R" + str(i) + ":  \t" + hex(reg[i]))
            print('PSR:\t' + bin(memory[psr]))
            print('PC: \t' + hex(pc))
        elif c == "p":
            return
        pc+=1
        if debug: 
            print(hex(pc))
        parse(memory[pc-1], debug)

lc3asm.loadFile("OS_vector_tables.asm")
lc3asm.asm()
loadIn()
pc = np.int16(0x200)
run(debug = False)
pc = np.int16(0x3000)