"""The HyLang virtual machine instruction set.

A clean stack ISA. Instructions are structured ``Instruction`` objects in
memory; the assembler serialises them to a readable ``.hyb`` text form. Jump
targets are symbolic labels here and resolved to indices at link time.

Notable cleanups vs the original textual assembly:
  * ``SHL``/``SHR`` mean exactly ``<<``/``>>`` (the old BSL/BSR were swapped).
  * ``JZ``/``JNZ`` replace the ``LNT _`` + conditional ``JMP`` idiom.
  * Functions live in a function table, not inline behind an ``SSKP/ESKP`` hack.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from typing import Tuple


class Opcode(Enum):
    # Stack / memory
    PUSH = auto()        # PUSH <const>            push a literal
    POP = auto()         # POP                     discard top of stack
    LOAD = auto()        # LOAD <name>             push scalar variable
    STORE = auto()       # STORE <name>            pop -> scalar variable
    LOADIDX = auto()     # LOADIDX <name> <k>      pop k indices, push element
    STOREIDX = auto()    # STOREIDX <name> <k>     pop k indices + value, store
    DECL = auto()        # DECL <type> <name>      declare scalar (default init)
    DECLARR = auto()     # DECLARR <type> <name> <ndims>  pop ndims sizes, alloc

    # Arithmetic
    ADD = auto()
    SUB = auto()
    MUL = auto()
    DIV = auto()
    POW = auto()
    MOD = auto()
    NEG = auto()         # unary minus

    # Comparison
    EQ = auto()
    NE = auto()
    GT = auto()
    LT = auto()
    GE = auto()
    LE = auto()

    # Bitwise
    SHL = auto()         # <<
    SHR = auto()         # >>
    BAND = auto()
    BXOR = auto()
    BOR = auto()

    # Logical
    AND = auto()
    OR = auto()
    NOT = auto()

    # Control / IO
    PRINT = auto()       # PRINT <k>               pop k values, print each
    JMP = auto()         # JMP <label>
    JZ = auto()          # JZ <label>              pop; jump if falsy
    JNZ = auto()         # JNZ <label>             pop; jump if truthy
    CALL = auto()        # CALL <name>
    RET = auto()
    HALT = auto()

    # Pseudo-ops (resolved at link, NOP at runtime)
    LABEL = auto()       # LABEL <name>
    FUNC = auto()        # FUNC <name>             marks a function entry point


# Default value used by DECL / DECLARR per declared type.
TYPE_DEFAULTS = {
    "int": 0,
    "float": 0.0,
    "string": "",
    "bool": False,
}


@dataclass
class Instruction:
    op: Opcode
    args: Tuple = ()

    def __repr__(self) -> str:
        if self.args:
            return f"{self.op.name} {' '.join(map(repr, self.args))}"
        return self.op.name
