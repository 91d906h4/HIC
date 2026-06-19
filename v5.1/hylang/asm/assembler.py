"""Serialise instructions to/from the readable ``.hyb`` text format and link them.

Linking is a single pass that records label and function entry points, so the VM
can jump by instruction index instead of re-scanning text on every jump.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

from ..errors import HyError
from ..codegen.isa import Instruction, Opcode

# What kind of value each argument slot holds, per opcode.
#   const : a runtime literal (PUSH)        -> serialised with type tagging
#   name  : an identifier                   -> bare token
#   type  : a type keyword                  -> bare token
#   int   : an integer count/arity          -> bare token
#   label : a jump label                    -> bare token
ARG_SPEC: Dict[Opcode, List[str]] = {
    Opcode.PUSH: ["const"],
    Opcode.LOAD: ["name"],
    Opcode.STORE: ["name"],
    Opcode.LOADIDX: ["name", "int"],
    Opcode.STOREIDX: ["name", "int"],
    Opcode.DECL: ["type", "name"],
    Opcode.DECLARR: ["type", "name", "int"],
    Opcode.PRINT: ["int"],
    Opcode.JMP: ["label"],
    Opcode.JZ: ["label"],
    Opcode.JNZ: ["label"],
    Opcode.CALL: ["name"],
    Opcode.LABEL: ["label"],
    Opcode.FUNC: ["name"],
}


@dataclass
class LinkedProgram:
    """Instructions plus resolved label/function entry tables."""

    instrs: List[Instruction]
    labels: Dict[str, int]
    funcs: Dict[str, int]


# --------------------------------------------------------------------------- #
# Constant (de)serialisation
# --------------------------------------------------------------------------- #
_STRING_ESCAPES = {"\\": "\\\\", '"': '\\"', "\n": "\\n", "\t": "\\t", "\r": "\\r"}


def _dump_const(value) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):  # must precede int (bool subclasses int)
        return "true" if value else "false"
    if isinstance(value, str):
        body = "".join(_STRING_ESCAPES.get(c, c) for c in value)
        return f'"{body}"'
    return str(value)


def _parse_const(token: str):
    if token == "null":
        return None
    if token in ("true", "false"):
        return token == "true"
    if len(token) >= 2 and token[0] == '"' and token[-1] == '"':
        return _unescape(token[1:-1])
    if "." in token:
        return float(token)
    return int(token)


def _unescape(text: str) -> str:
    out, i = [], 0
    rev = {"\\": "\\", '"': '"', "n": "\n", "t": "\t", "r": "\r"}
    while i < len(text):
        c = text[i]
        if c == "\\" and i + 1 < len(text):
            out.append(rev.get(text[i + 1], text[i + 1]))
            i += 2
        else:
            out.append(c)
            i += 1
    return "".join(out)


def _split_line(line: str) -> List[str]:
    """Whitespace-split a .hyb line while keeping quoted strings intact."""
    parts, cur, in_str = [], [], False
    i = 0
    while i < len(line):
        c = line[i]
        if c == '"':
            in_str = not in_str
            cur.append(c)
        elif c.isspace() and not in_str:
            if cur:
                parts.append("".join(cur))
                cur = []
        elif c == "\\" and in_str and i + 1 < len(line):
            cur.append(c)
            cur.append(line[i + 1])
            i += 1
        else:
            cur.append(c)
        i += 1
    if cur:
        parts.append("".join(cur))
    return parts


# --------------------------------------------------------------------------- #
# Public API
# --------------------------------------------------------------------------- #
def dumps(instrs: List[Instruction]) -> str:
    """Serialise instructions to ``.hyb`` text."""
    lines = ["; HyLang bytecode"]
    for ins in instrs:
        spec = ARG_SPEC.get(ins.op, [])
        parts = [ins.op.name]
        for kind, arg in zip(spec, ins.args):
            parts.append(_dump_const(arg) if kind == "const" else str(arg))
        # Indent everything except section markers, for readability.
        prefix = "" if ins.op in (Opcode.FUNC, Opcode.LABEL) else "  "
        lines.append(prefix + " ".join(parts))
    return "\n".join(lines) + "\n"


def loads(text: str) -> List[Instruction]:
    """Parse ``.hyb`` text back into instructions."""
    name_to_op = {op.name: op for op in Opcode}
    instrs: List[Instruction] = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith(";"):
            continue
        parts = _split_line(line)
        op_name = parts[0]
        if op_name not in name_to_op:
            raise HyError(f"Unknown opcode {op_name!r} in bytecode.")
        op = name_to_op[op_name]
        spec = ARG_SPEC.get(op, [])
        args = []
        for kind, token in zip(spec, parts[1:]):
            if kind == "const":
                args.append(_parse_const(token))
            elif kind == "int":
                args.append(int(token))
            else:
                args.append(token)
        instrs.append(Instruction(op, tuple(args)))
    return instrs


def link(instrs: List[Instruction]) -> LinkedProgram:
    """Resolve label and function entry points into index tables."""
    labels: Dict[str, int] = {}
    funcs: Dict[str, int] = {}
    for i, ins in enumerate(instrs):
        if ins.op is Opcode.LABEL:
            labels[ins.args[0]] = i
        elif ins.op is Opcode.FUNC:
            funcs[ins.args[0]] = i  # last definition wins, as in the original
    return LinkedProgram(instrs, labels, funcs)
