# j-LC3
A WIP LC3 assembler/emulator, for educational purposes

Written as an exercise to get me ready for the Fall 2020 semester as unbsj.

## Notes

**This is not complete.** You **will** experience bugs, and you **will** have a better experience using something else as of now. I suggest wchargin's online tool. 

Requires Numpy.

It is recomended at this point in development to run this in the Python interperiter directly, by opening python and using "import lc3", as this allows you to pause the running lc3 program and futher inspect the machines memory and registers when running in debug mode.

A copy of the lc3 operating system is included, and is now supported by the emulator. Emulator is now dependant on the os for all TRAP calls.

## Assembly

To use, first use "lc3.lc3asm.loadFile( *path* )" to load in an assembly source file, then use "lc3.lc3asm.asm()" to assemble the file.

## Emulating

To run the code, use "lc3.loadIn()", then set lc3.pc to the *.orig* of your program, and then use "lc3.run()".

If lc3.run is ran with the param debug=True ( lc3.run(debug=True) ), the program can be stepped through. After each step, the user can pause by entering 'p', read the registers by entering 'r', or inspect the stack with 'ss'.
