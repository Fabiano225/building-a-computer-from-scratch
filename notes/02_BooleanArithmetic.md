# Nand2Tetris: Part 2 – Arithmetic & ALU Cheat Sheet

This project transforms logic gates into a calculating machine. It focuses on binary representation, addition, and the logic of the Central Processing Unit (CPU).

## 1. Binary Addition & Overflow
Computers add from right to left, just like humans, but they only know two digits: 0 and 1.
* **1 + 0 = 1**
* **1 + 1 = 0**, carry **1** (this is "10" in binary, which equals 2).
* **1 + 1 + 1 = 1**, carry **1** (this is "11" in binary, which equals 3).
* **Overflow:** If a carry is generated at the leftmost bit (MSB) and there is no more space in the 16-bit register, it is dropped. The number "wraps around" to zero.

---

## 2. The Adder Hierarchy
Complexity is built in three distinct stages:

### HalfAdder (2 Inputs)
Adds two bits (`a`, `b`).
* **Sum:** Calculated via `Xor(a, b)`.
* **Carry:** Calculated via `And(a, b)`.
* *Limitation:* It cannot accept a carry-in from a previous column.

### FullAdder (3 Inputs)
Adds three bits (`a`, `b`, `cIn`). Built using two HalfAdders and one OR gate.
* Processes the carry bit (`cIn`) from the column to its right.
* Essential for any bit position from index 1 to 15.



### Add16 (16-bit Addition)
A chain of adders connected to process 16-bit buses.
* **Bit 0:** Uses a `HalfAdder` (no carry-in exists for the first column).
* **Bits 1-15:** Use `FullAdder` chips. The `carry` output of bit *i* connects to the `cIn` of bit *i+1* (**Ripple-Carry**).

---

## 3. Incrementing (Inc16)
The simplest arithmetic operation: $out = in + 1$.
* **The Logic:** You are adding the number `1` (binary `00...001`) to the input.
* **Efficiency:** You only need a chain of **HalfAdders**. Bit 0 adds the input bit and a constant `true` (1). Every subsequent bit only needs to add the input bit and the carry from the previous stage.
* **HDL Shortcut:** You can reuse your `Add16` by setting the `b` input to 1:
  `Add16(a=in, b[0]=true, b[1..15]=false, out=out);`

---

## 4. The ALU (Arithmetic Logic Unit)
The "brain" of the computer. It doesn't perform 64 different calculations; instead, it **manipulates** inputs and **selects** the desired result using 6 control bits (flags).

### The Control Bits (The "Switches")
1. **zx / zy (Zero):** Forces the input to 0 (`Mux16` with `false`).
2. **nx / ny (Negate):** Flips the bits (`Not16` + `Mux16`).
3. **f (Function):** Selects between `And16` (if 0) and `Add16` (if 1).
4. **no (Negate Out):** Flips the final result bits.



### Common ALU Operations
| zx | nx | zy | ny | f | no | Result (out) |
|:--:|:--:|:--:|:--:|:-:|:--:|:------------:|
| 1 | 0 | 1 | 0 | 1 | 0 | **0** |
| 1 | 1 | 1 | 1 | 1 | 1 | **1** |
| 0 | 0 | 1 | 1 | 0 | 0 | **x** |
| 0 | 0 | 0 | 0 | 1 | 0 | **x + y** |
| 0 | 1 | 0 | 0 | 1 | 1 | **y - x** |

---

## 5. Status Bits (The Sensors)
The ALU outputs two single-bit signals to tell the CPU about the result:

* **ng (Negative):** Check if the result is less than 0.
  * *How:* Simply grab the MSB (Most Significant Bit): `out[15]`.
* **zr (Zero):** Check if the result is exactly 0.
  * *How:* Use `Or8Way` on the bottom 8 bits and another `Or8Way` on the top 8 bits. If both outputs are 0, the whole number is 0. 
  * *Final Step:* Use a `Not` gate because `zr` must be **1** if the result is zero.



## 6. HDL Implementation Tips
* **Internal Pin Splitting:** You cannot use an `OUT` pin as an input later in the same chip. You must create "dummy" internal wires:
  `Mux16(..., out=out, out[15]=ng, out[0..7]=low, out[8..15]=high);`
* **Constants:** `true` is a 16-bit bus of ones; `false` is a 16-bit bus of zeros.