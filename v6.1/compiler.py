from lexer import Lexer

raw = open("./test.hy").read()

# Tokenize
tokens = Lexer(raw).getTokens()

print(tokens)