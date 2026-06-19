"""AST node definitions for HyLang.

Nodes are frozen dataclasses. Each carries an optional ``span`` for diagnostics.
A :class:`Program` is just an ordered list of top-level statements; the codegen
later separates function definitions from "main" statements.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, Union

from ..errors import SourceSpan

# --------------------------------------------------------------------------- #
# Expressions
# --------------------------------------------------------------------------- #


@dataclass(frozen=True)
class Literal:
    value: object            # int | float | str | bool | None
    span: Optional[SourceSpan] = None


@dataclass(frozen=True)
class Name:
    ident: str
    span: Optional[SourceSpan] = None


@dataclass(frozen=True)
class Unary:
    op: str                  # '-', 'not', and prefix '++'/'--'
    operand: "Expr"
    span: Optional[SourceSpan] = None


@dataclass(frozen=True)
class PostIncr:
    op: str                  # '++' or '--'
    target: "Expr"           # Name or Index
    span: Optional[SourceSpan] = None


@dataclass(frozen=True)
class Binary:
    op: str
    left: "Expr"
    right: "Expr"
    span: Optional[SourceSpan] = None


@dataclass(frozen=True)
class Index:
    target: "Expr"
    indices: List["Expr"]    # one entry per coordinate (across [] and commas)
    span: Optional[SourceSpan] = None


@dataclass(frozen=True)
class Call:
    func: str
    args: List["Expr"]
    span: Optional[SourceSpan] = None


@dataclass(frozen=True)
class ArrayLiteral:
    elements: List["Expr"]   # elements may themselves be ArrayLiteral (nested)
    span: Optional[SourceSpan] = None


Expr = Union[Literal, Name, Unary, PostIncr, Binary, Index, Call, ArrayLiteral]

# --------------------------------------------------------------------------- #
# Statements
# --------------------------------------------------------------------------- #


@dataclass(frozen=True)
class VarDecl:
    type: str
    name: str
    init: Optional[Expr] = None
    span: Optional[SourceSpan] = None


@dataclass(frozen=True)
class ArrayDecl:
    type: str
    name: str
    dims: List[Expr]
    init: Optional[ArrayLiteral] = None
    span: Optional[SourceSpan] = None


@dataclass(frozen=True)
class Assign:
    target: Expr             # Name or Index
    op: str                  # '=', '+=', '-=', '*=', '/='
    value: Expr
    span: Optional[SourceSpan] = None


@dataclass(frozen=True)
class ExprStmt:
    expr: Expr
    span: Optional[SourceSpan] = None


@dataclass(frozen=True)
class Return:
    value: Optional[Expr] = None
    span: Optional[SourceSpan] = None


@dataclass(frozen=True)
class Branch:
    """One condition + body (used for the leading `if` and each `elif`)."""

    cond: Expr
    body: List["Stmt"]


@dataclass(frozen=True)
class If:
    branches: List[Branch]            # if + elifs, in order
    orelse: Optional[List["Stmt"]] = None
    span: Optional[SourceSpan] = None


@dataclass(frozen=True)
class For:
    init: Optional["Stmt"]
    cond: Optional[Expr]
    update: Optional["Stmt"]
    body: List["Stmt"] = field(default_factory=list)
    span: Optional[SourceSpan] = None


@dataclass(frozen=True)
class While:
    cond: Expr
    body: List["Stmt"] = field(default_factory=list)
    span: Optional[SourceSpan] = None


@dataclass(frozen=True)
class Param:
    type: str
    name: str


@dataclass(frozen=True)
class FuncDef:
    name: str
    params: List[Param]
    body: List["Stmt"]
    span: Optional[SourceSpan] = None


@dataclass(frozen=True)
class Import:
    module: str
    span: Optional[SourceSpan] = None


Stmt = Union[
    VarDecl, ArrayDecl, Assign, ExprStmt, Return, If, For, While, FuncDef, Import
]


@dataclass(frozen=True)
class Program:
    statements: List[Stmt]
