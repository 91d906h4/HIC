"""Diagnostics for every compiler stage.

A single ``HyError`` hierarchy carries an optional :class:`SourceSpan` so messages
can point at the offending line/column instead of the old ``print()+exit()`` calls.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class SourceSpan:
    """A 1-based position in a source file."""

    line: int
    col: int

    def __str__(self) -> str:
        return f"line {self.line}, col {self.col}"


class HyError(Exception):
    """Base class for all HyLang errors.

    Attributes:
        message: Human readable explanation.
        span: Optional source position the error refers to.
    """

    kind = "Error"

    def __init__(self, message: str, span: Optional[SourceSpan] = None) -> None:
        self.message = message
        self.span = span
        super().__init__(message)

    def render(self, source: Optional[str] = None, filename: str = "<input>") -> str:
        """Build a multi-line diagnostic, with a source caret when possible."""
        head = f"{filename}"
        if self.span is not None:
            head += f", {self.span}"
        lines = [f"Traceback:", f"  File {head}"]

        if source is not None and self.span is not None:
            src_lines = source.splitlines()
            idx = self.span.line - 1
            if 0 <= idx < len(src_lines):
                lines.append(f"    {src_lines[idx]}")
                lines.append("    " + " " * (self.span.col - 1) + "^^^")

        lines.append(f"{self.kind}: {self.message}")
        return "\n".join(lines)


class LexError(HyError):
    kind = "Syntax Error"


class ParseError(HyError):
    kind = "Syntax Error"


class CodegenError(HyError):
    kind = "Compile Error"


class HyRuntimeError(HyError):
    kind = "Runtime Error"
