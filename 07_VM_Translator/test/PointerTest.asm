    @256
    D=A
    @SP
    M=D
    @300
    D=A
    @LCL
    M=D
    @400
    D=A
    @ARG
    M=D
    @3000
    D=A
    @THIS
    M=D
    @3010
    D=A
    @THAT
    M=D
    @3030  // push constant 3030
    D=A
    @SP
    A=M
    M=D
    @SP
    M=M+1
    @THIS  // pop pointer 0
    D=A
    @R13
    M=D
    @SP
    M=M-1
    @SP
    A=M
    D=M
    @R13
    A=M
    M=D
    @3040  // push constant 3040
    D=A
    @SP
    A=M
    M=D
    @SP
    M=M+1
    @THAT  // pop pointer 1
    D=A
    @R13
    M=D
    @SP
    M=M-1
    @SP
    A=M
    D=M
    @R13
    A=M
    M=D
    @32  // push constant 32
    D=A
    @SP
    A=M
    M=D
    @SP
    M=M+1
    @2  // pop this 2
    D=A
    @THIS
    A=D+M
    D=A
    @R13
    M=D
    @SP
    M=M-1
    @SP
    A=M
    D=M
    @R13
    A=M
    M=D
    @46  // push constant 46
    D=A
    @SP
    A=M
    M=D
    @SP
    M=M+1
    @6  // pop that 6
    D=A
    @THAT
    A=D+M
    D=A
    @R13
    M=D
    @SP
    M=M-1
    @SP
    A=M
    D=M
    @R13
    A=M
    M=D
    @THIS  // push pointer 0
    D=M
    @SP
    A=M
    M=D
    @SP
    M=M+1
    @THAT  // push pointer 1
    D=M
    @SP
    A=M
    M=D
    @SP
    M=M+1
    @SP  // add
    M=M-1
    @SP
    A=M
    D=M
    @SP
    M=M-1
    @SP
    A=M
    A=M
    D=D+A
    @SP
    A=M
    M=D
    @SP
    M=M+1
    @2  // push this 2
    D=A
    @THIS
    A=D+M
    D=M
    @SP
    A=M
    M=D
    @SP
    M=M+1
    @SP  // sub
    M=M-1
    @SP
    A=M
    D=M
    @SP
    M=M-1
    @SP
    A=M
    A=M
    D=A-D
    @SP
    A=M
    M=D
    @SP
    M=M+1
    @6  // push that 6
    D=A
    @THAT
    A=D+M
    D=M
    @SP
    A=M
    M=D
    @SP
    M=M+1
    @SP  // add
    M=M-1
    @SP
    A=M
    D=M
    @SP
    M=M-1
    @SP
    A=M
    A=M
    D=D+A
    @SP
    A=M
    M=D
    @SP
    M=M+1
