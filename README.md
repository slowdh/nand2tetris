# nand2tetris
Build computer from bunch of Nand gates.

I followed "From Nand to Tetris" (https://www.nand2tetris.org/) course. 


## 01_basic_gates
#### Build basic gates from Nand gates.

These gates would be basic building blocks for building even complex chips.

- What is implemented: 

  - [And, And16, DMux, DMux4Way, DMux8Way, Mux, Mux4Way16, Mux8Way16, Mux16, Not, Not16, Or, Or8Way, Or16, Xor]

  
## 01_ALU
#### Build ALU: Now it starts do something useful.

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
  