"""
Status:
    (0) Start
    (1) First zero
    (2) Dot after zero
"""
 
from errorHandler import Error

DIGITS_0_9 = "0123456789"
DIGITS_1_9 = "123456789"

INTEGER = "INTEGER"
FLOAT = "FLOAT"

class Lexer:
    def __init__(self, raw) -> None:
        self.raw = raw + ";"
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

    def status1(self) -> None:
        if self.currentChar == ".":
            self.token += self.currentChar
            self.status = 2
        elif self.currentChar == "0":
            Error().throw(2, 1, "Get 0 after 0.", "Remove duplicated 0s.")
        else:
            self.makeToken(INTEGER)

    def status2(self) -> None:
        if self.currentChar in DIGITS_0_9:
            self.token += self.currentChar
            self.status = 3
        else:
            Error().throw(1, 1, "There must be integers after '0.' symbol.")

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