from tokenizer import Tokenizer

raw = open("./test.hy").read()

# Tokenize
tokens = Tokenizer(raw).getTokens()