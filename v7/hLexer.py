from errorHandler import Error

E = Error()

DIGITS_0_9 = "0123456789"
DIGITS_1_9 = "123456789"
CHAR_a_zA_Z = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
CHAR_a_zA_Z0_9 = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"

INTEGER = "INTEGER"
FLOAT = "FLOAT"
STRING = "STRING"
BOOL = "BOOL"
SYMBOL = "SYMBOL"
COMMENT = "COMMENT"

DEF_INTEGER = "DEF_INTEGER"
DEF_FLOAT = "DEF_FLOAT"
DEF_STRING = "DEF_STRING"
DEF_BOOL = "DEF_BOOL"
DEF_FUNCTION = "DEF_FUNCTION"

IF = "IF"
ELSE = "ELSE"
ELIF = "ELIF"
WHILE = "WHILE"
FOR = "FOR"
BREAK = "BREAK"
LOGICAND = "LOGICAND"
LOGICOR = "LOGICOR"
LOGICNOT = "LOGICNOT"

MINUS = "MINUS"
MINUSSELF = "MINUSSELF"
PLUS = "PLUS"
PLUSSELF = "PLUSSELF"
DIVIDE = "DIVIDE"
SELFOPERATOR = "OPERATOR"
MULTUPLE = "MULTIPE"
EXP = "EXP"
REMAIN = "REMAIN"
BITOR = "BITOR"
BITAND = "BITAND"
BITXOR = "BITXOR"
ASSIGN = "ASSIGN"
EQUAL = "EQUAL"
GREATERTHAN="GREATERTHAN"
LESSTHAN = "LESSTHAN"
BITLEFTSHIFT = "BITLEFTSHIFT"
BITRIGHTSHIFT = "BITRIGHTSHIFT"
NOTEQUAL = "NOTEQUAL"
SEMICOLON = "SEMICOLON"
COMMA = "COMMA"
DOT = "DOT"
LEFTPAREN = "LEFTPAREN"
RIGHTPAREN = "RIGHTPAREN"
LEFTBRACKET = "LEFTBRACKET"
RIGHTBRACKET = "RIGHTBRACKET"
LEFTBRACE = "LEFTBRACE"
RIGHTBRACE = "RIGHTBRACE"

