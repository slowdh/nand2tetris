// Implement flip.

// temp = R1
// R1 = R0
// R0 = temp

@R1
D=M
@temp
M=D

@R0
D=M
@R1
M=D

@temp
D=M
@R0
M=D

(END)
@END
0;JMP