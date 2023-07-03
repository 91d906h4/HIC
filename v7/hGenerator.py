import re
from hSymbol import Symbol
from errorHandler import Error

S = Symbol()
E = Error()

class Generator:
    def __init__(self) -> None:
        self.result = []

        self.test1 = ['DEF_STRING', 'DEF_ARRAY', 'array', [2, 3], [['1', ',', '2', ',', '3'], ',', ['4', ',', '5', ',', '6', '+', '5', '*', ['ARRAY', 'a', ['3']]]]]
        self.test2 = ['DEF_INTEGER', 'u', ['123']]
        self.test3 = ['a', '+', 'b', '*', ['1', '+', '2', '/', '3', '*', '4', '-', '5'], '+', [['ARRAY', 'a', ['3', '==', '3']], '**', ['8', '/', '6']], '+', ['1', '+', ['b', '*', '6']], [['ARRAY', 'b', [['ARRAY', 'c', ['2', '+', '5', '*', ['8', '-', '7'], '/', ['FUNCTION', 'pow', 2, ['2'], ['5']]]]]]], '+', ['FUNCTION', 'func', 3, ['8', '-', '9'], ['8', '+', ['ARRAY', 'a', ['10']], ['3']], ['123']], '+', ['ARRAY', 'a', ['2']], ['5'], '+', ['5'], '+', ['1', ',', '2', ',', '3']]

        self.expGenerator(self.test3)

    def isSymbol(self, token: str) -> bool:
        keywords = ["if", "else", "elif", "for", "while", "break", "int", "float", "string", "bool", "function", "true", "false", "and", "or", "not"]
        return re.match(r"([_a-zA-Z][_a-zA-Z0-9]*)|(\d+)", str(token)) and token not in keywords

    def expGenerator(self, tokens: list):
        operator = []

        if tokens[0] == "ARRAY": return
        elif tokens[0] == "FUNCTION": return

        for token in tokens:
            if isinstance(token, list): self.expGenerator(token)
            elif self.isSymbol(token): self.result.append(f"LDA {token}")
            else:
                operator.append(token)

    def defGenerator(self, tokens: list):
        if tokens[1] != "DEF_ARRAY":
            match (tokens[0]):
                case "DEF_INTEGER":
                    self.result.append(f"INT {tokens[1]}")

Generator()