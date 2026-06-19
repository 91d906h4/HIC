# HyLang

A small, statically-typed toy language with a clean, multi-stage compiler and a
stack-based virtual machine. Source (`.hy`) is compiled to a readable bytecode
(`.hyb`) which the VM executes.

```
source.hy ──▶ Lexer ──▶ Parser ──▶ CodeGen ──▶ Assembler ──▶ VM
            tokens     AST        bytecode      .hyb text    output
```

Each stage is a small, independently testable unit that hands plain data to the
next one.

## Quick start

Run a program directly from source:

```sh
python -m hylang run examples/fibonacci.hy
```

Compile to bytecode, then run the bytecode:

```sh
python -m hylang compile examples/fibonacci.hy -o fibonacci.hyb
python -m hylang run fibonacci.hyb
```

`run` accepts either a `.hy` source file or a `.hyb` bytecode file.

## Project layout

```
hylang/
├── errors.py          # HyError hierarchy + SourceSpan (line/col diagnostics)
├── lexer/             # source text -> tokens
│   ├── token.py
│   └── lexer.py
├── parser/            # tokens -> AST
│   ├── ast.py         # frozen dataclass nodes
│   └── parser.py      # recursive descent + Pratt expressions
├── codegen/           # AST -> bytecode
│   ├── isa.py         # Opcode + Instruction definitions
│   └── codegen.py
├── asm/
│   └── assembler.py   # Instruction <-> .hyb text, plus the link step
├── vm/
│   └── vm.py          # executes a linked program
├── driver.py          # source -> bytecode, with #import expansion
└── cli.py             # `compile` / `run` commands

examples/              # sample programs (+ hmodule/ standard library)
tests/                 # pytest: golden, per-stage, and semantics tests
```

## Language guide

### Comments

```hy
// line comment
/* block comment, /* may be nested */ */
```

### Types and variables

Four scalar types: `int`, `float`, `string`, `bool`.

```hy
int    a;            // default 0
float  b = 1.5;
string c = "hello";  // default ""
bool   d = true;     // true, false, or null
int    x, y, z;      // multiple declarations at once
```

### Arrays

Arrays are fixed-size and may be multi-dimensional. Sizes can be any
expression (evaluated at runtime). Negative indices count from the end.

```hy
int grid[2][3];                 // 2x3, zero-filled
int row[3] = [1, 2, 3];         // with an initializer
int n = 4;
int dynamic[n];                 // size from a variable

row[0] = 10;
print(row[-1]);                 // 3
```

### Operators

From tightest to loosest binding:

| Operators                         | Notes                          |
|-----------------------------------|--------------------------------|
| `**`                              | exponent (right-associative)   |
| `*`  `/`  `%`                     |                                |
| `+`  `-`                          | `+` also concatenates strings  |
| `<<`  `>>`                        | bit shift                      |
| `<`  `>`  `<=`  `>=`              |                                |
| `==`  `!=`                        |                                |
| `&`  `^`  `\|`                    | bitwise                        |
| `and`                             |                                |
| `or`                              |                                |

Unary: `-x`, `not x`, and `++`/`--` (prefix or postfix). Comparisons and
logical operators produce real booleans (`true`/`false`).

### Control flow

```hy
if(n > 10){
    print("big");
}
elif(n == 10){
    print("ten");
}
else{
    print("small");
}

for(int i = 0; i < 10; i = i + 1){
    print(i);
}

while(n > 0){
    n = n - 1;
}
```

### Functions

Functions are declared with `function`. Arguments bind left-to-right (the first
parameter receives the first argument). Recursion is supported.

```hy
function add(int a, int b){
    return a + b;
}

print(add(2, 3));   // 5
```

### Imports

`#import <module.hm>` pulls in another file. Modules are searched for in
`hmodule/` next to the importing file. See [examples/hmodule/math.hm](examples/hmodule/math.hm).

```hy
#import <math.hm>
print(pow(2, 10));   // 1024
```

### Output

`print(...)` writes each argument on its own line:

```hy
print(1, 2, 3);   // prints 1, then 2, then 3
```

## Bytecode

Compiling produces a readable, line-oriented `.hyb` file. It is a stack machine:
operands are pushed and consumed from an operand stack. Functions live in a
function table reached via `CALL`; the main program ends at `HALT`, so execution
never falls into a function body by accident.

```
; HyLang bytecode
  DECL int a
  PUSH 100
  NEG
  STORE a
  LOAD a
  CALL abs
  PRINT 1
  HALT
FUNC abs
  ...
```

Jump targets (`JMP`/`JZ`/`JNZ`) and `CALL` names are symbolic labels in the text
form; the assembler resolves them to instruction indices when loading.

## Examples

| File | Shows |
|------|-------|
| [examples/fibonacci.hy](examples/fibonacci.hy) | recursion, dynamic programming, arrays |
| [examples/math.hy](examples/math.hy) | `#import`, function calls |
| [examples/perceptron.hy](examples/perceptron.hy) | float arrays, loops, comparison |
| [examples/arrays_strings.hy](examples/arrays_strings.hy) | arrays, strings, operators, booleans |

## Testing

```sh
python -m pytest
```

The suite covers golden output of every example (run both directly and via a
`.hyb` round-trip), per-stage unit tests for the lexer/parser/codegen, and
end-to-end language semantics.
