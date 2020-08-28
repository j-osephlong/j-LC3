.orig x3000
    LEA R0, MSG
    PUTS

    AND R0, R0, #0
    LOOP:
        AND R2, R2, #0
        ADD R2, R2, #-9
        ADD R0, R0, #1
        ADD R2, R2, R0
        BRn LOOP
    LD R1, ascii
    ADD R0, R0, R1
    OUT
    HALT

MSG: .stringz "Hello, \n\tthis is a test message.\n"
ascii: .fill x30
.END