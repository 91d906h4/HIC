from hLexer import Lexer
from hParser import Parser
from hGenerator import Generator

raw = open("./test/def_test.hy").read()

# Lexer
tokens = Lexer(raw).getTokens()

# Parser
Parser(tokens)

# Code Generator