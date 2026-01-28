# Nand2Tetris: Part 3 – Sequential Logic & Memory (RAM)

This project moves from static logic to **state**. It introduces the concept of time (the Clock) and explains how a computer remembers information using Flip-Flops and Registers.

## 1. The Foundation: DFF & Registers
Unlike logic gates, which react instantly, sequential chips "wait" for a clock tick.
* **DFF (Data Flip-Flop):** The atom of memory. It outputs the input from the *previous* time step: $out(t) = in(t-1)$.
* **Register:** A DFF combined with a **Mux**. 
    * If `load=1`, it stores a new value.
    * If `load=0`, it feeds its own output back into itself, "remembering" the value.
    * *HDL Concept:* `Mux(a=oldOut, b=in, sel=load, out=muxOut); DFF(in=muxOut, out=out, out=oldOut);`



---

## 2. Memory Hierarchy (The Matryoshka Principle)
RAM is built by nesting smaller units inside larger ones. Each level uses a **DMux** to distribute the `load` signal and a **Mux** to select the `out` signal.

### RAM8 (8 Registers)
* **Address (3-bit):** $2^3 = 8$ possible locations.
* **Logic:** Use `DMux8Way` to send the `load` bit to one specific register and `Mux8Way16` to pick which register's value to output.

### RAM64, RAM512, RAM4K
These follow a perfect "Power of 8" pattern.
* **RAM64:** Contains 8 RAM8 chips.
* **RAM512:** Contains 8 RAM64 chips.
* **RAM4K:** Contains 8 RAM512 chips.

---

## 3. Address Splitting: The "Which & Where" Logic
When addressing memory, we split the address bus into two functional parts:
* **The "Which" (High Bits):** Selects which sub-block (which RAM8 or RAM64) to activate.
* **The "Where" (Low Bits):** Is passed into that sub-block to find the exact register.

**Example: RAM64 (6-bit address `0..5`)**
* `address[3..5]`: Selects one of the 8 RAM8 blocks.
* `address[0..2]`: Selects the specific register inside that RAM8.



---

## 4. The RAM16K Exception
The pattern changes at 16K because $8 \times 4K$ would be 32K. Since we only want 16K, we only use **four** RAM4K blocks.
* **Address (14-bit):** $2^{14} = 16,384$.
* **The Split:**
    * `address[12..13]`: 2 bits to choose 1 of **4** RAM4K blocks (using `DMux4Way` / `Mux4Way16`).
    * `address[0..11]`: 12 bits to address the 4,096 registers inside the chosen RAM4K.
* **Warning:** Do **not** use `address[11..13]` with a `DMux8Way` here. Since you only have 14 bits, bit 11 must be part of the internal address for the RAM4K, not the block selector.

---

## 5. The Program Counter (PC)
The PC is a register with a "decision tree" in front of it. It handles four operations in a specific order of importance (Priority):

1. **Reset (Highest):** If `reset=1`, output becomes `0`.
2. **Load:** If `load=1`, it jumps to a new address (`in`).
3. **Inc:** If `inc=1`, it increments the current value (`out + 1`).
4. **Keep (Lowest):** If no pins are active, it maintains the current value.

### HDL Implementation Trick
We use a chain of `Mux16` gates. The **Reset** Mux must be the *last* one before the Register to ensure it can override everything else.

```
// Logic Flow: Inc -> Load -> Reset -> Register
Inc16(in=feedback, out=pcPlus1);
Mux16(a=feedback, b=pcPlus1, sel=inc, out=o1);
Mux16(a=o1, b=in, sel=load, out=o2);
Mux16(a=o2, b=false, sel=reset, out=finalIn);
Register(in=finalIn, load=true, out=out, out=feedback);
```

## 6. Pro-Tips for Sequential HDL
* Implicit Clock: The clock is built into the DFF and Register. State updates only happen at the end of a time step.

* Load=True: In the PC, the Register always has load=true because the Muxes already decided whether the value should change or "stay" (by feeding back the old value).