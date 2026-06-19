"""Token definitions for the HyLang lexer."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from typing import Any

from ..errors import SourceSpan


class TokenKind(Enum):
    """The lexical category of a token."""

    NUMBER = auto()      # int or float literal (value is int/float)
    STRING = auto()      # string literal (value is the unquoted str)
    BOOL = auto()        # true / false / null (value is True/False/None)
    IDENT = auto()       # identifier
    KEYWORD = auto()     # if / elif / else / for / while / function / return
    TYPE = auto()        # int / float / string / bool
    OP = auto()          # arithmetic, comparison, bitwise, logical operators
    ASSIGN = auto()      # = += -= *= /=
    LPAREN = auto()
    RPAREN = auto()
    LBRACKET = auto()
    RBRACKET = auto()
    LBRACE = auto()
    RBRACE = auto()
    COMMA = auto()
    SEMICOLON = auto()
    FLAG = auto()        # ===> name <=== marker (value is the inner text)
    IMPORT = auto()      # #import <module>  (value is the module filename)
    EOF = auto()


@dataclass(frozen=True)
class Token:
    """A single lexical token with its source position."""

    kind: TokenKind
    value: Any
    span: SourceSpan

    def __repr__(self) -> str:
        return f"Token({self.kind.name}, {self.value!r}, {self.span})"
