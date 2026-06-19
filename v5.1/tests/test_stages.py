"""Per-stage unit tests for the lexer, parser, and codegen."""

from hylang.lexer import tokenize
from hylang.lexer.token import TokenKind
from hylang.parser import parse
from hylang.parser import ast
from hylang.codegen import compile_program
from hylang.codegen.isa import Opcode


def kinds(source):
    return [t.kind for t in tokenize(source) if t.kind is not TokenKind.EOF]


def test_lexer_numbers_and_negative_is_two_tokens():
    toks = tokenize("-3.5")
    assert toks[0].kind is TokenKind.OP and toks[0].value == "-"
    assert toks[1].kind is TokenKind.NUMBER and toks[1].value == 3.5


def test_lexer_nested_block_comment():
    assert kinds("/* a /* b */ c */ 1") == [TokenKind.NUMBER]


def test_lexer_longest_match_operators():
    vals = [t.value for t in tokenize("a ** b += c") if t.kind is TokenKind.OP
            or t.kind is TokenKind.ASSIGN]
    assert "**" in vals and "+=" in vals


def test_parser_precedence_pratt():
    prog = parse(tokenize("int x = 1 + 2 * 3;"))
    decl = prog.statements[0]
    assert isinstance(decl, ast.VarDecl)
    add = decl.init
    assert isinstance(add, ast.Binary) and add.op == "+"
    assert isinstance(add.right, ast.Binary) and add.right.op == "*"


def test_parser_pow_right_associative():
    prog = parse(tokenize("int x = 2 ** 3 ** 2;"))
    pow_node = prog.statements[0].init
    assert pow_node.op == "**"
    # right child is the nested power -> right associativity
    assert isinstance(pow_node.right, ast.Binary) and pow_node.right.op == "**"


def test_parser_multi_declaration_expands():
    prog = parse(tokenize("int a, b, c;"))
    assert [s.name for s in prog.statements] == ["a", "b", "c"]
    assert all(isinstance(s, ast.VarDecl) for s in prog.statements)


def test_parser_if_elif_else_chain():
    src = "if(a){return 1;} elif(b){return 2;} else {return 3;}"
    node = parse(tokenize(src)).statements[0]
    assert isinstance(node, ast.If)
    assert len(node.branches) == 2  # if + elif
    assert node.orelse is not None


def test_codegen_functions_after_halt():
    instrs = compile_program(parse(tokenize(
        "function f(int n){return n;} int x = f(1); print(x);"
    )))
    ops = [i.op for i in instrs]
    assert Opcode.HALT in ops
    assert ops.index(Opcode.FUNC) > ops.index(Opcode.HALT)
