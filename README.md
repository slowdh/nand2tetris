# nand2tetris
Build computer from bunch of Nand gates.

I followed "From Nand to Tetris" (https://www.nand2tetris.org/) course. 


## 01_basic_gates
#### Build basic gates from Nand gates.

These gates would be basic building blocks for building even complex chips.

- What is implemented: 

  - [And, And16, DMux, DMux4Way, DMux8Way, Mux, Mux4Way16, Mux8Way16, Mux16, Not, Not16, Or, Or8Way, Or16, Xor]

  
## 02_ALU
#### Build ALU: Basic arithmatic, logic operation become possible. And that is enough.

- What is ALU?
  - ALU is  chip (or circuit) which does bunch of Arithmatic & Logic operations.
  - What / how many operations ALU support is a trade off between efficiency + performance. What is not implemented on hardware side can be implemented on software side. (as multiply can be implemented with multiple additions.)


- Implementation
  - It receives inputs as x, y, operation bits and outputs computed output with zero bit (is output zero), negative bit (is output negative).
  - We aim to perform following 18 operations: 
    - [0, 1, -1, x, y, !x, !y, -x, -y, x + 1, y + 1, x - 1, y - 1, x + y, y - x, x & y, x | y]
  - Of course we can implement above operations separately, but if we take a close look, we can logically group components together, thus making ALU much lighter.
  - So, what is actually implemented are these six operations:
    - [zx, nx, zy, ny, f, no]
    - zx: if zx, then x = 0
    - nx: if nx, then x = !x
    - zy: if zy, then y = 0
    - ny: if ny, then y = !y
    - f: if f, then out = x + y, else out = x & y
    - no: if no, then out = !out
  - If we cleverly combine these six operations, all 18 operations above can be made!
  

## 03_RAM_PC
#### Build memory: Now, we are able to store data.
#### Build PC: Count, repeat, and reset. Makes working in more efficient way.

 - From register to RAM
   - Assume we have DFF as a basic building block. 
     - Four nand gates can make SR Latch, which is primitive 1 bit memory cell.
     - Two SR Latch + Clock input can make DFF, which can memorize the input for one clock.
   - We can make 1 bit memory from DFF quite easily.
   - 1 bit memory parallely scales up 16 bit Register.
   - Register -> RAM 8 -> RAM 64 -> ... -> RAM 4K Scales up in a same fashion.
   
 
 - PC
   - It is basically incremental counter, being able to reset status and receive initial number.
   - Quite different from RAM logic, it is about continuous if-else logic.
   - if-else logic can be implemented with Mux chip.
   - Now we can count, track status from set of instructions!


## 04_Low_level_programming
#### Low level programming: programming dealing with hardwares.


- What is low level programming? (or Assembly language?)
  - It is low level in a sense that it directly deals with hardware components inside computer.
  - For example, we should specifically tell like put this data into that register or add this register value with other register value.
  - In most cases, one low level operation can be directly translated to one specific hardware operation.


- How to deal with basic functionality: Variable, Branching, Loop
  - Variable is a symbol to specific RAM address. Variable is a mapping from address to readable name. Assembler deals with this.
  - Branching is implemented with JMP instruction. Program Counter(PC) holds what address of instructions to run next time. By changing the value inside PC, we can change the flow of running instructions.
  - Loop is a special case of branching, with counting.


## 05_Computer
#### Computer = CPU + RAM 


- What is computer?
  - Computer at most basic is CPU + RAM.
  - With RAM, we can store data with instructions.
  - With CPU, we can manipulate on data.


- What is CPU?
  - CPU is composed of ALU, PC, several Registers (in here we have two).
  - CPU receives instruction + data from RAM, and compute the data, store data back to RAM (which needs ram address, data).
  - It also cares about what operation to run next time, PC.
  - When operation tell to Jump, PC changes the state and jump to 'address' (A register value) next time.


- What is RAM?
  - It is basically bunch of registers.
  - When instruction and data is stored at the same RAM (Unlike Harvard architecture), it should follow fetch-execution cycle.
  - If using memory mapped I/O, some part of RAM is used for I/O devices. (like screen, mouse, keyboard)


## 06_Assembler
#### From low level language to machine language.

- What are important things to know when building assembler?

  1. File I/O. 
     1. Read line by line and translate.
  2. Deal with symbols 
     1. Label for flow control, Variables for convenience.
  3. Parse input
     1. Ignore white spaces, comments.
     2. Break into meaningful chunk.
  4. Translate
     1. Code mapping (follow rules).


## 07-08_VM_Translator
#### Virtual Machine Language is a middle ground in between high level language and machine language.

- What is Virtual Machine?
  - Virtual Machine is a virtual computer, which has own systems of RAM and CPU Instruction set.
  - Why it is need then?
    - Actual CPUs (different computer) can have various instruction set according to manufacturing company / generation.
    - So, say we have some abstraction of individual computers, we can deal with high level codes more effectively when compiling.
  - It might be cool if abstraction level is not so low that we don't have to deal with nitty-gritty details and not so high that actual implementation part isn't too much of a work.
  - Here, we regard (efficient middle ground) VM as Stack Machine, which abstracts every possible operation into series of Stack operations.


- Stack Machine as a VM.
  - Operations are done on top of Stack.
    - [add, sub, neg, eq, gt, lt, and, or, not]
    - SP (Stack Pointer) takes care of operation sequence.

    
  - Accessing memory is done with Push / Pop commands to Stack.
    - Virtual memory consists of 8 segments.
      - local, argument, this, that, constant, static, temp, pointer.
      - Why divided like this?
        - local, static are for variable scope. (i.e. local, global variable)
        - pointer, this and that is for referencing current processing object / array

  
  - Function declaration, call, return
    - Handling function definition.
      - Makes a subroutine label. When function is called, jump to the declared function label and get the function code run.
      - Push local variable placeholder. (or move stack pointer)
      
    - Handling function call.
      - Save current status include [return address, LCL, ARG, THIS, THAT]
      - Jump to function label

    - Handling return.
      - Retrieve saved pointers.
      - Set return value to the right place on stack.
      - Jump to original code.
