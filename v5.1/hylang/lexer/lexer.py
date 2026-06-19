"""Hand-written scanner: source string -> list[Token].

Handles nested ``/* */`` and ``//`` comments, string literals with escapes,
int/float numbers, identifiers/keywords, longest-match operators, the
``===> flag <===`` marker, and ``#import <module>`` directives. Unary minus is
left for the parser, so negative numbers are no longer a post-hoc hack.
"""

from __future__ import annotations

from typing import List

from ..errors import LexError, SourceSpan
from .token import Token, TokenKind

KEYWORDS = {"if", "elif", "else", "for", "while", "function", "return"}
TYPES = {"int", "float", "string", "bool"}
WORD_OPERATORS = {"and", "or", "not"}

# Multi-character symbols, checked before single characters (longest match).
TWO_CHAR = {
    "**": TokenKind.OP,
    "++": TokenKind.OP,
    "--": TokenKind.OP,
    "<<": TokenKind.OP,
    ">>": TokenKind.OP,
    "<=": TokenKind.OP,
    ">=": TokenKind.OP,
    "==": TokenKind.OP,
    "!=": TokenKind.OP,
    "+=": TokenKind.ASSIGN,
    "-=": TokenKind.ASSIGN,
    "*=": TokenKind.ASSIGN,
    "/=": TokenKind.ASSIGN,
}
ONE_CHAR_OP = set("+-*/%<>&^|")
ONE_CHAR = {
    "=": TokenKind.ASSIGN,
    "(": TokenKind.LPAREN,
    ")": TokenKind.RPAREN,
    "[": TokenKind.LBRACKET,
    "]": TokenKind.RBRACKET,
    "{": TokenKind.LBRACE,
    "}": TokenKind.RBRACE,
    ",": TokenKind.COMMA,
    ";": TokenKind.SEMICOLON,
}
_ESCAPES = {"n": "\n", "t": "\t", "r": "\r", '"': '"', "\\": "\\", "0": "\0"}


