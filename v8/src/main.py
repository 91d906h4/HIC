from lexer import Lexer, TOKENS
from parser import Parser

lexer = Lexer(TOKENS)

input_text = """
if (x >= 10) {
    print(x);
} else {
    x = 5;
}
"""
tokens = lexer.tokenize(input_text)

print(tokens)

parser = Parser(tokens)

ast = parser.parse()
print(ast)