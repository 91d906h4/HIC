"""Recursive-descent parser with a Pratt expression sub-parser.

Statements are parsed top-down; expressions use binding powers (``BINARY_BP``)
so precedence lives in one table instead of the old operator-weight + manual
stack juggling. ``**`` is right-associative; everything else is left.
"""

from __future__ import annotations

from typing import List, Optional

from ..errors import ParseError
from ..lexer.token import Token, TokenKind
from . import ast

# Binding power per binary operator (higher binds tighter). Order mirrors the
# original operator weights: bitwise is looser than equality, logical loosest.
BINARY_BP = {
    "or": 1,
    "and": 2,
    "|": 3, "^": 3, "&": 3,
    "==": 4, "!=": 4,
    "<": 5, ">": 5, "<=": 5, ">=": 5,
    "<<": 6, ">>": 6,
    "+": 7, "-": 7,
    "*": 8, "/": 8, "%": 8,
    "**": 9,
}
RIGHT_ASSOC = {"**"}
PREFIX_OPS = {"-", "not", "++", "--"}


class Parser:
    def __init__(self, tokens: List[Token]) -> None:
        self.tokens = tokens
        self.pos = 0

    # -- cursor helpers ----------------------------------------------------
    def _peek(self, offset: int = 0) -> Token:
        j = self.pos + offset
        return self.tokens[j] if j < len(self.tokens) else self.tokens[-1]

    def _advance(self) -> Token:
        tok = self.tokens[self.pos]
        if tok.kind is not TokenKind.EOF:
            self.pos += 1
        return tok

    def _check(self, kind: TokenKind, value=None) -> bool:
        tok = self._peek()
        if tok.kind is not kind:
            return False
        return value is None or tok.value == value

    def _expect(self, kind: TokenKind, what: str) -> Token:
        if not self._check(kind):
            tok = self._peek()
            raise ParseError(f"Expected {what}, got {tok.value!r}.", tok.span)
        return self._advance()

    # -- top level ---------------------------------------------------------
    def parse(self) -> ast.Program:
        stmts: List[ast.Stmt] = []
        while not self._check(TokenKind.EOF):
            stmt = self._parse_stmt()
            if stmt is not None:
                stmts.append(stmt)
        return ast.Program(stmts)

    def _parse_block(self) -> List[ast.Stmt]:
        self._expect(TokenKind.LBRACE, "'{'")
        body: List[ast.Stmt] = []
        while not self._check(TokenKind.RBRACE) and not self._check(TokenKind.EOF):
            stmt = self._parse_stmt()
            if stmt is not None:
                body.append(stmt)
        self._expect(TokenKind.RBRACE, "'}'")
        return body

    # -- statements --------------------------------------------------------
    def _parse_stmt(self) -> Optional[ast.Stmt]:
        tok = self._peek()

        if tok.kind is TokenKind.FLAG:
            self._advance()
            return None
        if tok.kind is TokenKind.SEMICOLON:
            self._advance()
            return None
        if tok.kind is TokenKind.IMPORT:
            self._advance()
            return ast.Import(tok.value, tok.span)
        if tok.kind is TokenKind.TYPE:
            return self._parse_decl(consume_semi=True, allow_multi=True)
        if tok.kind is TokenKind.KEYWORD:
            if tok.value == "if":
                return self._parse_if()
            if tok.value == "for":
                return self._parse_for()
            if tok.value == "while":
                return self._parse_while()
            if tok.value == "function":
                return self._parse_function()
            if tok.value == "return":
                return self._parse_return()
            raise ParseError(f"Unexpected keyword {tok.value!r}.", tok.span)

        return self._parse_expr_stmt(consume_semi=True)

    def _parse_decl(self, consume_semi: bool, allow_multi: bool) -> ast.Stmt:
        type_tok = self._expect(TokenKind.TYPE, "a type")
        decls = [self._parse_declarator(type_tok.value)]
        if allow_multi:
            while self._check(TokenKind.COMMA):
                self._advance()
                decls.append(self._parse_declarator(type_tok.value))
        if consume_semi:
            self._expect(TokenKind.SEMICOLON, "';'")

        if len(decls) == 1:
            return decls[0]
        # Multiple declarators on one line -> wrap as a small block via a
        # synthetic list is not allowed (Program is flat), so the caller path
        # only ever requests multi at statement level where we can return a
        # Block-like If(False)?  Instead expose them through a tuple container.
        return _MultiDecl(decls)

    def _parse_declarator(self, type_str: str):
        name_tok = self._expect(TokenKind.IDENT, "an identifier")
        name = name_tok.value

        if self._check(TokenKind.LBRACKET):
            dims = self._parse_dim_groups()
            init = None
            if self._check(TokenKind.ASSIGN, "="):
                self._advance()
                init = self._parse_array_literal()
            return ast.ArrayDecl(type_str, name, dims, init, name_tok.span)

        init = None
        if self._check(TokenKind.ASSIGN, "="):
            self._advance()
            init = self._parse_expr()
        return ast.VarDecl(type_str, name, init, name_tok.span)

    def _parse_dim_groups(self) -> List[ast.Expr]:
        dims: List[ast.Expr] = []
        while self._check(TokenKind.LBRACKET):
            self._advance()
            dims.append(self._parse_expr())
            while self._check(TokenKind.COMMA):
                self._advance()
                dims.append(self._parse_expr())
            self._expect(TokenKind.RBRACKET, "']'")
        return dims

    def _parse_expr_stmt(self, consume_semi: bool) -> ast.Stmt:
        expr = self._parse_expr()
        if self._peek().kind is TokenKind.ASSIGN:
            op_tok = self._advance()
            value = self._parse_expr()
            node: ast.Stmt = ast.Assign(expr, op_tok.value, value, op_tok.span)
        else:
            node = ast.ExprStmt(expr, getattr(expr, "span", None))
        if consume_semi:
            self._expect(TokenKind.SEMICOLON, "';'")
        return node

    def _parse_if(self) -> ast.If:
        if_tok = self._advance()  # 'if'
        branches = [self._parse_branch()]
        orelse: Optional[List[ast.Stmt]] = None

        while True:
            if self._check(TokenKind.KEYWORD, "elif"):
                self._advance()
                branches.append(self._parse_branch())
            elif self._check(TokenKind.KEYWORD, "else") and \
                    self._peek(1).kind is TokenKind.KEYWORD and self._peek(1).value == "if":
                self._advance(); self._advance()  # 'else' 'if'
                branches.append(self._parse_branch())
            elif self._check(TokenKind.KEYWORD, "else"):
                self._advance()
                orelse = self._parse_block()
                break
            else:
                break
        return ast.If(branches, orelse, if_tok.span)

    def _parse_branch(self) -> ast.Branch:
        self._expect(TokenKind.LPAREN, "'('")
        cond = self._parse_expr()
        self._expect(TokenKind.RPAREN, "')'")
        body = self._parse_block()
        return ast.Branch(cond, body)

    def _parse_for(self) -> ast.For:
        for_tok = self._advance()
        self._expect(TokenKind.LPAREN, "'('")
        init = None if self._check(TokenKind.SEMICOLON) else self._parse_for_clause()
        self._expect(TokenKind.SEMICOLON, "';'")
        cond = None if self._check(TokenKind.SEMICOLON) else self._parse_expr()
        self._expect(TokenKind.SEMICOLON, "';'")
        update = None if self._check(TokenKind.RPAREN) else self._parse_for_clause()
        self._expect(TokenKind.RPAREN, "')'")
        body = self._parse_block()
        return ast.For(init, cond, update, body, for_tok.span)

    def _parse_for_clause(self) -> ast.Stmt:
        if self._check(TokenKind.TYPE):
            return self._parse_decl(consume_semi=False, allow_multi=False)
        return self._parse_expr_stmt(consume_semi=False)

    def _parse_while(self) -> ast.While:
        while_tok = self._advance()
        self._expect(TokenKind.LPAREN, "'('")
        cond = self._parse_expr()
        self._expect(TokenKind.RPAREN, "')'")
        body = self._parse_block()
        return ast.While(cond, body, while_tok.span)

    def _parse_function(self) -> ast.FuncDef:
        fn_tok = self._advance()
        name = self._expect(TokenKind.IDENT, "a function name").value
        self._expect(TokenKind.LPAREN, "'('")
        params: List[ast.Param] = []
        if not self._check(TokenKind.RPAREN):
            params.append(self._parse_param())
            while self._check(TokenKind.COMMA):
                self._advance()
                params.append(self._parse_param())
        self._expect(TokenKind.RPAREN, "')'")
        body = self._parse_block()
        return ast.FuncDef(name, params, body, fn_tok.span)

    def _parse_param(self) -> ast.Param:
        type_str = self._expect(TokenKind.TYPE, "a parameter type").value
        name = self._expect(TokenKind.IDENT, "a parameter name").value
        return ast.Param(type_str, name)

    def _parse_return(self) -> ast.Return:
        ret_tok = self._advance()
        value = None
        if not self._check(TokenKind.SEMICOLON):
            value = self._parse_expr()
        self._expect(TokenKind.SEMICOLON, "';'")
        return ast.Return(value, ret_tok.span)

    # -- expressions (Pratt) ----------------------------------------------
    def _parse_expr(self, min_bp: int = 0) -> ast.Expr:
        left = self._parse_unary()
        while True:
            tok = self._peek()
            if tok.kind is not TokenKind.OP or tok.value not in BINARY_BP:
                break
            bp = BINARY_BP[tok.value]
            right_assoc = tok.value in RIGHT_ASSOC
            if right_assoc:
                if bp < min_bp:
                    break
            elif bp <= min_bp:
                break
            self._advance()
            right = self._parse_expr(bp)
            left = ast.Binary(tok.value, left, right, tok.span)
        return left

    def _parse_unary(self) -> ast.Expr:
        tok = self._peek()
        if tok.kind is TokenKind.OP and tok.value in PREFIX_OPS:
            self._advance()
            operand = self._parse_unary()
            return ast.Unary(tok.value, operand, tok.span)
        return self._parse_postfix()

    def _parse_postfix(self) -> ast.Expr:
        node = self._parse_primary()
        while True:
            tok = self._peek()
            if tok.kind is TokenKind.LBRACKET:
                indices: List[ast.Expr] = []
                while self._check(TokenKind.LBRACKET):
                    self._advance()
                    indices.append(self._parse_expr())
                    while self._check(TokenKind.COMMA):
                        self._advance()
                        indices.append(self._parse_expr())
                    self._expect(TokenKind.RBRACKET, "']'")
                node = ast.Index(node, indices, tok.span)
            elif tok.kind is TokenKind.OP and tok.value in ("++", "--"):
                self._advance()
                node = ast.PostIncr(tok.value, node, tok.span)
            else:
                break
        return node

    def _parse_primary(self) -> ast.Expr:
        tok = self._peek()

        if tok.kind in (TokenKind.NUMBER, TokenKind.STRING, TokenKind.BOOL):
            self._advance()
            return ast.Literal(tok.value, tok.span)

        if tok.kind is TokenKind.IDENT:
            self._advance()
            if self._check(TokenKind.LPAREN):
                return self._parse_call(tok.value, tok.span)
            return ast.Name(tok.value, tok.span)

        if tok.kind is TokenKind.LPAREN:
            self._advance()
            expr = self._parse_expr()
            self._expect(TokenKind.RPAREN, "')'")
            return expr

        if tok.kind is TokenKind.LBRACKET:
            return self._parse_array_literal()

        raise ParseError(f"Unexpected token {tok.value!r}.", tok.span)

    def _parse_call(self, name: str, span) -> ast.Call:
        self._expect(TokenKind.LPAREN, "'('")
        args: List[ast.Expr] = []
        if not self._check(TokenKind.RPAREN):
            args.append(self._parse_expr())
            while self._check(TokenKind.COMMA):
                self._advance()
                args.append(self._parse_expr())
        self._expect(TokenKind.RPAREN, "')'")
        return ast.Call(name, args, span)

    def _parse_array_literal(self) -> ast.ArrayLiteral:
        bracket = self._expect(TokenKind.LBRACKET, "'['")
        elements: List[ast.Expr] = []
        if not self._check(TokenKind.RBRACKET):
            elements.append(self._parse_array_element())
            while self._check(TokenKind.COMMA):
                self._advance()
                elements.append(self._parse_array_element())
        self._expect(TokenKind.RBRACKET, "']'")
        return ast.ArrayLiteral(elements, bracket.span)

    def _parse_array_element(self) -> ast.Expr:
        if self._check(TokenKind.LBRACKET):
            return self._parse_array_literal()
        return self._parse_expr()