class Lexer:
    """Scans a single source string into tokens."""

    def __init__(self, source: str) -> None:
        self.src = source
        self.n = len(source)
        self.i = 0
        self.line = 1
        self.col = 1

    # -- low-level cursor helpers ------------------------------------------
    def _span(self) -> SourceSpan:
        return SourceSpan(self.line, self.col)

    def _peek(self, offset: int = 0) -> str:
        j = self.i + offset
        return self.src[j] if j < self.n else ""

    def _advance(self) -> str:
        ch = self.src[self.i]
        self.i += 1
        if ch == "\n":
            self.line += 1
            self.col = 1
        else:
            self.col += 1
        return ch

    def _starts_with(self, text: str) -> bool:
        return self.src.startswith(text, self.i)

    # -- main entry --------------------------------------------------------
    def tokenize(self) -> List[Token]:
        tokens: List[Token] = []
        while self.i < self.n:
            ch = self._peek()

            if ch in " \t\r\n":
                self._advance()
            elif self._starts_with("/*"):
                self._skip_block_comment()
            elif self._starts_with("//"):
                self._skip_line_comment()
            elif self._starts_with("===>"):
                tokens.append(self._read_flag())
            elif self._starts_with("#import"):
                tokens.append(self._read_import())
            elif ch == '"':
                tokens.append(self._read_string())
            elif ch.isdigit():
                tokens.append(self._read_number())
            elif ch.isalpha() or ch == "_":
                tokens.append(self._read_word())
            else:
                tokens.append(self._read_symbol())

        tokens.append(Token(TokenKind.EOF, None, self._span()))
        return tokens

    # -- comments ----------------------------------------------------------
    def _skip_block_comment(self) -> None:
        # Strings are tracked inside comments so that a '*/' embedded in a string
        # literal (e.g. "a +*/b") does not prematurely close the comment.
        span = self._span()
        depth = 0
        in_string = False
        while self.i < self.n:
            if self._peek() == '"':
                in_string = not in_string
                self._advance()
            elif not in_string and self._starts_with("/*"):
                self._advance(); self._advance()
                depth += 1
            elif not in_string and self._starts_with("*/"):
                self._advance(); self._advance()
                depth -= 1
                if depth == 0:
                    return
            else:
                self._advance()
        raise LexError("Unterminated block comment.", span)

    def _skip_line_comment(self) -> None:
        while self.i < self.n and self._peek() != "\n":
            self._advance()

    # -- literals ----------------------------------------------------------
    def _read_string(self) -> Token:
        span = self._span()
        self._advance()  # opening quote
        out: List[str] = []
        while self.i < self.n:
            ch = self._advance()
            if ch == '"':
                return Token(TokenKind.STRING, "".join(out), span)
            if ch == "\\":
                esc = self._advance() if self.i < self.n else ""
                out.append(_ESCAPES.get(esc, esc))
            else:
                out.append(ch)
        raise LexError("Unterminated string literal.", span)

    def _read_number(self) -> Token:
        span = self._span()
        digits: List[str] = []
        is_float = False
        while self.i < self.n:
            ch = self._peek()
            if ch.isdigit():
                digits.append(self._advance())
            elif ch == "." and not is_float and self._peek(1).isdigit():
                is_float = True
                digits.append(self._advance())
            else:
                break
        text = "".join(digits)
        value = float(text) if is_float else int(text)
        return Token(TokenKind.NUMBER, value, span)

    def _read_word(self) -> Token:
        span = self._span()
        chars: List[str] = []
        while self.i < self.n and (self._peek().isalnum() or self._peek() == "_"):
            chars.append(self._advance())
        word = "".join(chars)

        if word in ("true", "false"):
            return Token(TokenKind.BOOL, word == "true", span)
        if word == "null":
            return Token(TokenKind.BOOL, None, span)
        if word in TYPES:
            return Token(TokenKind.TYPE, word, span)
        if word in KEYWORDS:
            return Token(TokenKind.KEYWORD, word, span)
        if word in WORD_OPERATORS:
            return Token(TokenKind.OP, word, span)
        return Token(TokenKind.IDENT, word, span)

    # -- markers -----------------------------------------------------------
    def _read_flag(self) -> Token:
        span = self._span()
        for _ in range(4):  # consume '===>'
            self._advance()
        inner: List[str] = []
        while self.i < self.n and not self._starts_with("<==="):
            inner.append(self._advance())
        if not self._starts_with("<==="):
            raise LexError("Unterminated flag marker (expected '<===').", span)
        for _ in range(4):  # consume '<==='
            self._advance()
        return Token(TokenKind.FLAG, "".join(inner).strip(), span)

    def _read_import(self) -> Token:
        span = self._span()
        # consume the literal '#import'
        for _ in range(len("#import")):
            self._advance()
        while self.i < self.n and self._peek() in " \t":
            self._advance()
        if self._peek() != "<":
            raise LexError("Expected '<module>' after #import.", span)
        self._advance()  # '<'
        name: List[str] = []
        while self.i < self.n and self._peek() != ">":
            name.append(self._advance())
        if self._peek() != ">":
            raise LexError("Unterminated #import (expected '>').", span)
        self._advance()  # '>'
        return Token(TokenKind.IMPORT, "".join(name).strip(), span)

    # -- symbols -----------------------------------------------------------
    def _read_symbol(self) -> Token:
        span = self._span()
        two = self.src[self.i:self.i + 2]
        if two in TWO_CHAR:
            self._advance(); self._advance()
            return Token(TWO_CHAR[two], two, span)

        ch = self._advance()
        if ch in ONE_CHAR_OP:
            return Token(TokenKind.OP, ch, span)
        if ch in ONE_CHAR:
            return Token(ONE_CHAR[ch], ch, span)
        raise LexError(f"Unexpected character {ch!r}.", span)


def tokenize(source: str) -> List[Token]:
    """Convenience wrapper around :class:`Lexer`."""
    return Lexer(source).tokenize()
