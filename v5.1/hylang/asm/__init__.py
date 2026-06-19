"""Assembler package: instructions <-> .hyb text, plus link step."""

from .assembler import LinkedProgram, dumps, loads, link

__all__ = ["LinkedProgram", "dumps", "loads", "link"]
