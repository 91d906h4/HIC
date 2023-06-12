import re
from errorHandler import Error

E = Error()

class Parser:
    def __init__(self, tokens: list) -> None:
        self.tokens = tokens

        # _, t = self.expSolver(tokens, 0)
        # print(t)
        self.defSolver(tokens, 4)
    
    def isSymbol(self, token: str) -> bool:
        keywords = ["if", "else", "elif", "for", "while", "break", "int", "float", "string", "bool"]
        return re.match(r"[_a-zA-Z][_a-zA-Z0-9]*", token) and token not in keywords

    def expSolver(self, tokens: list, index: int):
        temp, isArray, isFunction = [], False, False

        while index < len(tokens):
            if tokens[index]["types"] == "SEMICOLON": break

            if tokens[index]["types"] == "COMMENT":
                index += 1
                continue

            if tokens[index]["types"] not in ["LEFTPAREN", "RIGHTPAREN", "LEFTBRACKET", "RIGHTBRACKET"]: temp.append(tokens[index]["symbol"])

            # Check if array.
            if index + 1 < len(tokens) and tokens[index + 1]["symbol"] == "[" and \
               not isinstance(temp[-1], list) and self.isSymbol(temp[-1]):
                arrayName = temp.pop()
                temp.append(["ARRAY", arrayName])
                isArray = True

            # Check if function
            if index + 1 < len(tokens) and tokens[index + 1]["symbol"] == "(" and \
               not isinstance(temp[-1], list) and self.isSymbol(temp[-1]):
                arrayName = temp.pop()
                temp.append(["FUNCTION", arrayName])
                isFunction = True

            if tokens[index]["types"] == "LEFTPAREN":
                index, t = self.expSolver(tokens, index + 1)

                if isFunction:
                    params = [[]]

                    # Split params by comma (,).
                    for factor in t:
                        if factor == ",": params.append([])
                        else: params[-1].append(factor)

                    params.insert(0, len(params))

                    temp[-1].extend(params)
                    isFunction = False

                else: temp.append(t)

            elif tokens[index]["types"] == "RIGHTPAREN":
                break

            elif tokens[index]["types"] == "LEFTBRACKET":
                index, t = self.expSolver(tokens, index + 1)

                if isArray:
                    temp[-1].append(t)
                    isArray = False

                else: temp.append(t)

            elif tokens[index]["types"] == "RIGHTBRACKET":
                break

            index += 1

        return index, temp

    def defSolver(self, tokens: list, index: int):
        temp = []

        if tokens[index]["types"] not in ["DEF_INTEGER", "DEF_FLOAT", "DEF_STRING", "DEF_BOOL"]:
            E.throw(2, 2, "Definition must start with 'int', 'float', 'string', or 'bool'.")
        else: temp.append(tokens[index]["types"])

        index += 1

        if tokens[index]["types"] != "SYMBOL": E.throw(2, 2, "Parameter must be a symbol.")
        else: temp.append(tokens[index]["symbol"])

        index += 1

        # Check if an array.
        params = []
        while tokens[index]["types"] == "LEFTBRACKET":
            index += 1
            index, t = self.expSolver(tokens, index)
            params.append(t)

            if tokens[index]["types"] != "RIGHTBRACKET": E.throw(2, 2, "There must be a close bracket (]).", "Add a close bracket.")
            index += 1

        if params: temp.append(params)

        print(temp)