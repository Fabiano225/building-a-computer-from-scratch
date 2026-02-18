// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/4/Fill.asm

// Runs an infinite loop that listens to the keyboard input. 
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel. When no key is pressed, 
// the screen should be cleared.

(LOOP_KEYBOARD)
    @KBD
    D=M
    @setWhite
    D;JEQ

    @color
    M=-1
    @RESET
    0;JMP

    (setWhite)
        @color
        M=0

    (RESET)
        @8192
        D=A
        @i
        M=D

        @SCREEN
        D=A
        @addr
        M=D

    (DRAW)
        @color
        D=M
        @addr
        A=M
        M=D
        @addr
        M=M+1

        @i
        M=M-1
        D=M

        @DRAW
        D;JGT
        
        @LOOP_KEYBOARD
        0;JMP