import re
from errorHandler import Error

E = Error()

class Parser:
    def __init__(self, tokens: list) -> None:
        self.tokens = tokens

        # _, t = self.expSolver(tokens, 5)

        # _, t = self.defSolver(tokens, 5)

        _, t = self.defFunction(tokens, 6)

        print(t)
    
    def isSymbol(self, token: str) -> bool:
        keywords = ["if", "else", "elif", "for", "while", "break", "int", "float", "string", "bool", "function", "true", "false", "and", "or", "not"]
        return re.match(r"[_a-zA-Z][_a-zA-Z0-9]*", token) and token not in keywords

    def termSolver(self, tokens: list, index: int):
        pass

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
            if tokens[index]["types"] != "INTEGER": E.throw(2, 2, "Size of array must be an integer.")
            params.append(int(tokens[index]["symbol"]))
            index += 1

            if tokens[index]["types"] != "RIGHTBRACKET": E.throw(2, 2, "There must be a close bracket (]).", "Add a close bracket.")
            index += 1

        if tokens[index]["types"] == "ASSIGN": index += 1
        elif tokens[index]["types"] == "SEMICOLON":
            if params: temp.append(params)
            return index, temp

        if params:
            temp.append(params)

            # Anonymous array.
            tokens.insert(index, {"types": "SYMBOL", "symbol": "anonymous"})
            
            index, t = self.expSolver(tokens, index)
            temp.append(t[0][2])
        else:
            index, t = self.expSolver(tokens, index)
            temp.append(t)

        return index, temp

    def defFunction(self, tokens: list, index: int):
        temp = []

        if tokens[index]["types"] != "DEF_FUNCTION":
            E.throw(2, 2, "Definition must start with 'function'.")
        else: temp.append(tokens[index]["types"])

        index += 1

        if tokens[index]["types"] != "SYMBOL": E.throw(2, 2, "Parameter must be a symbol.")
        else: temp.append(tokens[index]["symbol"])

        index += 1

        params = []
        while tokens[index]["types"] != "RIGHTPAREN":
            index += 1
            if tokens[index]["types"] == "SYMBOL": params.append(tokens[index]["symbol"])

        temp.append(params)

        print(tokens)

        return index, temp