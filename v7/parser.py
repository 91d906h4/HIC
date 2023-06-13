import re
from errorHandler import Error

E = Error()

class Parser:
    def __init__(self, tokens: list) -> None:
        self.tokens = tokens

        _ = self.termSolver(0)
    
    def isSymbol(self, token: str) -> bool:
        keywords = ["if", "else", "elif", "for", "while", "break", "int", "float", "string", "bool", "function", "true", "false", "and", "or", "not"]
        return re.match(r"[_a-zA-Z][_a-zA-Z0-9]*", token) and token not in keywords

    def termSolver(self, index: int):
        while index < len(self.tokens):
            if self.tokens[index]["types"] == "COMMENT":
                index += 1
                continue

            elif self.tokens[index]["types"] == "LEFTBRACE":
                index += 1
                index = self.termSolver(index)

            elif self.tokens[index]["types"] == "RIGHTBRACE":
                break

            elif self.tokens[index]["types"] == "DEF_FUNCTION":
                index, t = self.functionSolver(index)

            elif self.tokens[index]["types"] in ["DEF_INTEGER", "DEF_FLOAT", "DEF_STRING", "DEF_BOOL"]:
                index, t = self.defSolver(index)

            elif self.tokens[index]["types"] == "IF":
                index, t = self.ifSolver(index)

            elif self.tokens[index]["types"] in ["ELSE", "ELIF"]:
                E.throw(2, 2, "There must be an 'if' statement before 'elif' or 'else'.")

            elif self.tokens[index]["types"] == "FOR":
                index, t = self.forSolver(index)

            elif self.tokens[index]["types"] == "WHILE":
                index, t = self.whileSolver(index)

            else:
                index, t = self.expSolver(index)

            index += 1
        
        return index

    def expSolver(self, index: int):
        temp, isArray, isFunction = [], False, False

        while index < len(self.tokens):
            if self.tokens[index]["types"] == "SEMICOLON": break

            if self.tokens[index]["types"] == "COMMENT":
                index += 1
                continue

            if self.tokens[index]["types"] not in ["LEFTPAREN", "RIGHTPAREN", "LEFTBRACKET", "RIGHTBRACKET"]: temp.append(self.tokens[index]["symbol"])

            # Check if array.
            if index + 1 < len(self.tokens) and self.tokens[index + 1]["symbol"] == "[" and \
               not isinstance(temp[-1], list) and self.isSymbol(temp[-1]):
                arrayName = temp.pop()
                temp.append(["ARRAY", arrayName])
                isArray = True

            # Check if function
            if index + 1 < len(self.tokens) and self.tokens[index + 1]["symbol"] == "(" and \
               not isinstance(temp[-1], list) and self.isSymbol(temp[-1]):
                arrayName = temp.pop()
                temp.append(["FUNCTION", arrayName])
                isFunction = True

            if self.tokens[index]["types"] == "LEFTPAREN":
                index, t = self.expSolver(index + 1)

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

            elif self.tokens[index]["types"] == "RIGHTPAREN": break

            elif self.tokens[index]["types"] == "LEFTBRACKET":
                index, t = self.expSolver(index + 1)

                if isArray:
                    temp[-1].append(t)
                    isArray = False

                else: temp.append(t)

            elif self.tokens[index]["types"] == "RIGHTBRACKET": break

            index += 1

        return index, temp

    def defSolver(self, index: int):
        temp = []

        # If the definition statement is empty (e.g. for (;;) {...}), return an empty list.
        if self.tokens[index]["types"] == "SEMICOLON": return index, temp

        if self.tokens[index]["types"] not in ["DEF_INTEGER", "DEF_FLOAT", "DEF_STRING", "DEF_BOOL"]:
            E.throw(2, 2, "Definition must start with 'int', 'float', 'string', or 'bool'.")
        else: temp.append(self.tokens[index]["types"])

        index += 1

        # Check if the parameter name is legal (a symbol).
        if self.tokens[index]["types"] != "SYMBOL": E.throw(2, 2, "Parameter must be a symbol.")
        else: temp.append(self.tokens[index]["symbol"])

        index += 1

        # Check if an array.
        params = []
        while self.tokens[index]["types"] == "LEFTBRACKET":
            index += 1
            if self.tokens[index]["types"] != "INTEGER": E.throw(2, 2, "Size of array must be an integer.")
            params.append(int(self.tokens[index]["symbol"]))
            index += 1

            if self.tokens[index]["types"] != "RIGHTBRACKET": E.throw(2, 2, "There must be a close bracket (]).", "Add a close bracket.")
            index += 1

        # Check if any value given.
        if self.tokens[index]["types"] == "ASSIGN": index += 1
        elif self.tokens[index]["types"] == "SEMICOLON":
            if params: temp.append(params)
            return index, temp

        # Check if an array. If the 'params' is not empty, it means it is an array.
        if params:
            temp.append(params)

            # Anonymous array.
            # To define an array, we re-use the expSolver to parse the value,
            # but the expSolver require a name before an array, so we give it
            # an 'anonymous' array name.
            self.tokens.insert(index, {"types": "SYMBOL", "symbol": "anonymous"})
            
            index, t = self.expSolver(index)
            temp.append(t[0][2])
        else:
            index, t = self.expSolver(index)
            temp.append(t)

        return index, temp

    def functionSolver(self, index: int):
        temp = []

        index += 1

        if self.tokens[index]["types"] != "SYMBOL": E.throw(2, 2, "Parameter must be a symbol.")
        else: temp.append(self.tokens[index]["symbol"])

        index += 1

        params = []
        while self.tokens[index]["types"] != "RIGHTPAREN":
            index += 1
            if self.tokens[index]["types"] == "SYMBOL": params.append(self.tokens[index]["symbol"])

        temp.append(params)

        index += 2

        index = self.termSolver(index)

        return index, temp
    
    def ifSolver(self, index: int):
        temp = []

        index += 1

        # if self.tokens[index]["types"] != "LEFTPAREN":
        #     E.throw(2, 2, "There must be a open paren after 'if'.", "Use syntax 'if (...) {...}.'")

        index += 1

        index, temp = self.expSolver(index)
        index += 2

        index = self.termSolver(index)
        
        while self.tokens[index + 1]["types"] in ["ELSE", "ELIF"]:
            if self.tokens[index + 1]["types"] == "ELIF":
                index += 3

                index, temp = self.expSolver(index)
                index += 2

                index = self.termSolver(index)
            else:
                index += 3

                index = self.termSolver(index)

                break

        return index, temp

    def forSolver(self, index: int):
        temp = []

        index += 2

        # Get the first part (initialization) of for-loop.
        index, t = self.defSolver(index)

        index += 1

        # Get the second part (condition) of for-loop.
        index, t = self.expSolver(index)

        index += 1

        # Get the third part (increment/decrement) of for-loop.
        index, t = self.expSolver(index)

        index += 2

        index = self.termSolver(index)

        return index, temp

    def whileSolver(self, index: int):
        temp = []

        index += 2

        index, t = self.expSolver(index)

        index += 2

        index = self.termSolver(index)

        return index, temp