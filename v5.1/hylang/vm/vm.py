"""The HyLang stack virtual machine.

Runtime values are native Python values (``int``/``float``/``str``/``bool``/
``None``), so there is no per-instruction string re-parsing. Variables live in
scope frames (current function frame + the global frame); the operand stack is
shared across calls, which is how a callee leaves its return value for the
caller.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict, List, Optional

from ..errors import HyRuntimeError
from ..asm.assembler import LinkedProgram, link
from ..codegen.isa import Instruction, Opcode, TYPE_DEFAULTS


@dataclass
class ArrayCell:
    """A runtime array: flat data plus its declared shape."""

    data: list
    shape: List[int]


# Binary opcode -> function over (left, right). Right operand is popped first.
_BINARY = {
    Opcode.SUB: lambda b, a: b - a,
    Opcode.MUL: lambda b, a: b * a,
    Opcode.DIV: lambda b, a: b / a,
    Opcode.POW: lambda b, a: b ** a,
    Opcode.MOD: lambda b, a: b % a,
    Opcode.SHL: lambda b, a: b << a,
    Opcode.SHR: lambda b, a: b >> a,
    Opcode.BAND: lambda b, a: b & a,
    Opcode.BXOR: lambda b, a: b ^ a,
    Opcode.BOR: lambda b, a: b | a,
    Opcode.EQ: lambda b, a: b == a,
    Opcode.NE: lambda b, a: b != a,
    Opcode.GT: lambda b, a: b > a,
    Opcode.LT: lambda b, a: b < a,
    Opcode.GE: lambda b, a: b >= a,
    Opcode.LE: lambda b, a: b <= a,
}


def _display(value) -> str:
    """Format a value the way HyLang's print() shows it."""
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, ArrayCell):
        return "[" + ", ".join(_display(v) for v in value.data) + "]"
    if isinstance(value, list):
        return "[" + ", ".join(_display(v) for v in value) + "]"
    return str(value)