class Lexer:
    def __init__(self, raw) -> None:
        self.raw = raw + "\n;"
        self.index = -1
        self.rawLength = len(self.raw)
        self.status = 0
        self.token = ""
        self.currentChar = ""
        self.tokenList = []

    def getTokens(self) -> list:
        while self.index + 1 < self.rawLength:
            self.index += 1
            self.currentChar = self.raw[self.index]

            match (self.status):
                case 0: self.status0()
                case 1: self.status1()
                case 2: self.status2()
                case 3: self.status3()
                case 4: self.status4()
                case 5: self.status5()
                case 6: self.status6()
                case 7: self.status7()
                case 8: self.status8()
                case 9: self.status9()
                case 10: self.status10()
                case 11: self.status11()
                case 12: self.status12()
                case 13: self.status13()
                case 14: self.status14()
                case 15: self.status15()
                case 16: self.status16()
                case 17: self.status17()
                case 18: self.status18()
                case 19: self.status19()
                case 20: self.status20()
                case 21: self.status21()
                case 22: self.status22()
                case 23: self.status23()
                case 24: self.status24()
                case 25: self.status25()
                case 26: self.status26()
                case 27: self.status27()
                case 28: self.status28()
                case 29: self.status29()
                # case 30: self.status30() # Descarded
                case 31: self.status31()
                case 32: self.status32()
                case 33: self.status33()
                case 34: self.status34()
                case 35: self.status35()
                case 36: self.status36()
                case 37: self.status37()
                case 38: self.status38()
                case 39: self.status39()
                case _: self.status0()

        return self.tokenList

    def makeToken(self, types: str) -> None:
        self.tokenList.append({"types": types, "symbol": self.token})
        self.index -= 1
        self.status = 0
        self.token = ""

    def status0(self) -> None:
        if self.currentChar == "0":
            self.token += self.currentChar
            self.status = 1
        elif self.currentChar in DIGITS_1_9:
            self.token += self.currentChar
            self.status = 4
        elif self.currentChar == "\"":
            self.token += self.currentChar
            self.status = 5
        elif self.currentChar in CHAR_a_zA_Z:
            self.token += self.currentChar
            self.status = 7
        elif self.currentChar == "-":
            self.token += self.currentChar
            self.status = 8
        elif self.currentChar == "+":
            self.token += self.currentChar
            self.status = 10
        elif self.currentChar == "/":
            self.token += self.currentChar
            self.status = 12
        elif self.currentChar == "*":
            self.token += self.currentChar
            self.status = 17
        elif self.currentChar == "%":
            self.token += self.currentChar
            self.status = 19
        elif self.currentChar == "|":
            self.token += self.currentChar
            self.status = 20
        elif self.currentChar == "&":
            self.token += self.currentChar
            self.status = 21
        elif self.currentChar == "^":
            self.token += self.currentChar
            self.status = 22
        elif self.currentChar == "=":
            self.token += self.currentChar
            self.status = 23
        elif self.currentChar == ">":
            self.token += self.currentChar
            self.status = 24
        elif self.currentChar == "<":
            self.token += self.currentChar
            self.status = 26
        elif self.currentChar == "!":
            self.token += self.currentChar
            self.status = 28
        elif self.currentChar == ";":
            self.token += self.currentChar
            self.status = 31
        elif self.currentChar == ",":
            self.token += self.currentChar
            self.status = 32
        elif self.currentChar == ".":
            self.token += self.currentChar
            self.status = 33
        elif self.currentChar == "(":
            self.token += self.currentChar
            self.status = 34
        elif self.currentChar == ")":
            self.token += self.currentChar
            self.status = 35
        elif self.currentChar == "[":
            self.token += self.currentChar
            self.status = 36
        elif self.currentChar == "]":
            self.token += self.currentChar
            self.status = 37
        elif self.currentChar == "{":
            self.token += self.currentChar
            self.status = 38
        elif self.currentChar == "}":
            self.token += self.currentChar
            self.status = 39

    def status1(self) -> None:
        if self.currentChar == ".":
            self.token += self.currentChar
            self.status = 2
        elif self.currentChar == "0":
            E.throw(2, 1, "Get 0 after 0.", "Remove duplicated 0s.")
        else:
            self.makeToken(INTEGER)

    def status2(self) -> None:
        if self.currentChar in DIGITS_0_9:
            self.token += self.currentChar
            self.status = 3
        else:
            E.throw(1, 1, "There must be integers after '0.' symbol.")

    def status3(self) -> None:
        if self.currentChar in DIGITS_0_9:
            self.token += self.currentChar
            self.status = 3
        else:
            self.makeToken(FLOAT)

    def status4(self) -> None:
        if self.currentChar in DIGITS_0_9:
            self.token += self.currentChar
            self.status = 4
        elif self.currentChar  == ".":
            self.token += self.currentChar
            self.status = 2
        else:
            self.makeToken(INTEGER)

    def status5(self) -> None:
        if self.currentChar == "\"":
            self.token += self.currentChar
            self.index += 1
            self.makeToken(STRING)
        elif self.currentChar == "\\":
            self.token += self.currentChar
            self.status = 6
        else:
            self.token += self.currentChar
            self.status = 5

    def status6(self) -> None:
        self.token += self.currentChar
        self.status = 5

    def status7(self) -> None:
        if self.currentChar in CHAR_a_zA_Z0_9:
            self.token += self.currentChar
            self.status = 7
        else:
            match (self.token):
                case "int": self.makeToken(DEF_INTEGER)
                case "float": self.makeToken(DEF_FLOAT)
                case "string": self.makeToken(DEF_STRING)
                case "bool": self.makeToken(DEF_BOOL)
                case "function": self.makeToken(DEF_FUNCTION)
                case "if": self.makeToken(IF)
                case "else": self.makeToken(ELSE)
                case "elif": self.makeToken(ELIF)
                case "while": self.makeToken(WHILE)
                case "for": self.makeToken(FOR)
                case "and": self.makeToken(LOGICAND)
                case "or": self.makeToken(LOGICOR)
                case "not": self.makeToken(LOGICNOT)
                case "true": self.makeToken(BOOL)
                case "false": self.makeToken(BOOL)
                case "break": self.makeToken(BREAK)
                case _: self.makeToken(SYMBOL)

    def status8(self) -> None:
        if self.currentChar in DIGITS_1_9:
            self.token += self.currentChar
            self.status = 4
        elif self.currentChar == "0":
            self.token += self.currentChar
            self.status = 1
        elif self.currentChar == "-":
            self.token += self.currentChar
            self.status = 9
        elif self.currentChar == "=":
            self.token += self.currentChar
            self.status = 16
        else:
            self.makeToken(MINUS)

    def status9(self) -> None:
        self.makeToken(MINUSSELF)

    def status10(self) -> None:
        if self.currentChar == "+":
            self.token += self.currentChar
            self.status = 11
        elif self.currentChar == "=":
            self.token += self.currentChar
            self.status = 16
        else:
            self.makeToken(PLUS)

    def status11(self) -> None:
        self.makeToken(PLUSSELF)

    def status12(self) -> None:
        if self.currentChar == "/":
            self.token += self.currentChar
            self.status = 13
        elif self.currentChar == "*":
            self.token += self.currentChar
            self.status = 14
        elif self.currentChar == "=":
            self.token += self.currentChar
            self.status = 16
        else:
            self.makeToken(DIVIDE)

    def status13(self) -> None:
        if self.currentChar == "\n":
            self.makeToken(COMMENT)
        else:
            self.token += self.currentChar
            self.status = 13

    def status14(self) -> None:
        if self.currentChar == "*":
            self.token += self.currentChar
            self.status = 15
        else:
            self.token += self.currentChar
            self.status = 14

    def status15(self) -> None:
        if self.currentChar == "/":
            self.token += self.currentChar
            self.index += 1
            self.makeToken(COMMENT)
        else:
            self.token += self.currentChar
            self.status = 14

    def status16(self) -> None:
        self.makeToken(SELFOPERATOR)

    def status17(self) -> None:
        if self.currentChar == "*":
            self.token += self.currentChar
            self.status = 18
        elif self.currentChar == "=":
            self.token += self.currentChar
            self.status = 16
        else:
            self.makeToken(MULTUPLE)

    def status18(self) -> None:
        if self.currentChar == "=":
            self.token += self.currentChar
            self.status = 16
        else:
            self.makeToken(EXP)

    def status19(self) -> None:
        if self.currentChar == "=":
            self.token += self.currentChar
            self.status = 16
        else:
            self.makeToken(REMAIN)

    def status20(self) -> None:
        if self.currentChar == "=":
            self.token += self.currentChar
            self.status = 16
        else:
            self.makeToken(BITOR)

    def status21(self) -> None:
        if self.currentChar == "=":
            self.token += self.currentChar
            self.status = 16
        else:
            self.makeToken(BITAND)

    def status22(self) -> None:
        if self.currentChar == "=":
            self.token += self.currentChar
            self.status = 16
        else:
            self.makeToken(BITXOR)

    def status23(self) -> None:
        if self.currentChar == "=":
            self.token += self.currentChar
            self.status = 16
        else:
            self.index += 1
            self.makeToken(ASSIGN)

    def status24(self) -> None:
        if self.currentChar == "=":
            self.token += self.currentChar
            self.status = 16
        elif self.currentChar == ">":
            self.token += self.currentChar
            self.status = 25
        else:
            self.makeToken(GREATERTHAN)

    def status25(self) -> None:
        if self.currentChar == "=":
            self.token += self.currentChar
            self.status = 16
        else:
            self.makeToken(BITRIGHTSHIFT)

    def status26(self) -> None:
        if self.currentChar == "=":
            self.token += self.currentChar
            self.status = 16
        elif self.currentChar == "<":
            self.token += self.currentChar
            self.status = 27
        else:
            self.makeToken(LESSTHAN)

    def status27(self) -> None:
        if self.currentChar == "=":
            self.token += self.currentChar
            self.status = 16
        else:
            self.makeToken(BITLEFTSHIFT)

    def status28(self) -> None:
        if self.currentChar == "=":
            self.token += self.currentChar
            self.status = 29
        else:
            E.throw(1, 1, "There is no symbol '!'.", "Did you mean '!=='?")

    def status29(self) -> None:
        if self.currentChar == "=":
            self.token += self.currentChar
            self.index += 1
            self.makeToken(NOTEQUAL)
        else:
            E.throw(1, 1, "There is no symbol '!='.", "Did you mean '!=='?")

    def status31(self) -> None:
        self.makeToken(SEMICOLON)

    def status32(self) -> None:
        self.makeToken(COMMA)

    def status33(self) -> None:
        self.makeToken(DOT)

    def status34(self) -> None:
        self.makeToken(LEFTPAREN)

    def status35(self) -> None:
        self.makeToken(RIGHTPAREN)

    def status36(self) -> None:
        self.makeToken(LEFTBRACKET)

    def status37(self) -> None:
        self.makeToken(RIGHTBRACKET)

    def status38(self) -> None:
        self.makeToken(LEFTBRACE)

    def status39(self) -> None:
        self.makeToken(RIGHTBRACE)