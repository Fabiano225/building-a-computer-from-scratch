# Nand2Tetris: Project 11 – Compiler II: Code Generation

This project completes the Jack Compiler. We morph the Syntax Analyzer built in Project 10 into a full-scale compiler. Instead of outputting passive XML, the compiler will now generate executable Virtual Machine (VM) code. This involves understanding the semantics of the code, managing variable scopes, and translating high-level constructs into stack-based operations.



## 1. The Symbol Table
To generate correct code, the compiler must remember the variables declared in the program. This is done using a **Symbol Table**, which tracks the properties of every identifier.

### Variable Properties Tracked
* **`name`:** The identifier (e.g., `x`, `sum`, `player`).
* **`type`:** The data type (`int`, `char`, `boolean`, or a class name).
* **`kind`:** The category of the variable (`STATIC`, `FIELD`, `ARG`, or `VAR`/local).
* **`index`:** A running integer assigning a memory slot (e.g., the first field is `0`, the second is `1`).

### Scope Management
The compiler must maintain two separate scopes simultaneously:
1. **Class-Level Scope:** Tracks `STATIC` and `FIELD` variables. This table persists across the entire class compilation.
2. **Subroutine-Level Scope:** Tracks `ARG` (arguments) and `VAR` (local variables). This table is **cleared and reset** every time the compiler starts parsing a new method, function, or constructor.



---

## 2. Code Generation: Subroutines and "this"
Different types of subroutines require different setups in VM code, particularly regarding memory allocation and object orientation (the `this` pointer).

### Constructors
* **Purpose:** Allocate memory for a new object and return its base address.
* **Logic:** 1. Count the number of `FIELD` variables in the class.
  2. Call `Memory.alloc(size)` to get a memory block.
  3. Anchor the `this` segment to the returned base address (`pop pointer 0`).
  4. At the end, return the base address (`push pointer 0`, `return`).

### Methods
* **Purpose:** Operate on an existing object.
* **Logic:** A method implicitly receives the object's base address as its very first argument (`ARG 0`). Before executing the method's body, the compiler must anchor the `this` segment to this address (`push argument 0`, `pop pointer 0`).

### Functions
* **Purpose:** Standalone subroutines (like static methods). They do not interact with object fields, so they do not need to manipulate the `this` pointer.

---

## 3. Translating Statements & Control Flow
The compiler translates high-level logic into stack operations and branching commands.

### Expressions (Postfix Translation)
Jack uses infix notation (`x + y`), but the VM is stack-based and requires postfix execution.
* *Rule:* To compile `exp1 op exp2`, the compiler recursively compiles `exp1`, then compiles `exp2`, and finally outputs the `op` command.
* *Example:* `x + (y * 2)` translates to:
  `push x`, `push y`, `push 2`, `call Math.multiply 2`, `add`.

### If and While Statements
Control flow requires generating unique labels (e.g., `IF_TRUE0`, `IF_FALSE0`, `WHILE_EXP0`) and utilizing the VM's `if-goto` and `goto` commands.
* **`while (condition) { body }`:**
  1. Output `label WHILE_EXP`
  2. Compile `condition`
  3. Output `not` (invert the condition)
  4. Output `if-goto WHILE_END` (exit loop if condition is false)
  5. Compile `body`
  6. Output `goto WHILE_EXP` (loop back)
  7. Output `label WHILE_END`

---

## 4. Arrays and Objects
Handling memory directly is the trickiest part of code generation, relying heavily on the `THAT` segment (`pointer 1`).

### Arrays (`a[i]`)
To access or mutate an array element, we calculate its memory address (`base_address + index`) and anchor the `THAT` segment to it.
* **Expression (`x = a[i]`):** Push `a`, push `i`, `add`. Pop to `pointer 1`. Push `that 0`. Pop to `x`.
* **Assignment (`a[i] = x`):** This is highly complex because evaluating the right side (`x`) might change the `THAT` pointer. The compiler must calculate the target address, push it to the stack, evaluate `x`, and then use a temporary register (`temp 0`) to safely pop the value into `THAT 0`.

### Method Calls (`obj.doSomething()`)
Whenever a method is called on an object, the compiler must secretly push the object's base address as the first argument before pushing the explicit arguments. If `obj.doSomething(1, 2)` is called, the VM code actually calls `Class.doSomething` with 3 arguments.

---

## 5. Development & Testing Stages
Because compiling is complex, Project 11 provides a staged testing pipeline:
1. **Seven:** Tests basic arithmetic, `push` commands, and standard `return`.
2. **ConvertToBin:** Tests local variables, standard expressions, and `while`/`if`/`let` statements.
3. **Square:** Tests object-orientation (constructors, methods, fields, and the `this` pointer).
4. **Average:** Tests the calculation of array memory addresses and string constants.
5. **Pong:** A full integration test of all Jack language features.
6. **ComplexArrays:** A stress test specifically targeting deeply nested array assignments (e.g., `a[b[c]] = d[e]`).