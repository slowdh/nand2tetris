// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Fill.asm

// Runs an infinite loop that listens to the keyboard input.
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel;
// the screen should remain fully black as long as the key is pressed. 
// When no key is pressed, the program clears the screen, i.e. writes
// "white" in every pixel;
// the screen should remain fully clear as long as no key is pressed.

// Put your code here.

// if RAM[Keyboard] == 0
//    jump to WHITE
      
// else
//    for register in ScreenRam
//        register = -1

// WHITE
// for register in ScreenRam
//     register = 0

@24576
D=A
@keyboard
M=D
@16384
D=A
@screen
M=D
@8191
D=A
@screenlen
M=D

(LOOP)
@keyboard
A=M
D=M
@WHITE
D;JEQ

(BLACK)
@i
M=0
(BFILL)
@i
D=M
@screenlen
D=D-M
@LOOP
D;JGT

@screen
D=M
@i
A=D+M
M=-1
@i
M=M+1
@BFILL
0;JMP

(WHITE)
@i
M=0
(WFILL)
@i
D=M
@screenlen
D=D-M
@LOOP
D;JGT

@screen
D=M
@i
A=D+M
M=0
@i
M=M+1
@WFILL
0;JMP

