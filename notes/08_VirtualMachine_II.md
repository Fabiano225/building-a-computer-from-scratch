# Nand2Tetris: Project 8 – Virtual Machine II: Program Control

This project completes the VM Translator (the compiler's backend) by adding control flow capabilities. We implement branching (loops and conditionals), the function call-and-return protocol, and the ability to compile entire directories of `.vm` files into a single Hack program.

## 1. Branching Commands (Control Flow)
Branching allows the program to jump to different parts of the code instead of executing linearly. To prevent naming collisions between different functions, a good convention is to format labels as `FunctionName$labelName`.

* **`label symbol`:** Marks a destination in the VM code. 
  * *Translation:* A standard Hack assembly label: `(FunctionName$symbol)`.
* **`goto symbol`:** An unconditional jump. 
  * *Translation:* `@FunctionName$symbol` followed by `0;JMP`.
* **`if-goto symbol`:** A conditional jump. 
  * *Action:* Pops the topmost value off the stack. If the value is **not zero** (True), it jumps to the label. Otherwise, it continues to the next line.
  * *Translation:* Pop to `D`, then `@FunctionName$symbol` followed by `D;JNE` (Jump if Not Equal to 0).

---

## 2. Function Commands & The Call Stack
This is the heart of the VM. When a function calls another function, the caller must freeze its current state, let the callee run, and then resume exactly where it left off.



### The Anatomy of a Stack Frame
When a function is called, a "Frame" is pushed to the stack. It consists of:
1. The arguments passed to the function.
2. The saved state of the caller (Return Address, LCL, ARG, THIS, THAT).
3. The local variables of the called function.
4. The working stack for the called function's calculations.

### `function functionName nVars`
* **Action:** Declares a function and initializes its local variables.
* **Logic:** 1. Create a label `(functionName)`. 
  2. Run a loop that pushes `0` onto the stack `nVars` times to initialize the local variables.

### `call functionName nArgs`
* **Action:** Calls a function, passing `nArgs` arguments that have already been pushed to the stack.
* **Logic (The Caller's Setup):** 1. Push a unique `return-address` label to the stack.
  2. Push the current values of `LCL`, `ARG`, `THIS`, and `THAT` to save the caller's state.
  3. Reposition `ARG` for the callee: `ARG = SP - nArgs - 5`.
  4. Reposition `LCL` for the callee: `LCL = SP`.
  5. Jump to `functionName` (`goto functionName`).
  6. Inject the `(return-address)` label right here.

### `return`
* **Action:** Ends the current function, moves the return value to the caller, and restores the caller's state.
* **Logic (The Callee's Teardown):**
  1. Save the `FRAME` (the current `LCL` value) in a temporary variable (e.g., `@R14`).
  2. Read the `RET` address (located at `FRAME - 5`) and save it in a temporary variable (e.g., `@R15`).
  3. Pop the topmost value (the function's result) and store it at `*ARG` (overwriting the first argument).
  4. Reposition `SP` to point right after the return value: `SP = ARG + 1`.
  5. Restore `THAT`, `THIS`, `ARG`, and `LCL` by reading backwards from the `FRAME` (`FRAME-1`, `FRAME-2`, etc.).
  6. Jump to the saved `RET` address.

---

## 3. Bootstrapping & Multi-File Compilation
In Project 8, programs often consist of multiple `.vm` files (e.g., `Main.vm`, `Sys.vm`, `Math.vm`). 

### Directory Translation
* The translator must accept a **directory** as input, not just a single file.
* It must iterate through all `.vm` files in that directory and append their translated Hack assembly code into a single `.asm` output file.
* Static variables must be scoped to their file. `@Filename.index` ensures that `static 0` in `Main.vm` doesn't overwrite `static 0` in `Math.vm`.

### The Bootstrap Code (Sys.init)
Before any VM code can run, the computer must be initialized. When compiling a directory, the translator must inject this startup code at the very top of the `.asm` file:
1. Set `SP` to `256` (`@256`, `D=A`, `@SP`, `M=D`).
2. Call `Sys.init` (using the standard `call` protocol with 0 arguments). `Sys.init` is the OS function that eventually calls `Main.main`.