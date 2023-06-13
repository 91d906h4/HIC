from lexer import Lexer
from parser import Parser

raw = open("./test/test.hy").read()

# Tokenize
tokens = Lexer(raw).getTokens()

# for i in tokens:
#     print(i)

parse = Parser(tokens)