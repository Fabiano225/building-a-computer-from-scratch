# Nand2Tetris: Part 1 – Logic & HDL Cheat Sheet

These notes serve as a reminder of the most important points regarding buses and slicing.

## 1. Core Logic Principles
* **AND**: Output is 1 only if **all** inputs are 1.
* **OR**: Output is 1 if **at least one** input is 1 (always 1 except for 0-0-0).
* **NAND**: The "Universal Gate." Opposite of AND (0 only if all inputs are 1).
* **XOR**: "Odd-Parity Gate." Output is 1 if an **odd number** of inputs are 1.

---

## 2. Thinking in HDL:
HDL is a **Hardware Description Language**. It is a list of connections, not a sequence of commands.
`Mux(a=a, b=b, sel=sel, out=x);` means:
1.  Take the `Mux` chip.
2.  Connect its internal pin `a` to my input `a`.
3.  Store the result in an internal wire (node) named `x`.

### Internal Nodes (Wires)
When passing a signal from one gate to the next, you must name the "invisible" wire:
```hdl
// Building AND from NAND and NOT
Nand(a=a, b=b, out=nandResult); // 'nandResult' is the internal wire
Not(in=nandResult, out=out);

## 3. Buses & Slicing (The Syntax Wall):
A bus like `in[16]` or `sel[3]` is a bundle of wires.

### The `[0..1]` Slicing Trick
Larger chips often take only a piece of a bus.

* `sel[3]` has three wires: index 0, 1, and 2.

* `sel[0..1]`: Slices the first two wires (Bit 0 and 1). Used to choose between 4 options.

* `sel[2]`: Grabs the 3rd wire. Used to choose between two "blocks" of 4.

## 4. Building Pyramids (Mux & DMux Hierarchy)
Complex chips are built by nesting simpler chips.

### Mux4Way16 (1 of 4)
* Layer 1: Two `Mux16` chips decide between "neighbors" (a vs b and c vs d) using `sel[0]`.

* Layer 2: One final `Mux16` decides between the two winners using `sel[1]`.

### Mux8Way16 (1 of 8)
* Layer 1: Two `Mux4Way16` chips filter two groups of four. Both use `sel[0..1]`.

* Layer 2: One final `Mux16` picks the grand winner using the "highest" bit `sel[2]`.

### DMux4Way (Distribute 1 to 4)
* Layer 1: One `DMux` sends the signal to either the "top half" or "bottom half" using `sel[1]`.

* Layer 2: Two more `DMux` gates perform the fine distribution using `sel[0]`.

## 5. Multi-Bit vs. Way
* 16-Bit Gates (`And16`, `Mux16`): Imagine 16 gates in parallel. They are "wide."

* Way Gates (`Or8Way`): This is a "funnel." It takes an 8-bit bus and collapses it into one single bit. It checks if any bit in the bus is 1.