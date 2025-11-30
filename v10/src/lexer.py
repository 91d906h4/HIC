import re

class TokenType:
    INTEGER = 'INTEGER'
    ID = 'ID'
    KEYWORD = 'KEYWORD'
    PLUS = 'PLUS'
    MINUS = 'MINUS'
    MUL = 'MUL'
    DIV = 'DIV'
    LPAREN = 'LPAREN'
    RPAREN = 'RPAREN'
    LBRACE = 'LBRACE'
    RBRACE = 'RBRACE'
    LBRACKET = 'LBRACKET'
    RBRACKET = 'RBRACKET'
    SEMICOLON = 'SEMICOLON'
    ASSIGN = 'ASSIGN'
    EQ = 'EQ'
    NEQ = 'NEQ'
    LT = 'LT'
    GT = 'GT'
    LE = 'LE'
    GE = 'GE'
    COMMA = 'COMMA'
    COLON = 'COLON'
    EOF = 'EOF'
    STRING = 'STRING'
    AND = 'AND'
    OR = 'OR'
    NOT = 'NOT'
    TRUE = 'TRUE'
    FALSE = 'FALSE'
    NONE = 'NONE'
    DOT = 'DOT'
    PLUSPLUS = 'PLUSPLUS'
    MINUSMINUS = 'MINUSMINUS'
    PLUSEQ = 'PLUSEQ'
    MINUSEQ = 'MINUSEQ'
    MULEQ = 'MULEQ'
    DIVEQ = 'DIVEQ'

class Token:
    def __init__(self, type, value):
        self.type = type
        self.value = value

    def __repr__(self):
        return f'Token({self.type}, {repr(self.value)})'