class _MultiDecl:
    """Internal carrier for ``int a, b;`` declared on a single line.

    The driver expands it into individual declarations before codegen, so it
    never reaches the AST consumers as a real statement.
    """

    def __init__(self, decls: List[ast.Stmt]) -> None:
        self.decls = decls


def _flatten(statements: List[ast.Stmt]) -> List[ast.Stmt]:
    """Expand any ``_MultiDecl`` carriers into individual declarations."""
    out: List[ast.Stmt] = []
    for stmt in statements:
        if isinstance(stmt, _MultiDecl):
            out.extend(stmt.decls)
        else:
            out.append(_flatten_nested(stmt))
    return out


def _flatten_nested(stmt: ast.Stmt) -> ast.Stmt:
    """Flatten _MultiDecl that appear inside block bodies."""
    if isinstance(stmt, ast.If):
        branches = [ast.Branch(b.cond, _flatten(b.body)) for b in stmt.branches]
        orelse = _flatten(stmt.orelse) if stmt.orelse is not None else None
        return ast.If(branches, orelse, stmt.span)
    if isinstance(stmt, ast.For):
        return ast.For(stmt.init, stmt.cond, stmt.update, _flatten(stmt.body), stmt.span)
    if isinstance(stmt, ast.While):
        return ast.While(stmt.cond, _flatten(stmt.body), stmt.span)
    if isinstance(stmt, ast.FuncDef):
        return ast.FuncDef(stmt.name, stmt.params, _flatten(stmt.body), stmt.span)
    return stmt


def parse(tokens: List[Token]) -> ast.Program:
    """Parse tokens into a :class:`Program`, expanding multi-declarations."""
    program = Parser(tokens).parse()
    return ast.Program(_flatten(program.statements))
