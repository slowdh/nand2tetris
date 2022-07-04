// Compute 1 + 2 + ... + n
// RAM[1] = 1 + 2 + ... + n
// n = RAM[0]

// i = 1
// n = RAM[0]
// sum = 0

// (LOOP)
// if i > n:
//     jump to (STOP)
// sum = sum + i
// i = i + 1
// jump to LOOP


// (STOP)
// RAM[1] = sum
// (END)


@i
M=1

@R0
D=M
@n
M=D

@sum
M=0

(LOOP)
@i
D=M
@n
D=D-M
@STOP
D;JGT
@i
D=M
@sum
M=D+M
@i
M=M+1
@LOOP
0;JMP

(STOP)
@sum
D=M
@R1
M=D

(END)
@END
0;JMP





