class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def match(self, expected_type):
        """Check and consume the expected token"""
        if self.pos < len(self.tokens) and self.tokens[self.pos][0] == expected_type:
            self.pos += 1
            return self.tokens[self.pos - 1]
        return None

    def factor(self):
        """factor -> NUMBER | ID | ( expr ) | function_call"""
        if token := self.match("NUMBER"):
            return {"type": "NUMBER", "value": token[1]}
        elif token := self.match("ID"):
            if self.match("LPAREN"):  # Function call
                args = []
                if not self.match("RPAREN"):  # Check for empty args
                    args.append(self.expr())
                    while self.match("COMMA"):
                        args.append(self.expr())
                    if not self.match("RPAREN"):
                        raise SyntaxError("Expected closing parenthesis in function call")
                return {"type": "FUNC_CALL", "name": token[1], "args": args}
            return {"type": "VAR", "name": token[1]}
        elif self.match("LPAREN"):
            node = self.expr()
            if not self.match("RPAREN"):
                raise SyntaxError("Expected closing parenthesis")
            return node
        else:
            raise SyntaxError(f"Unexpected token: {self.tokens[self.pos]}")

    def term(self):
        """term -> factor ( ("*" | "/") factor )*"""
        node = self.factor()
        while (op := self.match("MULT")) or (op := self.match("DIV")):
            node = {"type": "BIN_OP", "op": op[1], "left": node, "right": self.factor()}
        return node

    def expr(self):
        """expr -> term ( ("+" | "-") term )*"""
        node = self.term()
        while (op := self.match("PLUS")) or (op := self.match("MINUS")):
            node = {"type": "BIN_OP", "op": op[1], "left": node, "right": self.term()}
        return node

    def assignment(self):
        """assignment -> ID "=" expr"""
        var_name = self.match("ID")
        if not var_name or not self.match("ASSIGN"):
            raise SyntaxError("Expected assignment of the form 'var = value;'")
        value = self.expr()
        return {"type": "ASSIGN", "var": var_name[1], "value": value}

    def if_stmt(self):
        """if_stmt -> "if" "(" expr ")" "{" statement* "}" ( "elif" "(" expr ")" "{" statement* "}" )? ( "else" "{" statement* "}" )?"""
        if not self.match("IF"):
            return None
        if not self.match("LPAREN"):
            raise SyntaxError("Expected '(' after 'if'")
        condition = self.expr()
        if not self.match("RPAREN"):
            raise SyntaxError("Expected ')' after condition")
        if not self.match("LBRACE"):
            raise SyntaxError("Expected '{' after 'if' condition")
        
        true_branch = self.statements()
        if not self.match("RBRACE"):
            raise SyntaxError("Expected '}' after 'if' block")
        
        false_branch = None
        if self.match("ELSE"):
            if not self.match("LBRACE"):
                raise SyntaxError("Expected '{' after 'else'")
            false_branch = self.statements()
            if not self.match("RBRACE"):
                raise SyntaxError("Expected '}' after 'else' block")

        return {"type": "IF", "condition": condition, "true_branch": true_branch, "false_branch": false_branch}

    def statement(self):
        """statement -> expr ";" | assignment ";" | if_stmt"""
        if self.pos >= len(self.tokens):
            return None
        if self.tokens[self.pos][0] == "IF":
            return self.if_stmt()
        if self.tokens[self.pos][0] == "ID" and self.tokens[self.pos + 1][0] == "ASSIGN":
            stmt = self.assignment()
            if not self.match("SEMICOLON"):
                raise SyntaxError("Expected ';' after assignment")
            return stmt
        stmt = self.expr()
        if not self.match("SEMICOLON"):
            raise SyntaxError("Expected ';' after expression")
        return stmt

    def statements(self):
        """program -> statement*"""
        stmts = []
        while self.pos < len(self.tokens):
            stmt = self.statement()
            if stmt:
                stmts.append(stmt)
        return stmts

    def parse(self):
        return self.statements()


if __name__ == "__main__":
    tokens = [
        ("NUMBER", "3"), ("PLUS", "+"), ("NUMBER", "5"),
        ("MULT", "*"), ("LPAREN", "("), ("NUMBER", "10"),
        ("MINUS", "-"), ("NUMBER", "2"), ("RPAREN", ")")
    ]
    parser = Parser(tokens)
    ast = parser.parse()
    print(ast)
