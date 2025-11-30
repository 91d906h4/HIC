from lexer import TokenType, Token

class AST:
    pass

class Program(AST):
    def __init__(self, statements):
        self.statements = statements

class FunctionDef(AST):
    def __init__(self, name, params, body):
        self.name = name
        self.params = params # list of (type, name)
        self.body = body

class VarDecl(AST):
    def __init__(self, type_name, name, size=None):
        self.type_name = type_name
        self.name = name
        self.size = size # For arrays

class Assign(AST):
    def __init__(self, left, right):
        self.left = left
        self.right = right

class BinOp(AST):
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right

class Num(AST):
    def __init__(self, token):
        self.token = token
        self.value = token.value

class String(AST):
    def __init__(self, token):
        self.token = token
        self.value = token.value

class BoolLiteral(AST):
    def __init__(self, token):
        self.token = token
        self.value = token.type == TokenType.TRUE

class NoneLiteral(AST):
    def __init__(self):
        self.value = None

class UnaryOp(AST):
    def __init__(self, op, expr):
        self.op = op
        self.expr = expr

class Var(AST):
    def __init__(self, token):
        self.token = token
        self.value = token.value

class FunctionCall(AST):
    def __init__(self, name, args, kwargs=None, obj=None):
        self.name = name
        self.args = args
        self.kwargs = kwargs if kwargs is not None else [] # list of (name, value) tuples
        self.obj = obj  # For method calls like math.sqrt()

class Return(AST):
    def __init__(self, expr):
        self.expr = expr

class If(AST):
    def __init__(self, condition, true_body, false_body=None):
        self.condition = condition
        self.true_body = true_body
        self.false_body = false_body

class While(AST):
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body

class For(AST):
    def __init__(self, init, condition, update, body):
        self.init = init
        self.condition = condition
        self.update = update
        self.body = body

class Block(AST):
    def __init__(self, statements):
        self.statements = statements

class ArrayAccess(AST):
    def __init__(self, array, index):
        self.array = array # AST node (Var or another ArrayAccess)
        self.index = index

class Import(AST):
    def __init__(self, filename):
        self.filename = filename

class PythonImport(AST):
    def __init__(self, module_name):
        self.module_name = module_name

class AttributeAccess(AST):
    def __init__(self, obj, attribute):
        self.obj = obj  # Can be Var or another AttributeAccess
        self.attribute = attribute  # String name of attribute

class Increment(AST):
    def __init__(self, var_name):
        self.var_name = var_name

class Decrement(AST):
    def __init__(self, var_name):
        self.var_name = var_name

class CompoundAssign(AST):
    def __init__(self, left, op, right):
        self.left = left   # Variable name (string)
        self.op = op       # Operator: '+=', '-=', '*=', '/='
        self.right = right # Expression

class Break(AST):
    pass

class Continue(AST):
    pass

class TryCatch(AST):
    def __init__(self, try_body, catch_body):
        self.try_body = try_body
        self.catch_body = catch_body

class Throw(AST):
    def __init__(self, expr):
        self.expr = expr

class DictLiteral(AST):
    def __init__(self, pairs):
        self.pairs = pairs # list of (key, value) tuples

class ArrayLiteral(AST):
    def __init__(self, elements):
        self.elements = elements

class StringLiteral(AST):
    def __init__(self, value):
        self.value = value


class ClassDef(AST):
    def __init__(self, name, methods):
        self.name = name
        self.methods = methods

class ThisAccess(AST):
    def __init__(self, attribute):
        self.attribute = attribute