class Lexer:
    def __init__(self, text):
        self.text = text
        self.pos = 0
        self.current_char = self.text[self.pos] if self.text else None

    def error(self):
        raise Exception(f'Invalid character at position {self.pos}: {self.current_char}')

    def advance(self):
        self.pos += 1
        if self.pos > len(self.text) - 1:
            self.current_char = None
        else:
            self.current_char = self.text[self.pos]

    def peek(self):
        peek_pos = self.pos + 1
        if peek_pos > len(self.text) - 1:
            return None
        else:
            return self.text[peek_pos]

    def skip_whitespace(self):
        while self.current_char is not None and self.current_char.isspace():
            self.advance()

    def skip_comment(self):
        while self.current_char is not None and self.current_char != '\n':
            self.advance()
        self.advance()

    def skip_multiline_comment(self):
        self.advance() # /
        self.advance() # *
        while self.current_char is not None:
            if self.current_char == '*' and self.peek() == '/':
                self.advance()
                self.advance()
                break
            self.advance()

    def number(self):
        result = ''
        while self.current_char is not None and self.current_char.isdigit():
            result += self.current_char
            self.advance()
        
        # Check for decimal point
        if self.current_char == '.' and self.peek() and self.peek().isdigit():
            result += self.current_char
            self.advance()
            while self.current_char is not None and self.current_char.isdigit():
                result += self.current_char
                self.advance()
        
        return int(result) if '.' not in result else float(result)

    def string(self, quote_char):
        result = ''
        self.advance()  # Skip opening quote
        while self.current_char is not None and self.current_char != quote_char:
            if self.current_char == '\\':
                # Handle escape sequences
                self.advance()
                if self.current_char == 'n':
                    result += '\n'
                elif self.current_char == 't':
                    result += '\t'
                elif self.current_char == 'r':
                    result += '\r'
                elif self.current_char == '\\':
                    result += '\\'
                elif self.current_char == '"':
                    result += '"'
                elif self.current_char == "'":
                    result += "'"
                else:
                    result += self.current_char
                self.advance()
            else:
                result += self.current_char
                self.advance()
        self.advance()  # Skip closing quote
        return result

    def _id(self):
        result = ''
        while self.current_char is not None and (self.current_char.isalnum() or self.current_char == '_'):
            result += self.current_char
            self.advance()
        
        keywords = {
            'function': TokenType.KEYWORD,
            'return': TokenType.KEYWORD,
            'if': TokenType.KEYWORD,
            'else': TokenType.KEYWORD,
            'while': TokenType.KEYWORD,
            'for': TokenType.KEYWORD,
            'var': TokenType.KEYWORD,
            'import': TokenType.KEYWORD,
            'true': TokenType.TRUE,
            'false': TokenType.FALSE,
            'none': TokenType.NONE,
            'break': TokenType.KEYWORD,
            'continue': TokenType.KEYWORD,
            'try': TokenType.KEYWORD,
            'catch': TokenType.KEYWORD,
            'throw': TokenType.KEYWORD,
            'class': TokenType.KEYWORD,
            'this': TokenType.KEYWORD,
        }
        
        token_type = keywords.get(result, TokenType.ID)
        return Token(token_type, result)

    def get_next_token(self):
        while self.current_char is not None:
            if self.current_char.isspace():
                self.skip_whitespace()
                continue

            if self.current_char == '/':
                if self.peek() == '/':
                    self.skip_comment()
                    continue
                elif self.peek() == '*':
                    self.skip_multiline_comment()
                    continue
                elif self.peek() == '=':
                    self.advance()
                    self.advance()
                    return Token(TokenType.DIVEQ, '/=')
                else:
                    self.advance()
                    return Token(TokenType.DIV, '/')

            if self.current_char.isdigit():
                return Token(TokenType.INTEGER, self.number())

            if self.current_char == '"':
                return Token(TokenType.STRING, self.string('"'))
            
            if self.current_char == "'":
                return Token(TokenType.STRING, self.string("'"))

            if self.current_char.isalpha() or self.current_char == '_':
                return self._id()

            if self.current_char == '+':
                if self.peek() == '+':
                    self.advance()
                    self.advance()
                    return Token(TokenType.PLUSPLUS, '++')
                elif self.peek() == '=':
                    self.advance()
                    self.advance()
                    return Token(TokenType.PLUSEQ, '+=')
                self.advance()
                return Token(TokenType.PLUS, '+')

            if self.current_char == '-':
                if self.peek() == '-':
                    self.advance()
                    self.advance()
                    return Token(TokenType.MINUSMINUS, '--')
                elif self.peek() == '=':
                    self.advance()
                    self.advance()
                    return Token(TokenType.MINUSEQ, '-=')
                self.advance()
                return Token(TokenType.MINUS, '-')

            if self.current_char == '*':
                if self.peek() == '=':
                    self.advance()
                    self.advance()
                    return Token(TokenType.MULEQ, '*=')
                self.advance()
                return Token(TokenType.MUL, '*')

            if self.current_char == '/':
                # Handled above for comments
                pass

            if self.current_char == '(':
                self.advance()
                return Token(TokenType.LPAREN, '(')

            if self.current_char == ')':
                self.advance()
                return Token(TokenType.RPAREN, ')')

            if self.current_char == '{':
                self.advance()
                return Token(TokenType.LBRACE, '{')

            if self.current_char == '}':
                self.advance()
                return Token(TokenType.RBRACE, '}')
            
            if self.current_char == '[':
                self.advance()
                return Token(TokenType.LBRACKET, '[')

            if self.current_char == ']':
                self.advance()
                return Token(TokenType.RBRACKET, ']')

            if self.current_char == ';':
                self.advance()
                return Token(TokenType.SEMICOLON, ';')
            
            if self.current_char == ',':
                self.advance()
                return Token(TokenType.COMMA, ',')

            if self.current_char == ':':
                self.advance()
                return Token(TokenType.COLON, ':')

            if self.current_char == '=':
                if self.peek() == '=':
                    self.advance()
                    self.advance()
                    return Token(TokenType.EQ, '==')
                self.advance()
                return Token(TokenType.ASSIGN, '=')
            
            if self.current_char == '!':
                if self.peek() == '=':
                    self.advance()
                    self.advance()
                    return Token(TokenType.NEQ, '!=')
                self.advance()
                return Token(TokenType.NOT, '!')

            if self.current_char == '<':
                if self.peek() == '=':
                    self.advance()
                    self.advance()
                    return Token(TokenType.LE, '<=')
                self.advance()
                return Token(TokenType.LT, '<')

            if self.current_char == '>':
                if self.peek() == '=':
                    self.advance()
                    self.advance()
                    return Token(TokenType.GE, '>=')
                self.advance()
                return Token(TokenType.GT, '>')

            if self.current_char == '&':
                if self.peek() == '&':
                    self.advance()
                    self.advance()
                    return Token(TokenType.AND, '&&')
                self.error()

            if self.current_char == '|':
                if self.peek() == '|':
                    self.advance()
                    self.advance()
                    return Token(TokenType.OR, '||')
                self.error()

            if self.current_char == '.':
                self.advance()
                return Token(TokenType.DOT, '.')

            self.error()

        return Token(TokenType.EOF, None)

    def peek_token(self):
        saved_pos = self.pos
        saved_char = self.current_char
        token = self.get_next_token()
        self.pos = saved_pos
        self.current_char = saved_char
        return token
