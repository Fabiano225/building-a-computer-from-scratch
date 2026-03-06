# Nand2Tetris: Project 7 – Virtual Machine I: Stack Arithmetic

This project builds the first half of the Compiler's backend. We write a **VM Translator** that converts intermediate Virtual Machine (VM) code into Hack Assembly language. This allows high-level, object-oriented code to eventually run on our hardware.

## 1. The Stack Machine Concept
The Nand2Tetris VM is a stack-based machine. Instead of using named registers for calculations, it uses a Last-In-First-Out (LIFO) data structure.

* **Operands:** Numbers are "pushed" onto the top of the stack.
* **Operations:** Commands "pop" their required operands off the stack, compute the result, and "push" the result back onto the stack.
* **Stack Pointer (SP):** A predefined Hack register mapped to `RAM[0]`. It always points to the next available (empty) memory location at the top of the stack.

---

## 2. Arithmetic and Logical Commands
These commands manipulate the values currently sitting on top of the stack.

### Unary Operations (`neg`, `not`)
* **Action:** Modifies the single topmost value on the stack.
* **Hack Logic:** Go to `SP - 1`, flip its bits/sign, and leave it in place. The SP itself does not move.

### Binary Operations (`add`, `sub`, `and`, `or`)
* **Action:** Pops two values, applies the operation, and pushes the single result.
* **Hack Logic:** Decrement `SP` to get the second operand (`y`), decrement `SP` again to get the first operand (`x`). Compute `x op y`, store the result at the new top, and leave `SP` pointing just above it.

### Relational Operations (`eq`, `gt`, `lt`)
* **Action:** Compares the top two values. Returns **-1 (True)** or **0 (False)** to the stack.
* **Hack Logic:** Requires Hack assembly jump instructions (`JEQ`, `JGT`, `JLT`).
* **The Label Problem:** Since you might call `eq` multiple times, your translator must generate **unique assembly labels** (e.g., `TRUE_1`, `END_1`) for each comparison to prevent duplicate definitions.

---

## 3. Memory Segments
The VM language abstracts memory into virtual segments. The translator maps these to physical Hack RAM.

### Base Pointer Segments (`local`, `argument`, `this`, `that`)
These are dynamic. Their starting addresses change depending on which function is currently running.
* **LCL (RAM[1]):** Base address of the `local` segment.
* **ARG (RAM[2]):** Base address of the `argument` segment.
* **THIS (RAM[3]):** Base address of the `this` segment.
* **THAT (RAM[4]):** Base address of the `that` segment.
* **Access Logic:** Target RAM Address = Base Pointer Value + Index.

### Fixed Segments (`temp`, `pointer`)
Mapped directly to fixed RAM locations; they do not use base pointers.
* **temp:** Mapped to `RAM[5]` through `RAM[12]`. (Target Address = 5 + Index).
* **pointer:** Used to manually set the THIS/THAT bases. `pointer 0` maps to `RAM[3]` (THIS), `pointer 1` maps to `RAM[4]` (THAT).

### Special Segments (`constant`, `static`)
* **constant:** A purely virtual segment. `push constant i` pushes the literal number `i`. You cannot `pop` to a constant.
* **static:** Variables shared across the entire `.vm` file. Translated using Hack assembly variables formatted as `@Filename.i` (assigned to `RAM[16]`+).


# Nand2Tetris: Project 8 – Virtual Machine II: Program Control

This project completes the VM Translator by adding branching (loops/conditionals) and the function call-and-return protocol.

## 1. Branching Commands
Branching allows the program to jump to different parts of the code instead of executing linearly.

* **`label symbol`:** Marks a destination in the VM code. Translated simply as a Hack assembly label: `(Filename.symbol)`.
* **`goto symbol`:** An unconditional jump. Translated as `@Filename.symbol` followed by `0;JMP`.
* **`if-goto symbol`:** A conditional jump. It pops the topmost value off the stack. If the value is not zero (True), it jumps to the label. Otherwise, it continues to the next line.

---

## 2. Function Commands & The Call Stack
This is the most complex part of the VM. When a function calls another function, the caller must freeze its current state, let the callee run, and then resume exactly where it left off.



### `function functionName nVars`
* **Action:** Declares a function and initializes its local variables.
* **Hack Logic:** Create a label `(functionName)`. Then, run a loop that pushes `0` onto the stack `nVars` times to initialize the local variables.

### `call functionName nArgs`
* **Action:** Calls a function, passing `nArgs` arguments that have already been pushed to the stack.
* **Hack Logic (The Caller's Frame):** 1. Push a unique `return-address` label to the stack.
  2. Push the current values of `LCL`, `ARG`, `THIS`, and `THAT` to save the caller's state.
  3. Reposition `ARG` for the callee: `ARG = SP - nArgs - 5`.
  4. Reposition `LCL` for the callee: `LCL = SP`.
  5. Jump to `functionName` (`goto functionName`).
  6. Inject the `(return-address)` label right here.

### `return`
* **Action:** Ends the current function, moves the return value to the caller, and restores the caller's state.
* **Hack Logic (The Callee's Teardown):**
  1. Save the `FRAME` (the current `LCL` value) in a temporary variable (`@R14`).
  2. Read the `RET` address (located at `FRAME - 5`) and save it in a temporary variable (`@R15`).
  3. Pop the topmost value (the function's result) and store it at `*ARG` (overwriting the first argument).
  4. Reposition `SP` to point right after the return value: `SP = ARG + 1`.
  5. Restore `THAT`, `THIS`, `ARG`, and `LCL` by reading backwards from the `FRAME` (`FRAME-1`, `FRAME-2`, etc.).
  6. Jump to the saved `RET` address.

---

## 3. Bootstrapping
Before any VM code can run, the computer must be initialized. When the VM Translator targets an entire directory (not just one file), it must inject this code at the very beginning of the `.asm` file:
1. Set `SP` to `256` (`@256`, `D=A`, `@SP`, `M=D`).
2. Call `Sys.init` (the equivalent of `main()` in Nand2Tetris, using the standard `call` protocol).