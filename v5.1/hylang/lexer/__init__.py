"""Lexer package: turns source text into a flat token stream."""

from .token import Token, TokenKind
from .lexer import Lexer, tokenize

__all__ = ["Token", "TokenKind", "Lexer", "tokenize"]
