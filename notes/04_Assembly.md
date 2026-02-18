# Nand2Tetris: Project 4 – Machine Language (ASM)

This project marks the transition from hardware architecture to software control. We use the **Hack Machine Language** to directly manipulate the CPU, RAM, and peripheral devices like the Screen and Keyboard.

## 1. Instruction Set Architecture (ISA)
The Hack computer uses two types of 16-bit instructions:

### The A-Instruction (Address)
* **Syntax:** `@value` (where value is a non-negative constant or a symbol).
* **Function:** Sets the **A-register** to the specified value.
* **Usage:** * Loading constants (`@5`, `D=A`).
    * Selecting a RAM address for subsequent operations (`@R0`, `M=D`).
    * Declaring jump targets (`@LOOP`, `0;JMP`).

### The C-Instruction (Compute)
* **Syntax:** `dest = comp ; jump`
* **Function:** The core of the CPU. It performs a calculation, stores the result, and optionally jumps to a new instruction address.
* **The 'M' Register:** When `M` is used in a C-instruction, it refers to the memory location currently addressed by the A-register (`RAM[A]`).

---

## 2. Memory-Mapped I/O
Interaction with the outside world is handled via specific memory ranges:

* **RAM[0-15]:** Virtual registers (`R0`–`R15`).
* **Screen (RAM[16384-24575]):** A 256x512 pixel map. Each bit represents one pixel (1 = black, 0 = white).
* **Keyboard (RAM[24576]):** Stores the ASCII code of the key currently being pressed. It holds `0` if no key is active.



---

## 3. Program Flow & Logic Control
Assembler code is executed linearly. To implement `IF` or `WHILE` logic, we use Labels and Jumps.

### Labels
Labels like `(LOOP)` or `(END)` are pseudo-instructions. They don't take up memory but tell the Assembler: "Remember this instruction's address for future jumps."

### Conditional Jumps
Jumps are always evaluated against the value in the **D-register** or the result of a `comp` operation:
* `D;JGT`: Jump if $D > 0$.
* `D;JEQ`: Jump if $D = 0$.
* `D;JLT`: Jump if $D < 0$.

---

## 4. Key Implementation Patterns

### Pointer Manipulation
To traverse an array or the screen memory, we use **Pointers**. We store the starting address in a variable and increment it.

```
@SCREEN
D=A
@addr
M=D      // Store the base address of the screen in 'addr'

@addr
A=M      // Set A to the value stored in 'addr'
M=-1     // RAM[addr] = black
```

### The Refresh Cycle (The "Fill" Pattern)
For interactive programs (like `Fill.asm`), the code follows a three-step cycle:

1. **Poll Input:** Check `@KBD` to determine the state.

2. **Initialize/Reset:** Set the loop counter (`i = 8192`) and the screen pointer (`addr = 16384`) for the next frame.

3. **Inner Loop:** Iterate through every screen register to apply the color.

## 5. Multiplication (Mult.asm)

Since the Hack ALU does not have a built-in multiplication unit, we implement it through Iterative Addition.
* To calculate $R0 \times R1$, we add $R0$ to itself $R1$ times.
* Efficiency: To handle the case where $R1 = 0$, the loop condition should check for completion at the very beginning (pre-test loop).