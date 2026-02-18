# Nand2Tetris: Project 5 – The Hack Computer Architecture

This project is the culmination of the hardware track. We integrate the ALU, registers, and the Program Counter (PC) into a functional **Central Processing Unit (CPU)** and finally assemble the complete **Hack Computer**.

## 1. The CPU: Logic-to-Hardware Mapping
The core challenge of the CPU is realizing that the 16-bit instruction is not just data, but a set of **Control Bits (c-bits)** that act as physical switches for the hardware.

### Instruction Decoding & Data Paths
* **Instruction Mux (Left):** Decides if the A-register receives a constant from an A-instruction (`@value`) or the ALU's output from a C-instruction.
* **The 'a' bit (`instruction[12]`):** This bit acts as a selector for the ALU's secondary input.
    * `a=0`: ALU operates on the **A-register**.
    * `a=1`: ALU operates on **Memory (inM)**.
* **Destination Bits (`instruction[3..5]`):** These route the ALU output to the correct storage locations (`d1` -> A, `d2` -> D, `d3` -> M).



### Jump Logic: The Control Flow
The CPU decides the next instruction address by evaluating the ALU's status bits (`zr`, `ng`) against the instruction's jump bits (`j1, j2, j3`).
* **Positive Status:** Since the ALU only provides "zero" and "negative" flags, we must derive the "positive" flag: `pos = Not(zr Or ng)`.
* **C-Instruction Guard:** A jump must **only** occur if the current instruction is a C-instruction (`instruction[15] == 1`).

---

## 2. Memory: Address Space Mapping
The Memory module acts as a "traffic controller," directing data between the RAM, the Screen, and the Keyboard based on the memory map.

### Address Decoding (The MSB Strategy)
We use the two most significant bits (`address[13..14]`) to route the `load` signal and select the `out` value:

| address[14] | address[13] | Target Chip | Range |
| :--- | :--- | :--- | :--- |
| **0** | **0** | RAM16K | 0x0000 - 0x1FFF |
| **0** | **1** | RAM16K | 0x2000 - 0x3FFF |
| **1** | **0** | Screen | 0x4000 - 0x5FFF |
| **1** | **1** | Keyboard | 0x6000 |



### Implementation Nuances
* **RAM Consolidation:** Because RAM16K covers two address slots (`00` and `01`), we merge the load signals: `Or(a=loadA, b=loadB, out=loadRAM)`.
* **Keyboard Logic:** The Keyboard is read-only; it has no `load` pin. Its output is simply selected by the final `Mux4Way16` when the address is `24576`.

---

## 3. The Computer: Top-Level Integration
The `Computer.hdl` connects the three main modules into a closed-loop system.

* **ROM32K:** The "Instruction Memory." It provides the `instruction` located at the current `pc`.
* **CPU:** The "Processor." It takes the `instruction` and `inM`, producing `outM`, `writeM`, and the next `pc` address.
* **Memory:** The "Data Memory." It stores `outM` if `writeM` is high and provides the CPU with the current `inM` value.



---

## 4. Debugging & HDL Best Practices
* **Signal Sequence:** In HDL, logic gates must be defined before the pins that use their output (e.g., calculate `doJump` before feeding it into the `PC` chip).
* **Internal Pins:** To use an output signal as an input for another chip within the same module, you must create an internal wire (e.g., `ALU(..., out=aluOut, out=outM)`).
* **Bus Widths:** Hack addresses are 15-bit. Ensure you slice your 16-bit buses correctly: `ARegister(..., out[0..14]=addressM)`.