class VM:
    def __init__(self, program: LinkedProgram,
                 out: Optional[Callable[[str], None]] = None) -> None:
        self.program = program
        self.out = out if out is not None else print
        self.stack: list = []
        self.frames: List[Dict[str, object]] = [{}]
        self.callstack: List[int] = []
        self.pc = 0

    # -- helpers -----------------------------------------------------------
    def _pop(self):
        if not self.stack:
            raise HyRuntimeError("Operand stack underflow.")
        return self.stack.pop()

    def _scope_of(self, name: str) -> Dict[str, object]:
        if name in self.frames[-1]:
            return self.frames[-1]
        if name in self.frames[0]:
            return self.frames[0]
        raise HyRuntimeError(f"Undefined variable {name!r}.")

    def _pop_indices(self, k: int) -> List[int]:
        coords = [int(self._pop()) for _ in range(k)]
        coords.reverse()
        return coords

    @staticmethod
    def _flat_index(coords: List[int], shape: List[int]) -> int:
        if len(coords) == 1:
            return coords[0]  # 1-D: allow Python-style negative indexing
        pos = 0
        for c, dim in zip(coords, shape):
            pos = pos * dim + c
        return pos

    @staticmethod
    def _truthy(value) -> bool:
        return bool(value)

    # -- main loop ---------------------------------------------------------
    def run(self) -> None:
        instrs = self.program.instrs
        handlers = self._handlers()
        while self.pc < len(instrs):
            ins = instrs[self.pc]
            handler = handlers.get(ins.op)
            if handler is None:
                raise HyRuntimeError(f"Unsupported opcode {ins.op.name}.")
            jumped = handler(ins)
            if not jumped:
                self.pc += 1

    def _handlers(self) -> Dict[Opcode, Callable[[Instruction], bool]]:
        h: Dict[Opcode, Callable[[Instruction], bool]] = {
            Opcode.PUSH: self._op_push,
            Opcode.POP: self._op_pop,
            Opcode.LOAD: self._op_load,
            Opcode.STORE: self._op_store,
            Opcode.LOADIDX: self._op_loadidx,
            Opcode.STOREIDX: self._op_storeidx,
            Opcode.DECL: self._op_decl,
            Opcode.DECLARR: self._op_declarr,
            Opcode.NEG: self._op_neg,
            Opcode.ADD: self._op_add,
            Opcode.AND: self._op_and,
            Opcode.OR: self._op_or,
            Opcode.NOT: self._op_not,
            Opcode.PRINT: self._op_print,
            Opcode.JMP: self._op_jmp,
            Opcode.JZ: self._op_jz,
            Opcode.JNZ: self._op_jnz,
            Opcode.CALL: self._op_call,
            Opcode.RET: self._op_ret,
            Opcode.HALT: self._op_halt,
            Opcode.LABEL: self._op_nop,
            Opcode.FUNC: self._op_nop,
        }
        for op in _BINARY:
            h[op] = self._op_binary
        return h

    # -- handlers (return True if they set self.pc themselves) -------------
    def _op_push(self, ins: Instruction) -> bool:
        self.stack.append(ins.args[0])
        return False

    def _op_pop(self, ins: Instruction) -> bool:
        self._pop()
        return False

    def _op_load(self, ins: Instruction) -> bool:
        name = ins.args[0]
        value = self._scope_of(name)[name]
        self.stack.append(value.data if isinstance(value, ArrayCell) else value)
        return False

    def _op_store(self, ins: Instruction) -> bool:
        name = ins.args[0]
        self._scope_of(name)[name] = self._pop()
        return False

    def _op_loadidx(self, ins: Instruction) -> bool:
        name, k = ins.args
        coords = self._pop_indices(k)
        cell = self._array(name)
        self.stack.append(cell.data[self._flat_index(coords, cell.shape)])
        return False

    def _op_storeidx(self, ins: Instruction) -> bool:
        name, k = ins.args
        coords = self._pop_indices(k)
        value = self._pop()
        cell = self._array(name)
        cell.data[self._flat_index(coords, cell.shape)] = value
        return False

    def _array(self, name: str) -> ArrayCell:
        cell = self._scope_of(name)[name]
        if not isinstance(cell, ArrayCell):
            raise HyRuntimeError(f"{name!r} is not an array.")
        return cell

    def _op_decl(self, ins: Instruction) -> bool:
        type_str, name = ins.args
        self.frames[-1][name] = TYPE_DEFAULTS[type_str]
        return False

    def _op_declarr(self, ins: Instruction) -> bool:
        type_str, name, ndims = ins.args
        sizes = self._pop_indices(ndims)
        length = 1
        for s in sizes:
            length *= s
        default = TYPE_DEFAULTS[type_str]
        self.frames[-1][name] = ArrayCell([default] * length, list(sizes))
        return False

    def _op_neg(self, ins: Instruction) -> bool:
        self.stack.append(-self._pop())
        return False

    def _op_add(self, ins: Instruction) -> bool:
        a = self._pop()
        b = self._pop()
        if isinstance(a, str) or isinstance(b, str):
            self.stack.append(_display(b) + _display(a))
        else:
            self.stack.append(b + a)
        return False

    def _op_binary(self, ins: Instruction) -> bool:
        a = self._pop()
        b = self._pop()
        try:
            self.stack.append(_BINARY[ins.op](b, a))
        except ZeroDivisionError:
            raise HyRuntimeError("Division or modulo by zero.")
        return False

    def _op_and(self, ins: Instruction) -> bool:
        a = self._pop()
        b = self._pop()
        self.stack.append(self._truthy(b) and self._truthy(a))
        return False

    def _op_or(self, ins: Instruction) -> bool:
        a = self._pop()
        b = self._pop()
        self.stack.append(self._truthy(b) or self._truthy(a))
        return False

    def _op_not(self, ins: Instruction) -> bool:
        self.stack.append(not self._truthy(self._pop()))
        return False

    def _op_print(self, ins: Instruction) -> bool:
        k = ins.args[0]
        values = [self._pop() for _ in range(k)]
        values.reverse()
        for v in values:
            self.out(_display(v))
        return False

    def _op_jmp(self, ins: Instruction) -> bool:
        self.pc = self._label(ins.args[0])
        return True

    def _op_jz(self, ins: Instruction) -> bool:
        if not self._truthy(self._pop()):
            self.pc = self._label(ins.args[0])
            return True
        return False

    def _op_jnz(self, ins: Instruction) -> bool:
        if self._truthy(self._pop()):
            self.pc = self._label(ins.args[0])
            return True
        return False

    def _label(self, name: str) -> int:
        if name not in self.program.labels:
            raise HyRuntimeError(f"Unknown label {name!r}.")
        return self.program.labels[name]

    def _op_call(self, ins: Instruction) -> bool:
        name = ins.args[0]
        if name not in self.program.funcs:
            raise HyRuntimeError(f"Call to undefined function {name!r}.")
        self.callstack.append(self.pc + 1)
        self.frames.append({})
        self.pc = self.program.funcs[name]
        return True

    def _op_ret(self, ins: Instruction) -> bool:
        if not self.callstack:
            raise HyRuntimeError("'return' outside of a function.")
        self.frames.pop()
        self.pc = self.callstack.pop()
        return True

    def _op_halt(self, ins: Instruction) -> bool:
        self.pc = len(self.program.instrs)
        return True

    def _op_nop(self, ins: Instruction) -> bool:
        return False


def run(program, out: Optional[Callable[[str], None]] = None) -> None:
    """Run a list of instructions or an already-linked program."""
    if isinstance(program, LinkedProgram):
        linked = program
    else:
        linked = link(program)
    VM(linked, out).run()
