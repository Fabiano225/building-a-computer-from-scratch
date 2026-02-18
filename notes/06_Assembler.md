# Nand2Tetris: Project 6 – The Assembler

This project marks the final step in the software-to-hardware bridge. We develop a **Symbolic Assembler** that translates Hack assembly language (`.asm`) into binary machine code (`.hack`). This is the first software tool in the stack that allows us to move away from manually writing bits and toward human-readable programming.

## 1. The Translation Strategy: The Two-Pass Approach
The primary challenge of an assembler is resolving **Forward References** (using a label before it is defined). To handle this efficiently, we implement a two-pass logic.

### Pass 1: Label Discovery
* **Goal:** Map all label symbols (e.g., `(LOOP)`) to their corresponding ROM addresses.
* **Logic:** We traverse the code and maintain a `ROM_address` counter.
    * Every A-instruction or C-instruction increments the counter.
    * Every Label-instruction `(Xxx)` is added to the symbol table with the current counter value, but **does not** increment the counter itself.



### Pass 2: Binary Generation
* **Goal:** Produce the final 16-bit binary instructions.
* **Logic:** We traverse the code again, ignoring labels, and translate each line:
    * **Symbols:** Replace with their numeric values from the symbol table.
    * **Mnemonics:** Replace with their bit-field equivalents.

---

## 2. Instruction Decoding
The Hack architecture defines two instruction formats, distinguished by the most significant bit (MSB).

### The A-Instruction (`0vvvvvvvvvvvvvvv`)
* **Format:** `@value`
* **Function:** Sets the A-register to a 15-bit constant.
* **Translation:** If the value is a symbol, look it up in the table. Convert the final integer to a 15-bit binary string prefixed with `0`.

### The C-Instruction (`111accccccdddjjj`)
The most complex part of the assembler. It maps the syntax `dest=comp;jump` into specific bit-fields:



* **Comp (`a + c1..c6`):** The 7-bit code representing the ALU operation.
* **Dest (`d1, d2, d3`):** The 3-bit code determining where to store the result.
* **Jump (`j1, j2, j3`):** The 3-bit code for the branching condition.

---

## 3. Symbol Management
The Assembler maintains a **Symbol Table** to manage three distinct types of symbols:

### Predefined Symbols
The Hack specification reserves specific names for I/O and virtual registers:
* `R0`-`R15`: RAM addresses 0-15.
* `SCREEN`: 16384, `KBD`: 24576.
* `SP`, `LCL`, `ARG`, `THIS`, `THAT`: RAM addresses 0-4.

### Labels
Created via the `(Xxx)` syntax. These represent **ROM addresses** (points in the code) and are used for jumping.

### Variables
Any symbol encountered that is neither predefined nor a label is treated as a variable.
* **Allocation:** Variables are automatically assigned to the RAM starting at address **16**.
* **Pointer:** The assembler tracks the next available RAM slot (`next_var_address++`) as new variables are discovered.



---

## 4. Key Implementation Patterns (Python/Java)

### String Parsing & Cleaning
To ensure the assembler doesn't crash on comments or whitespace, we use a robust cleaning pipeline:
1. **Comment Removal:** `line.split("//")[0]`
2. **Whitespace Trimming:** `.strip()`
3. **Empty Line Guard:** Skip lines that are empty after cleaning.

### Component Extraction
For C-instructions, we utilize a "split-and-check" logic to handle optional fields:
```python
# Example logic
if "=" in line:
    dest_part, rest = line.split("=")
else:
    dest_part, rest = "null", line

if ";" in rest:
    comp_part, jump_part = rest.split(";")
else:
    comp_part, jump_part = rest, "null"
```

## 5. Output Requirements
* **File Naming:** The output file must have the same base name as the input, but with a `.hack` extension (e.g., `Prog.asm` -> `Prog.hack`).
* **Line Termination**: Each 16-bit instruction must be on a new line.
* **EOF Handling:** To match official comparison files, ensure the last line does not contain a trailing newline character.

```python
# Best practice:
with open(output_file, "w") as f:
    f.write("\n".join(binary_instructions))
```