class Parser:
    def __init__(self, lexer):
        self.lexer = lexer
        self.current_token = self.lexer.get_next_token()

    def error(self, msg='Invalid syntax'):
        raise Exception(f'{msg} at {self.current_token}')

    def eat(self, token_type):
        if self.current_token.type == token_type:
            self.current_token = self.lexer.get_next_token()
        else:
            self.error(f'Expected {token_type}, got {self.current_token.type}')

    def factor(self):
        token = self.current_token
        if token.type == TokenType.INTEGER:
            self.eat(TokenType.INTEGER)
            return Num(token)
        elif token.type == TokenType.STRING:
            self.eat(TokenType.STRING)
            return String(token)
        elif token.type == TokenType.TRUE or token.type == TokenType.FALSE:
            self.eat(token.type)
            return BoolLiteral(token)
        elif token.type == TokenType.NONE:
            self.eat(TokenType.NONE)
            return NoneLiteral()
        elif token.type == TokenType.NOT:
            self.eat(TokenType.NOT)
            return UnaryOp(token, self.factor())
        elif token.type == TokenType.LPAREN:
            self.eat(TokenType.LPAREN)
            node = self.expr()
            self.eat(TokenType.RPAREN)
            return node
        elif token.type == TokenType.LBRACE:
            self.eat(TokenType.LBRACE)
            pairs = []
            if self.current_token.type != TokenType.RBRACE:
                key = self.expr()
                self.eat(TokenType.COLON)
                value = self.expr()
                pairs.append((key, value))
                while self.current_token.type == TokenType.COMMA:
                    self.eat(TokenType.COMMA)
                    key = self.expr()
                    self.eat(TokenType.COLON)
                    value = self.expr()
                    pairs.append((key, value))
            self.eat(TokenType.RBRACE)
            return DictLiteral(pairs)
        elif token.type == TokenType.LBRACKET:
            self.eat(TokenType.LBRACKET)
            elements = []
            if self.current_token.type != TokenType.RBRACKET:
                elements.append(self.expr())
                while self.current_token.type == TokenType.COMMA:
                    self.eat(TokenType.COMMA)
                    elements.append(self.expr())
            self.eat(TokenType.RBRACKET)
            return ArrayLiteral(elements)
        elif token.type == TokenType.KEYWORD and token.value == 'this':
            self.eat(TokenType.KEYWORD)  # this
            self.eat(TokenType.DOT)
            attr = self.current_token.value
            self.eat(TokenType.ID)
            return ThisAccess(attr)
        elif token.type == TokenType.ID:
            return self.variable_or_call()
        elif token.type == TokenType.MINUS:
            self.eat(TokenType.MINUS)
            return BinOp(Num(token), token, self.factor()) # Unary minus hack
        else:
            self.error()

    def variable_or_call(self):
        token = self.current_token
        self.eat(TokenType.ID)
        
        result = Var(token)
        
        while self.current_token.type in (TokenType.LPAREN, TokenType.LBRACKET, TokenType.DOT):
            if self.current_token.type == TokenType.LPAREN:
                self.eat(TokenType.LPAREN)
                args = []
                kwargs = []
                if self.current_token.type != TokenType.RPAREN:
                    # Check for named argument
                    if self.current_token.type == TokenType.ID and self.lexer.peek_token().type == TokenType.ASSIGN:
                        name = self.current_token.value
                        self.eat(TokenType.ID)
                        self.eat(TokenType.ASSIGN)
                        val = self.expr()
                        kwargs.append((name, val))
                    else:
                        args.append(self.expr())

                    while self.current_token.type == TokenType.COMMA:
                        self.eat(TokenType.COMMA)
                        if self.current_token.type == TokenType.ID and self.lexer.peek_token().type == TokenType.ASSIGN:
                            name = self.current_token.value
                            self.eat(TokenType.ID)
                            self.eat(TokenType.ASSIGN)
                            val = self.expr()
                            kwargs.append((name, val))
                        else:
                            if kwargs:
                                self.error("Positional argument cannot follow keyword argument")
                            args.append(self.expr())

                self.eat(TokenType.RPAREN)
                # Function call on the result so far
                
                if isinstance(result, Var):
                    result = FunctionCall(result.token.value, args, kwargs)
                elif isinstance(result, AttributeAccess):
                     # Convert AttributeAccess to FunctionCall with obj
                     result = FunctionCall(result.attribute, args, kwargs, obj=result.obj)
                else:
                    # Call on expression? e.g. arr[0]()
                    # We don't have AST for generic call on expression yet.
                    # FunctionCall expects name.
                    # Let's assume for now we only call named functions or methods.
                    self.error("Function call on expression not supported yet")

            elif self.current_token.type == TokenType.LBRACKET:
                self.eat(TokenType.LBRACKET)
                index = self.expr()
                self.eat(TokenType.RBRACKET)
                result = ArrayAccess(result, index)
            
            elif self.current_token.type == TokenType.DOT:
                self.eat(TokenType.DOT)
                attr_name = self.current_token.value
                self.eat(TokenType.ID)
                result = AttributeAccess(result, attr_name)
        
        return result

    def term(self):
        node = self.factor()
        while self.current_token.type in (TokenType.MUL, TokenType.DIV):
            token = self.current_token
            if token.type == TokenType.MUL:
                self.eat(TokenType.MUL)
            elif token.type == TokenType.DIV:
                self.eat(TokenType.DIV)
            node = BinOp(left=node, op=token, right=self.factor())
        return node

    def comparison(self):
        node = self.term()
        while self.current_token.type in (TokenType.PLUS, TokenType.MINUS):
            token = self.current_token
            if token.type == TokenType.PLUS:
                self.eat(TokenType.PLUS)
            elif token.type == TokenType.MINUS:
                self.eat(TokenType.MINUS)
            node = BinOp(left=node, op=token, right=self.term())
        
        # Handle comparisons
        if self.current_token.type in (TokenType.EQ, TokenType.NEQ, TokenType.LT, TokenType.GT, TokenType.LE, TokenType.GE):
            token = self.current_token
            self.eat(token.type)
            node = BinOp(left=node, op=token, right=self.comparison())
            
        return node

    def logical_and(self):
        node = self.comparison()
        while self.current_token.type == TokenType.AND:
            token = self.current_token
            self.eat(TokenType.AND)
            node = BinOp(left=node, op=token, right=self.comparison())
        return node

    def expr(self):
        node = self.logical_and()
        while self.current_token.type == TokenType.OR:
            token = self.current_token
            self.eat(TokenType.OR)
            node = BinOp(left=node, op=token, right=self.logical_and())
        return node

    def statement(self):
        token = self.current_token
        
        if token.type == TokenType.KEYWORD:
            if token.value == 'if':
                return self.if_stmt()
            elif token.value == 'while':
                return self.while_stmt()
            elif token.value == 'for':
                return self.for_stmt()
            elif token.value == 'return':
                return self.return_stmt()
            elif token.value == 'var':
                return self.var_decl()
            elif token.value == 'import':
                return self.import_stmt()
            elif token.value == 'break':
                self.eat(TokenType.KEYWORD)
                self.eat(TokenType.SEMICOLON)
                return Break()
            elif token.value == 'continue':
                self.eat(TokenType.KEYWORD)
                self.eat(TokenType.SEMICOLON)
                return Continue()
            elif token.value == 'try':
                return self.try_catch_stmt()
            elif token.value == 'throw':
                return self.throw_stmt()
            elif token.value == 'this':
                self.eat(TokenType.KEYWORD)  # this
                self.eat(TokenType.DOT)
                attr = self.current_token.value
                self.eat(TokenType.ID)
                if self.current_token.type == TokenType.ASSIGN:
                    self.eat(TokenType.ASSIGN)
                    right = self.expr()
                    self.eat(TokenType.SEMICOLON)
                    return Assign(ThisAccess(attr), right)
                else:
                    self.error('Expected assignment after this.attribute')
        elif token.type == TokenType.ID:
            # Parse the left-hand side (variable, array access, attribute access, or function call)
            expr = self.variable_or_call()
            
            if self.current_token.type == TokenType.SEMICOLON:
                # Expression statement (e.g. func(), obj.method())
                self.eat(TokenType.SEMICOLON)
                if isinstance(expr, FunctionCall):
                    return expr
                else:
                    # Allow other expressions as statements (e.g. x.y;)
                    return expr
            
            elif self.current_token.type == TokenType.ASSIGN:
                self.eat(TokenType.ASSIGN)
                right = self.expr()
                self.eat(TokenType.SEMICOLON)
                return Assign(expr, right)
                
            elif self.current_token.type == TokenType.PLUSPLUS:
                # x++;
                self.eat(TokenType.PLUSPLUS)
                self.eat(TokenType.SEMICOLON)
                if isinstance(expr, Var):
                    return Increment(expr.token.value)
                else:
                    self.error("Increment only supported for variables")
            
            elif self.current_token.type == TokenType.MINUSMINUS:
                # x--;
                self.eat(TokenType.MINUSMINUS)
                self.eat(TokenType.SEMICOLON)
                if isinstance(expr, Var):
                    return Decrement(expr.token.value)
                else:
                    self.error("Decrement only supported for variables")
            
            elif self.current_token.type in (TokenType.PLUSEQ, TokenType.MINUSEQ, TokenType.MULEQ, TokenType.DIVEQ):
                op_token = self.current_token
                self.eat(op_token.type)
                right = self.expr()
                self.eat(TokenType.SEMICOLON)
                
                op_str = ''
                if op_token.type == TokenType.PLUSEQ: op_str = '+='
                elif op_token.type == TokenType.MINUSEQ: op_str = '-='
                elif op_token.type == TokenType.MULEQ: op_str = '*='
                elif op_token.type == TokenType.DIVEQ: op_str = '/='
                
                if isinstance(expr, Var):
                    return CompoundAssign(expr.token.value, op_str, right)
                else:
                    self.error("Compound assignment only supported for variables")
            
            else:
                self.error('Expected assignment, function call, or increment/decrement')
        elif token.type == TokenType.LBRACE:
            return self.block()

        self.error()

    def var_decl(self):
        self.eat(TokenType.KEYWORD) # var
        name = self.current_token.value
        self.eat(TokenType.ID)
        
        size = None
        init_value = None
        
        if self.current_token.type == TokenType.LBRACKET:
            self.eat(TokenType.LBRACKET)
            size = self.expr() 
            self.eat(TokenType.RBRACKET)
        elif self.current_token.type == TokenType.ASSIGN:
            # var x = value;
            self.eat(TokenType.ASSIGN)
            init_value = self.expr()
        
        self.eat(TokenType.SEMICOLON)
        
        # If there's an initialization, return both VarDecl and Assign
        var_decl = VarDecl('var', name, size)
        if init_value:
            # Create a compound statement: declare then assign
            return Block([var_decl, Assign(Var(Token(TokenType.ID, name)), init_value)])
        return var_decl

    def return_stmt(self):
        self.eat(TokenType.KEYWORD)
        expr = self.expr()
        self.eat(TokenType.SEMICOLON)
        return Return(expr)

    def if_stmt(self):
        self.eat(TokenType.KEYWORD) # if
        self.eat(TokenType.LPAREN)
        condition = self.expr()
        self.eat(TokenType.RPAREN)
        true_body = self.statement()
        false_body = None
        if self.current_token.type == TokenType.KEYWORD and self.current_token.value == 'else':
            self.eat(TokenType.KEYWORD)
            false_body = self.statement()
        return If(condition, true_body, false_body)

    def while_stmt(self):
        self.eat(TokenType.KEYWORD) # while
        self.eat(TokenType.LPAREN)
        condition = self.expr()
        self.eat(TokenType.RPAREN)
        body = self.statement()
        return While(condition, body)

    def for_stmt(self):
        self.eat(TokenType.KEYWORD) # for
        self.eat(TokenType.LPAREN)
        
        # Init
        init = self.statement() # usually var decl or assign
        
        # Condition
        condition = self.expr()
        self.eat(TokenType.SEMICOLON)
        
        # Update - handle i++, i--, or regular assignment
        if self.current_token.type == TokenType.ID:
            update_var = self.current_token.value
            self.eat(TokenType.ID)
            
            if self.current_token.type == TokenType.PLUSPLUS:
                self.eat(TokenType.PLUSPLUS)
                update = Increment(update_var)
            elif self.current_token.type == TokenType.MINUSMINUS:
                self.eat(TokenType.MINUSMINUS)
                update = Decrement(update_var)
            elif self.current_token.type == TokenType.ASSIGN:
                self.eat(TokenType.ASSIGN)
                update_right = self.expr()
                update = Assign(Var(Token(TokenType.ID, update_var)), update_right)
            elif self.current_token.type == TokenType.PLUSEQ:
                self.eat(TokenType.PLUSEQ)
                update_right = self.expr()
                update = CompoundAssign(update_var, '+=', update_right)
            elif self.current_token.type == TokenType.MINUSEQ:
                self.eat(TokenType.MINUSEQ)
                update_right = self.expr()
                update = CompoundAssign(update_var, '-=', update_right)
            else:
                self.error('Expected assignment or increment/decrement in for loop update')
        else:
            self.error('Expected variable in for loop update')
        
        self.eat(TokenType.RPAREN)
        body = self.statement()
        
        return For(init, condition, update, body)

    def import_stmt(self):
        self.eat(TokenType.KEYWORD) # import
        
        # Check if it's a string (file import) or identifier (Python module)
        if self.current_token.type == TokenType.STRING:
            filename = self.current_token.value
            self.eat(TokenType.STRING)
            self.eat(TokenType.SEMICOLON)
            return Import(filename)
        elif self.current_token.type == TokenType.ID:
            module_name = self.current_token.value
            self.eat(TokenType.ID)
            self.eat(TokenType.SEMICOLON)
            return PythonImport(module_name)
        else:
            self.error("Expected module name or filename after import")

    def try_catch_stmt(self):
        self.eat(TokenType.KEYWORD) # try
        try_body = self.block()
        self.eat(TokenType.KEYWORD) # catch
        catch_body = self.block()
        return TryCatch(try_body, catch_body)

    def throw_stmt(self):
        self.eat(TokenType.KEYWORD) # throw
        expr = self.expr()
        self.eat(TokenType.SEMICOLON)
        return Throw(expr)

    def block(self):
        self.eat(TokenType.LBRACE)
        statements = []
        while self.current_token.type != TokenType.RBRACE and self.current_token.type != TokenType.EOF:
            statements.append(self.statement())
        self.eat(TokenType.RBRACE)
        return Block(statements)

    def class_def(self):
        self.eat(TokenType.KEYWORD)  # class
        class_name = self.current_token.value
        self.eat(TokenType.ID)
        self.eat(TokenType.LBRACE)
        
        methods = []
        while self.current_token.type == TokenType.KEYWORD and self.current_token.value == 'function':
            methods.append(self.function_def())
        
        self.eat(TokenType.RBRACE)
        return ClassDef(class_name, methods)

    def function_def(self):
        self.eat(TokenType.KEYWORD) # function
        name = self.current_token.value
        self.eat(TokenType.ID)
        self.eat(TokenType.LPAREN)
        params = []
        if self.current_token.type != TokenType.RPAREN:
            # int x or var x
            if self.current_token.type == TokenType.KEYWORD:
                self.eat(TokenType.KEYWORD) # int or var
            param_name = self.current_token.value
            self.eat(TokenType.ID)
            params.append(('var', param_name))
            
            while self.current_token.type == TokenType.COMMA:
                self.eat(TokenType.COMMA)
                if self.current_token.type == TokenType.KEYWORD:
                    self.eat(TokenType.KEYWORD) # int or var
                param_name = self.current_token.value
                self.eat(TokenType.ID)
                params.append(('var', param_name))
        
        self.eat(TokenType.RPAREN)
        body = self.block()
        return FunctionDef(name, params, body)

    def parse(self):
        statements = []
        while self.current_token.type != TokenType.EOF:
            if self.current_token.type == TokenType.KEYWORD and self.current_token.value == 'function':
                statements.append(self.function_def())
            elif self.current_token.type == TokenType.KEYWORD and self.current_token.value == 'class':
                statements.append(self.class_def())
            elif self.current_token.type == TokenType.KEYWORD and self.current_token.value == 'import':
                statements.append(self.import_stmt())
            else:
                # Top level statements (like print(fib(10));)
                statements.append(self.statement())
        return Program(statements)
