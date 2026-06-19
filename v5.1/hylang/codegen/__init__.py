"""Codegen package: AST -> bytecode instructions."""

from .isa import Opcode, Instruction, TYPE_DEFAULTS
from .codegen import CodeGen, compile_program

__all__ = ["Opcode", "Instruction", "TYPE_DEFAULTS", "CodeGen", "compile_program"]
