# Nand2Tetris: Part 12 – The Operating System (Jack OS) Cheat Sheet

This final project closes the gap between high-level software (Jack) and the hardware architecture (Hack). Since the Hack hardware is extremely minimalistic, the OS must implement basic features like multiplication, memory allocation, and text rendering in software.

## 1. Math: Software Arithmetic
The Hack ALU only supports `+`, `-`, `&`, `|`, `!`, and `-x`. It does **not** support multiplication or division natively. All math functions must run in $O(n)$ time, where $n = 16$ (number of bits).

* **Multiplication (`x * y`):** Implemented using shift-and-add. You iterate through the 16 bits of `y`. If the $i$-th bit of `y` is 1, you add the shifted version of `x` to the sum.
* **Division (`x / y`):** Implemented using long division (recursively or iteratively). *Crucial detail:* Handle overflow and division by zero.
* **Square Root (`sqrt(x)`):** Implemented using binary search. You build the result bit by bit (from $j = 7$ down to $0$) by checking if `(y + 2^j)^2 <= x`. *Warning:* `(y + 2^j)^2` can overflow the 16-bit limit, so you must also check that it remains `> 0`.

---

## 2. Memory Management (The Heap)
Jack has no automatic garbage collection. The `Memory` class manages the RAM segment from `2048` to `16383` (the Heap) for object and array allocation.

* **The FreeList:** A linked list tracking available memory blocks. A block has a header: `[length, next]`. 
* **`alloc(size)`:** Uses a search algorithm (like *First-Fit* or *Best-Fit*) to find a block in the `freeList` large enough. It carves out `size + 1` words (1 word for the block's own size header) and returns the base address.
* **`deAlloc(object)`:** Reclaims the memory. In a basic implementation, it simply appends the freed block to the end of the `freeList`. (Advanced OS implementations merge adjacent free blocks to prevent fragmentation).

---

## 3. Screen & Graphics (Memory-Mapped I/O)
The physical screen is a 512x256 grid of pixels, mapped to RAM addresses `16384` to `24575`. 
* **1 Bit = 1 Pixel:** Each 16-bit word in memory controls 16 horizontal pixels.
* **`drawPixel(x, y)`:** You cannot just overwrite a word in memory, or you will erase the other 15 pixels! 
    1. Calculate the address: `16384 + (y * 32) + (x / 16)`
    2. Read the current 16-bit value (`Memory.peek`).
    3. Use bitwise `|` (to draw black) or `& ~` (to draw white) to change *only* the specific bit (`x % 16`).
    4. Write the value back (`Memory.poke`).
* **`drawLine(x1, y1, x2, y2)`:** Uses an algorithm (like Bresenham's) to draw straight lines efficiently without using floating-point math or division.

---

## 4. Input / Output (Text & Keyboard)
The Hack platform treats text purely as graphical pixels drawn on the screen.

* **Output (Font Rendering):** The OS stores a bitmap dictionary (`charMaps`) for every printable ASCII character. Each character is an 8x11 pixel grid. `printChar` loops through these 11 rows and calls `drawPixel` (or pokes memory directly for speed) to draw the character at the current `cursor` position.
* **Keyboard (`24576`):** This single RAM address holds the ASCII code of the currently pressed key, or `0` if nothing is pressed.
    * `keyPressed()`: Simply peeks at `24576`.
    * `readChar()`: Uses a **busy loop** (waiting) until a key is pressed, registers the key, and uses another busy loop waiting until the key is *released* before echoing it to the screen and returning the value.

---

## 5. Strings & Arrays
* **Arrays:** In Jack, `Array.new(size)` is basically just a direct call to `Memory.alloc(size)`. Array indexing (`arr[i]`) is resolved by the compiler into pointer addition (`*(arr + i)`).
* **Strings:** Strings are dynamically allocated arrays of characters.
    * They have a `maxLength` (capacity) and a `length` (current characters).
    * **Type Casting:** `intValue()` parses characters into numbers (using `c - 48`). `setInt(val)` does the reverse (using modulo and division) to turn a number into ASCII digits.

---

## 6. Sys (The Bootloader)
* **`Sys.init()`:** The first thing the VM emulator runs. It must initialize the OS classes in a specific order (usually: Memory, Math, Screen, Output, Keyboard) before calling `Main.main()`.
* **`Sys.wait(duration)`:** Implemented using a nested loop. The inner loop acts as a delay to approximate 1 millisecond per iteration. You must calibrate this constant based on your machine's/emulator's execution speed.