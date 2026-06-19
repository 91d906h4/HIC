"""AST -> bytecode.

Layout of the emitted program: all "main" statements first, then ``HALT``,
then every function body. Functions are reached only through ``CALL`` (the
function table is built at link time from the ``FUNC`` markers), so execution
falls off into ``HALT`` and never walks into a function body by accident.

Calling convention: arguments are pushed right-to-left and the callee prologue
pops them in declaration order, so the first parameter receives the first
argument (standard left-to-right binding).
"""

from __future__ import annotations

from typing import List

from ..errors import CodegenError
from ..parser import ast
from .isa import Instruction, Opcode

BINOP_OPCODE = {
    "+": Opcode.ADD, "-": Opcode.SUB, "*": Opcode.MUL, "/": Opcode.DIV,
    "**": Opcode.POW, "%": Opcode.MOD,
    "==": Opcode.EQ, "!=": Opcode.NE, ">": Opcode.GT, "<": Opcode.LT,
    ">=": Opcode.GE, "<=": Opcode.LE,
    "<<": Opcode.SHL, ">>": Opcode.SHR, "&": Opcode.BAND, "^": Opcode.BXOR,
    "|": Opcode.BOR,
    "and": Opcode.AND, "or": Opcode.OR,
}


class CodeGen:
    def __init__(self) -> None:
        self.instrs: List[Instruction] = []
        self._label_n = 0

    # -- helpers -----------------------------------------------------------
    def _emit(self, op: Opcode, *args) -> None:
        self.instrs.append(Instruction(op, tuple(args)))

    def _new_label(self) -> str:
        self._label_n += 1
        return f"L{self._label_n}"

    # -- top level ---------------------------------------------------------
    def compile(self, program: ast.Program) -> List[Instruction]:
        funcs = [s for s in program.statements if isinstance(s, ast.FuncDef)]
        mains = [
            s for s in program.statements
            if not isinstance(s, (ast.FuncDef, ast.Import))
        ]

        for stmt in mains:
            self._gen_stmt(stmt)
        self._emit(Opcode.HALT)
        for func in funcs:
            self._gen_func(func)
        return self.instrs

    def _gen_func(self, func: ast.FuncDef) -> None:
        self._emit(Opcode.FUNC, func.name)
        for param in func.params:
            self._emit(Opcode.DECL, param.type, param.name)
            self._emit(Opcode.STORE, param.name)
        for stmt in func.body:
            self._gen_stmt(stmt)
        # Safety net so a function without an explicit return still returns.
        self._emit(Opcode.PUSH, None)
        self._emit(Opcode.RET)

    # -- statements --------------------------------------------------------
    def _gen_stmt(self, stmt: ast.Stmt) -> None:
        if isinstance(stmt, ast.VarDecl):
            self._gen_var_decl(stmt)
        elif isinstance(stmt, ast.ArrayDecl):
            self._gen_array_decl(stmt)
        elif isinstance(stmt, ast.Assign):
            self._gen_assign(stmt)
        elif isinstance(stmt, ast.ExprStmt):
            self._gen_expr_stmt(stmt)
        elif isinstance(stmt, ast.Return):
            self._gen_return(stmt)
        elif isinstance(stmt, ast.If):
            self._gen_if(stmt)
        elif isinstance(stmt, ast.For):
            self._gen_for(stmt)
        elif isinstance(stmt, ast.While):
            self._gen_while(stmt)
        elif isinstance(stmt, ast.Import):
            pass
        elif isinstance(stmt, ast.FuncDef):
            raise CodegenError("Nested function definitions are not supported.",
                               stmt.span)
        else:
            raise CodegenError(f"Cannot generate code for {type(stmt).__name__}.",
                               getattr(stmt, "span", None))

    def _gen_var_decl(self, stmt: ast.VarDecl) -> None:
        self._emit(Opcode.DECL, stmt.type, stmt.name)
        if stmt.init is not None:
            self._gen_expr(stmt.init)
            self._emit(Opcode.STORE, stmt.name)

    def _gen_array_decl(self, stmt: ast.ArrayDecl) -> None:
        for dim in stmt.dims:
            self._gen_expr(dim)
        self._emit(Opcode.DECLARR, stmt.type, stmt.name, len(stmt.dims))
        if stmt.init is not None:
            self._gen_array_init(stmt.name, stmt.init)

    def _gen_array_init(self, name: str, literal: ast.ArrayLiteral) -> None:
        for coords, value in _flatten_literal(literal, []):
            self._gen_expr(value)
            for c in coords:
                self._emit(Opcode.PUSH, c)
            self._emit(Opcode.STOREIDX, name, len(coords))

    def _gen_assign(self, stmt: ast.Assign) -> None:
        op = stmt.op
        target = stmt.target

        if isinstance(target, ast.Name):
            if op == "=":
                self._gen_expr(stmt.value)
            else:
                self._emit(Opcode.LOAD, target.ident)
                self._gen_expr(stmt.value)
                self._emit(BINOP_OPCODE[op[0]])
            self._emit(Opcode.STORE, target.ident)
        elif isinstance(target, ast.Index):
            name = self._index_name(target)
            k = len(target.indices)
            if op == "=":
                self._gen_expr(stmt.value)
            else:
                for idx in target.indices:
                    self._gen_expr(idx)
                self._emit(Opcode.LOADIDX, name, k)
                self._gen_expr(stmt.value)
                self._emit(BINOP_OPCODE[op[0]])
            for idx in target.indices:
                self._gen_expr(idx)
            self._emit(Opcode.STOREIDX, name, k)
        else:
            raise CodegenError("Invalid assignment target.", stmt.span)

    def _gen_expr_stmt(self, stmt: ast.ExprStmt) -> None:
        expr = stmt.expr
        if isinstance(expr, ast.Call) and expr.func == "print":
            self._gen_print(expr)
            return
        self._gen_expr(expr)
        self._emit(Opcode.POP)  # discard the unused result

    def _gen_return(self, stmt: ast.Return) -> None:
        if stmt.value is not None:
            self._gen_expr(stmt.value)
        else:
            self._emit(Opcode.PUSH, None)
        self._emit(Opcode.RET)

    def _gen_if(self, stmt: ast.If) -> None:
        end = self._new_label()
        for branch in stmt.branches:
            nxt = self._new_label()
            self._gen_expr(branch.cond)
            self._emit(Opcode.JZ, nxt)
            for s in branch.body:
                self._gen_stmt(s)
            self._emit(Opcode.JMP, end)
            self._emit(Opcode.LABEL, nxt)
        if stmt.orelse is not None:
            for s in stmt.orelse:
                self._gen_stmt(s)
        self._emit(Opcode.LABEL, end)

    def _gen_for(self, stmt: ast.For) -> None:
        if stmt.init is not None:
            self._gen_stmt(stmt.init)
        start, end = self._new_label(), self._new_label()
        self._emit(Opcode.LABEL, start)
        if stmt.cond is not None:
            self._gen_expr(stmt.cond)
            self._emit(Opcode.JZ, end)
        for s in stmt.body:
            self._gen_stmt(s)
        if stmt.update is not None:
            self._gen_stmt(stmt.update)
        self._emit(Opcode.JMP, start)
        self._emit(Opcode.LABEL, end)

    def _gen_while(self, stmt: ast.While) -> None:
        start, end = self._new_label(), self._new_label()
        self._emit(Opcode.LABEL, start)
        self._gen_expr(stmt.cond)
        self._emit(Opcode.JZ, end)
        for s in stmt.body:
            self._gen_stmt(s)
        self._emit(Opcode.JMP, start)
        self._emit(Opcode.LABEL, end)

    # -- expressions -------------------------------------------------------
    def _gen_expr(self, expr: ast.Expr) -> None:
        if isinstance(expr, ast.Literal):
            self._emit(Opcode.PUSH, expr.value)
        elif isinstance(expr, ast.Name):
            self._emit(Opcode.LOAD, expr.ident)
        elif isinstance(expr, ast.Binary):
            self._gen_expr(expr.left)
            self._gen_expr(expr.right)
            self._emit(BINOP_OPCODE[expr.op])
        elif isinstance(expr, ast.Unary):
            self._gen_unary(expr)
        elif isinstance(expr, ast.PostIncr):
            self._gen_postincr(expr)
        elif isinstance(expr, ast.Index):
            name = self._index_name(expr)
            for idx in expr.indices:
                self._gen_expr(idx)
            self._emit(Opcode.LOADIDX, name, len(expr.indices))
        elif isinstance(expr, ast.Call):
            self._gen_call(expr)
        elif isinstance(expr, ast.ArrayLiteral):
            raise CodegenError("Array literal is only valid as an initializer.",
                               expr.span)
        else:
            raise CodegenError(f"Cannot generate {type(expr).__name__}.",
                               getattr(expr, "span", None))

    def _gen_unary(self, expr: ast.Unary) -> None:
        if expr.op == "-":
            self._gen_expr(expr.operand)
            self._emit(Opcode.NEG)
        elif expr.op == "not":
            self._gen_expr(expr.operand)
            self._emit(Opcode.NOT)
        elif expr.op in ("++", "--"):
            # prefix: increment first, then yield the new value.
            self._gen_incr(expr.operand, expr.op, expr.span)
            self._gen_expr(expr.operand)
        else:
            raise CodegenError(f"Unknown unary operator {expr.op!r}.", expr.span)

    def _gen_postincr(self, expr: ast.PostIncr) -> None:
        # postfix: yield the old value, then increment.
        self._gen_expr(expr.target)
        self._gen_incr(expr.target, expr.op, expr.span)

    def _gen_incr(self, target: ast.Expr, op: str, span) -> None:
        if not isinstance(target, ast.Name):
            raise CodegenError("++/-- requires a simple variable target.", span)
        bin_op = Opcode.ADD if op == "++" else Opcode.SUB
        self._emit(Opcode.LOAD, target.ident)
        self._emit(Opcode.PUSH, 1)
        self._emit(bin_op)
        self._emit(Opcode.STORE, target.ident)

    def _gen_call(self, expr: ast.Call) -> None:
        if expr.func == "print":
            raise CodegenError("print() does not return a value.", expr.span)
        # Push right-to-left so the prologue (which pops in declaration order)
        # binds the first parameter to the first argument.
        for arg in reversed(expr.args):
            self._gen_expr(arg)
        self._emit(Opcode.CALL, expr.func)

    def _gen_print(self, expr: ast.Call) -> None:
        for arg in expr.args:
            self._gen_expr(arg)
        self._emit(Opcode.PRINT, len(expr.args))

    @staticmethod
    def _index_name(node: ast.Index) -> str:
        if not isinstance(node.target, ast.Name):
            raise CodegenError("Only simple arrays can be indexed.", node.span)
        return node.target.ident


def _flatten_literal(node: ast.ArrayLiteral, prefix):
    """Yield ``(coords, value_expr)`` pairs for a (possibly nested) literal."""
    for i, el in enumerate(node.elements):
        if isinstance(el, ast.ArrayLiteral):
            yield from _flatten_literal(el, prefix + [i])
        else:
            yield prefix + [i], el


def compile_program(program: ast.Program) -> List[Instruction]:
    """Compile a parsed program into a flat instruction list."""
    return CodeGen().compile(program)
