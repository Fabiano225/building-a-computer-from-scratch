# Nand2Tetris: Project 10 – Compiler I: Syntax Analysis

This project marks the beginning of the high-level language translation process. We build the frontend of a compiler for the Jack programming language. The goal is to perform **Syntax Analysis** (Lexical Analysis and Parsing), which translates raw Jack source code into a structured, intermediate XML syntax tree. This proves that our compiler understands the grammar of the language before we generate executable VM code in Project 11.

## 1. The Jack Tokenizer (Lexical Analysis)
Before understanding the grammar, the compiler must break down the raw text into a stream of meaningful chunks called **Tokens**, while ignoring whitespace and comments.

### Token Types
Every piece of valid Jack code falls into one of five categories:
* **`keyword`:** Reserved words in the Jack language (e.g., `class`, `constructor`, `let`, `if`, `int`, `true`).
* **`symbol`:** Punctuation and operators (e.g., `{`, `}`, `(`, `)`, `+`, `=`, `;`).
* **`identifier`:** Programmer-defined names for variables, classes, and subroutines (e.g., `Main`, `x`, `draw`). Must not start with a digit.
* **`integerConstant`:** Numeric values from `0` to `32767`.
* **`stringConstant`:** A sequence of characters enclosed in double quotes (e.g., `"Hello World"`). The quotes themselves are discarded.

### XML Escaping Rules
Since the output is formatted as XML, specific Jack symbols clash with XML markup syntax and must be escaped during the tokenizing phase:
* `<` becomes `&lt;`
* `>` becomes `&gt;`
* `"` becomes `&quot;`
* `&` becomes `&amp;`

---

## 2. The Compilation Engine (Parsing)
The parser receives the stream of tokens and groups them into logical structures according to the Jack Grammar. We use a **Recursive Descent Parsing** strategy, meaning each grammatical rule has a dedicated compilation method that can call other methods recursively.

### Program Structure
* **`class`:** The root of every Jack file. It contains a class name, variable declarations, and subroutines.
* **`classVarDec`:** Static or field variables declared at the class level.
* **`subroutineDec`:** Methods, functions, or constructors. It includes the return type, name, a `parameterList`, and a `subroutineBody`.

### Statements
Jack features five specific statements, which are grouped inside a `<statements>` block.
* **`letStatement`:** Assigns a value to a variable or array element (`let x = 15;`).
* **`ifStatement`:** Conditional branching, including an optional `else` block.
* **`whileStatement`:** Loop execution based on an expression.
* **`doStatement`:** Subroutine calls for their side effects, ignoring any return value (`do draw();`).
* **`returnStatement`:** Exits a subroutine, optionally returning a value.

### Expressions & Terms
* **`expression`:** A combination of terms and operators (e.g., `x + (y * 2)`).
* **`term`:** The base units of expressions (constants, variables, or nested expressions).
* **`expressionList`:** A comma-separated list of expressions, typically used when passing arguments to a subroutine.

---

## 3. The LL(1) Lookahead Challenge
Jack is an LL(1) grammar, meaning we generally only need to look at the current token to know which parsing rule to apply. However, when parsing a `term` that begins with an `identifier`, we face an ambiguity. An identifier `foo` could be:

1. A simple variable: `foo`
2. An array access: `foo[i]`
3. A subroutine call: `foo()`
4. A method/function call on an object/class: `foo.bar()`

### The Solution: Peeking
To resolve this, the Tokenizer must support a `peek()` function to look at the **next** token without advancing the stream:
* If the next token is `[` -> Parse as array access.
* If the next token is `(` -> Parse as a subroutine call.
* If the next token is `.` -> Parse as a method/function call.
* Otherwise -> Parse as a simple variable name.

---

## 4. Key Implementation Patterns (Python/Java)

### Robust Tokenization (Regex)
Using Regular Expressions makes separating strings, symbols, and keywords highly efficient.
```python
# Example logic for tokenizing
import re

# Strip all comments (single line and multi-line)
text = re.sub(r'//.*', '', text)
text = re.sub(r'/\*.*?\*/', '', text, flags=re.DOTALL)

# Split into tokens using a capturing group
token_pattern = re.compile(r'("[^"\n]*"|[{}()\[\].,;+\-*/&|<>=~]|\b[a-zA-Z_]\w*\b|\b\d+\b)')
tokens = token_pattern.findall(text)
```

### Recursive Parsing
Methods in the Compilation Engine mirror the grammar rules and call each other.

```python
def compileExpression(self):
    self.write("<expression>")
    self.compileTerm() # Every expression has at least one term
    
    # Process optional operators and additional terms
    while self.current_token() in ['+', '-', '*', '/', '&', '|', '<', '>', '=']:
        self.processSymbol()
        self.compileTerm()
        
    self.write("</expression>")
```

## 5. Output Requirements
* **Empty Tags:** If a grammar rule produces no inner content (e.g., an empty parameter list), it MUST be formatted with a line break between the opening and closing tags to satisfy the `TextComparer`:
```xml
<parameterList>
</parameterList>
```

* **Indentation:** While the `TextComparer` ignores whitespace and indentation, adding indentation (e.g., 2 spaces per nested level) is highly recommended to make the XML output human-readable for debugging.