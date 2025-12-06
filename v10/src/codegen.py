import parser

class CodeGen:
    def __init__(self):
        self.code = []
        self.label_counter = 0
        self.scopes = [] # List of dicts {var_name: offset}
        self.current_offset = 0
        self.current_function_params = 0  # Track params for current function
        self.loop_stack = []  # Stack of (continue_label, break_label) for nested loops
        self.try_stack = []  # Stack of catch labels for nested try blocks
        self.python_modules = set()  # Track imported Python modules
        self.var_map = {}  # Simple variable map for now
        self.var_map = {}  # Simple variable map for now
        self.globals = {}  # Map global variable names to absolute stack offsets
        self.function_signatures = {} # Map function name to list of parameter names

    def new_label(self):
        self.label_counter += 1
        return f'L{self.label_counter}'

    def emit(self, instr):
        self.code.append(instr)

    def enter_scope(self):
        self.scopes.append({})
        self.current_offset = 0

    def exit_scope(self):
        self.scopes.pop()

    def define_var(self, name, size=1):
        # Stack grows upwards. 
        # Local variables are at positive offsets from FP (Frame Pointer) in our simplified model?
        # Or let's assume a simple stack machine where locals are just indexed.
        # Let's say locals are 0, 1, 2... relative to the start of the function's stack frame.
        
        # In this simple VM, let's assume:
        # FP points to the start of locals.
        # LOAD 0 -> loads first local.
        
        scope = self.scopes[-1]
        scope[name] = self.current_offset
        self.current_offset += size

    def get_var_offset(self, name):
        # Check local scopes first (reverse order)
        for scope in reversed(self.scopes):
            if name in scope:
                return (False, scope[name])
        
        # Check globals
        if name in self.globals:
            return (True, self.globals[name])
            
        raise Exception(f'Undefined variable: {name}')

    def generate(self, node):
        method_name = f'visit_{type(node).__name__}'
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        raise Exception(f'No visit_{type(node).__name__} method')

    def visit_Program(self, node):
        # Pre-scan for global variables to assign them offsets
        global_offset = 0
        
        def scan_globals(stmt):
            nonlocal global_offset
            if isinstance(stmt, parser.VarDecl):
                if stmt.name not in self.globals:
                    self.globals[stmt.name] = global_offset
                    # print(f"DEBUG: Found Global: {stmt.name} at {global_offset}")
                    global_offset += 1
            elif isinstance(stmt, parser.Block):
                for s in stmt.statements:
                    scan_globals(s)
            elif isinstance(stmt, parser.If):
                scan_globals(stmt.true_body)
                if stmt.false_body:
                    scan_globals(stmt.false_body)
            elif isinstance(stmt, parser.While):
                scan_globals(stmt.body)
            elif isinstance(stmt, parser.For):
                if stmt.init:
                    scan_globals(stmt.init)
                scan_globals(stmt.body)
            elif isinstance(stmt, parser.TryCatch):
                scan_globals(stmt.try_body)
                scan_globals(stmt.catch_body)

        for stmt in node.statements:
            if not isinstance(stmt, parser.FunctionDef) and not isinstance(stmt, parser.ClassDef):
                scan_globals(stmt)
            elif isinstance(stmt, parser.FunctionDef):
                # Register function signature
                param_names = [p[1] for p in stmt.params]
                self.function_signatures[stmt.name] = param_names

        main_label = self.new_label()
        
        # Emit symbol table for runtime variable sharing
        import json
        self.emit(f"SYMBOL_TABLE {json.dumps(self.globals)}")
        
        self.emit(f'JMP {main_label}')
        
        # Emit functions and classes before main code
        for stmt in node.statements:
            if isinstance(stmt, parser.FunctionDef) or isinstance(stmt, parser.ClassDef):
                self.generate(stmt)
        
        self.emit(f'{main_label}:')
        self.enter_scope() # Global scope (or main scope)
        
        # Populate global scope with pre-calculated offsets
        # But wait, define_var uses current_offset.
        # We need to make sure current_offset matches global_offset logic.
        # Actually, we can just let visit_VarDecl handle it, but we need to ensure
        # it uses the SAME offsets we calculated.
        # Or better: just let visit_VarDecl do its job, but we need to know WHICH vars are globals.
        # The self.globals map tells us which names are globals.
        
        for stmt in node.statements:
            if not isinstance(stmt, parser.FunctionDef) and not isinstance(stmt, parser.ClassDef):
                self.generate(stmt)
        self.exit_scope()
        self.emit('HALT')
        return self.code

    def visit_FunctionDef(self, node):
        self.emit(f'{node.name}:')
        self.enter_scope()
        
        # Parameters are pushed before call, so they are effectively local variables
        # But in a real stack frame, they are at negative offsets or we pop them into locals.
        # Simplest approach: Caller pushes args. Callee pops them into locals?
        # Or Caller pushes args. Callee treats them as locals 0, 1, 2...
        # Let's assume Caller pushes args.
        # And we map params to offsets 0, 1, ...
        
        # BUT, if we use LOAD <offset>, and we want to support recursion, we need a Frame Pointer.
        # Let's assume the VM handles FP.
        # LOAD 0 is the first local/param.
        
        # Parameters are pushed before call
        # Stack: ... arg1, arg2, IP, FP
        # FP points to slot above saved FP.
        # Saved FP is at FP-1.
        # IP is at FP-2.
        # Last arg is at FP-3.
        
        num_params = len(node.params)
        self.current_function_params = num_params
        for i, (type_name, param_name) in enumerate(node.params):
            # Param i (0-indexed) is at FP - 2 - (num_params - i)
            offset = -2 - (num_params - i)
            self.scopes[-1][param_name] = offset
            
        self.generate(node.body)
        
        # Implicit return if not present
        self.emit('PUSH 0')
        self.emit(f'RET {num_params}')
        
        self.current_function_params = 0
        self.exit_scope()

    def visit_Block(self, node):
        for stmt in node.statements:
            self.generate(stmt)

    def visit_DictLiteral(self, node):
        # Create new dict
        self.emit('DICT_NEW') # Pushes ptr
        
        for key, value in node.pairs:
            self.emit('DUP') # Duplicate ptr
            self.generate(key)
            self.generate(value)
            self.emit('SET') # Pops val, key, ptr. Original ptr remains.

    def visit_ArrayLiteral(self, node):
        # Push all elements
        for element in node.elements:
            self.generate(element)
        # Create array from top N elements
        self.emit(f'ARRAY_LITERAL {len(node.elements)}')

    def visit_ArrayAccess(self, node):
        # Generate code for the array expression (could be a variable or another array access)
        self.generate(node.array)
        self.generate(node.index)
        self.emit('GET')

    def visit_Assign(self, node):
        if isinstance(node.left, parser.Var):
            self.generate(node.right)
            is_global, offset = self.get_var_offset(node.left.value)
            if is_global:
                self.emit(f'STORE_GLOBAL {offset}')
            else:
                self.emit(f'STORE {offset}')
        elif isinstance(node.left, parser.ThisAccess):
            # this.property = value
            # LOAD_THIS, PUSH property_name, PUSH value, SET
            self.emit('LOAD_THIS')
            self.emit(f'STRING_NEW "{node.left.attribute}"')
            self.generate(node.right)
            self.emit('SET')
        elif isinstance(node.left, parser.ArrayAccess):
            # arr[i] = val
            # PUSH arr
            # PUSH index
            # PUSH val
            # SET
            
            self.generate(node.left.array) # Push array/dict ref
            self.generate(node.left.index) # Push index/key
            self.generate(node.right) # Push value
            self.emit('SET')

    def visit_VarDecl(self, node):
        if node.size: # Array
            if isinstance(node.size, parser.Num):
                count = node.size.value
                self.emit(f'PUSH {count}')
            else:
                self.generate(node.size)
            
            self.emit('ARRAY_NEW')
            offset = self.current_offset
            self.define_var(node.name)
            self.emit(f'STORE {offset}')  # Store the array pointer
            
        else:
            # var a;
            self.emit('PUSH 0') # Init to 0 or none
            # Check if it's a global variable
            if node.name in self.globals:
                self.emit(f'STORE_GLOBAL {self.globals[node.name]}')
            else:
                offset = self.current_offset
                self.define_var(node.name)
                self.emit(f'STORE {offset}')  # Store the initial value

    def visit_Return(self, node):
        self.generate(node.expr)
        self.emit(f'RET {self.current_function_params}')

    def visit_If(self, node):
        false_label = self.new_label()
        end_label = self.new_label()
        
        self.generate(node.condition)
        self.emit(f'JIF {false_label}')
        
        self.generate(node.true_body)
        self.emit(f'JMP {end_label}')
        
        self.emit(f'{false_label}:')
        if node.false_body:
            self.generate(node.false_body)
            
        self.emit(f'{end_label}:')

    def visit_While(self, node):
        start_label = self.new_label()
        end_label = self.new_label()
        
        self.loop_stack.append((start_label, end_label))
        
        self.emit(f'{start_label}:')
        self.generate(node.condition)
        self.emit(f'JIF {end_label}')
        
        self.generate(node.body)
        self.emit(f'JMP {start_label}')
        
        self.emit(f'{end_label}:')
        
        self.loop_stack.pop()

    def visit_For(self, node):
        # for(init; cond; update) body
        # ->
        # init
        # start:
        # cond
        # JIF end
        # body
        # update
        # JMP start
        # end:
        
        start_label = self.new_label()
        update_label = self.new_label()
        end_label = self.new_label()
        
        self.generate(node.init)
        
        self.loop_stack.append((update_label, end_label))
        
        self.emit(f'{start_label}:')
        self.generate(node.condition)
        self.emit(f'JIF {end_label}')
        
        self.generate(node.body)
        
        self.emit(f'{update_label}:')
        self.generate(node.update)
        self.emit(f'JMP {start_label}')
        
        self.emit(f'{end_label}:')
        
        self.loop_stack.pop()

    def visit_BinOp(self, node):
        self.generate(node.left)
        self.generate(node.right)
        
        if node.op.type == parser.TokenType.PLUS:
            self.emit('ADD')
        elif node.op.type == parser.TokenType.MINUS:
            self.emit('SUB')
        elif node.op.type == parser.TokenType.MUL:
            self.emit('MUL')
        elif node.op.type == parser.TokenType.DIV:
            self.emit('DIV')
        elif node.op.type == parser.TokenType.EQ:
            self.emit('EQ')
        elif node.op.type == parser.TokenType.NEQ:
            self.emit('NEQ')
        elif node.op.type == parser.TokenType.LT:
            self.emit('LT')
        elif node.op.type == parser.TokenType.GT:
            self.emit('GT')
        elif node.op.type == parser.TokenType.LE:
            self.emit('LE')
        elif node.op.type == parser.TokenType.GE:
            self.emit('GE')
        elif node.op.type == parser.TokenType.AND:
            # Short-circuit evaluation: if left is false, skip right
            end_label = self.new_label()
            self.emit('DUP')  # Duplicate left value
            self.emit(f'JIF {end_label}')  # If false, skip right evaluation
            self.emit('POP')  # Pop the duplicated false value
            # Right side is already on stack from generate(node.right)
            self.emit(f'{end_label}:')
        elif node.op.type == parser.TokenType.OR:
            # Short-circuit evaluation: if left is true, skip right
            end_label = self.new_label()
            self.emit('DUP')  # Duplicate left value
            self.emit(f'JIF {end_label}')  # If false, continue to right
            self.emit('POP')  # Pop the duplicated value
            self.emit('POP')  # Pop the right value
            self.emit('PUSH 1')  # Push true
            self.emit(f'{end_label}:')
        # Add others...

    def visit_Num(self, node):
        self.emit(f'PUSH {node.value}')
    
    def visit_String(self, node):
        # Emit STRING_NEW with the string value
        escaped = node.value.replace('\\', '\\\\').replace('\n', '\\n').replace('\t', '\\t')
        self.emit(f'STRING_NEW "{escaped}"')

    def visit_BoolLiteral(self, node):
        # Push Python's True/False so typeof can detect them
        value = 'True' if node.value else 'False'
        self.emit(f'PUSH_{value.upper()}')

    def visit_NoneLiteral(self, node):
        self.emit('PUSH_NONE')

    def visit_UnaryOp(self, node):
        self.generate(node.expr)
        if node.op.type == parser.TokenType.NOT:
            self.emit('NOT')

    def visit_Var(self, node):
        # Check if this is a Python module reference
        if node.token.value in self.python_modules:
            # Push module name as string so VM can look it up
            self.emit(f'PUSH_MODULE {node.token.value}')
        else:
            # Regular variable
            try:
                is_global, offset = self.get_var_offset(node.token.value)
                if is_global:
                    self.emit(f'LOAD_GLOBAL {offset}')
                else:
                    self.emit(f'LOAD {offset}')
            except:
                # If not found in scopes, assume it's a dynamic variable (e.g. from Python)
                self.emit(f'LOAD_PYTHON_GLOBAL "{node.token.value}"')

    def visit_FunctionCall(self, node):
        builtins = ['print', 'len', 'abs', 'push', 'pop', 'input', 'readfile', 'writefile', 'int', 'str', 'typeof', '_python_', '_javascript_']
        void_builtins = ['print', 'push', '_python_', '_javascript_']  # Functions that don't return values
        
        # Check if this is a class instantiation
        if hasattr(self, 'classes') and node.name in self.classes:
            # Create new instance (dict)
            self.emit('DICT_NEW')
            self.emit('DUP')  # Keep instance on stack
            
            # Call constructor if it exists
            class_info = self.classes[node.name]
            if 'constructor' in class_info['methods']:
                # Push instance as 'this'
                self.emit('DUP')
                # Generate constructor arguments
                for arg in node.args:
                    self.generate(arg)
                # Call constructor
                self.emit(f"CALL_CONSTRUCTOR {class_info['methods']['constructor']} {len(node.args)}")
                self.emit('POP')  # Discard constructor return value
            # Instance is left on stack
            return
        
        # Check if this is a method call (has obj attribute)
        if node.obj is not None:
            # Method call: obj.method(args)
            # Generate code for object
            self.generate(node.obj)
            # Generate code for arguments
            for arg in node.args:
                self.generate(arg)
            # Call the method
            self.emit(f'CALL_METHOD {node.name} {len(node.args)}')
        elif node.name == 'print':
            # Built-in print
            for arg in node.args:
                self.generate(arg)
                self.emit('PRINT')
            # Print returns nothing
        elif node.name == '_python_':
            # Execute inline Python code
            self.generate(node.args[0])
            self.emit('EXEC_PYTHON')
        elif node.name == '_javascript_':
            # Execute inline JavaScript code (Node.js)
            self.generate(node.args[0])
            self.emit('EXEC_JAVASCRIPT')
        elif node.name in builtins:
            # Other built-in functions
            for arg in node.args:
                self.generate(arg)
            # Special cases to avoid instruction name conflicts
            if node.name == 'push':
                self.emit('ARRAY_PUSH')
            elif node.name == 'pop':
                self.emit('ARRAY_POP')
            else:
                self.emit(node.name.upper())
            # If it's a void function being used as expression, we don't push anything
        else:

            # User function or variable call
            
            # Check if it's a known HIC function
            if node.name in self.function_signatures:
                sig = self.function_signatures[node.name]
                
                # Prepare arguments
                final_args = [None] * len(sig)
                
                # 1. Fill positional args
                if len(node.args) > len(sig):
                    raise Exception(f"Too many arguments for function '{node.name}'")
                
                for i, arg in enumerate(node.args):
                    final_args[i] = arg
                
                # 2. Fill named args
                for name, val in node.kwargs:
                    if name not in sig:
                        raise Exception(f"Unknown argument '{name}' for function '{node.name}'")
                    idx = sig.index(name)
                    if final_args[idx] is not None:
                        raise Exception(f"Duplicate argument '{name}' for function '{node.name}'")
                    final_args[idx] = val
                
                # 3. Check for missing args
                for i, arg in enumerate(final_args):
                    if arg is None:
                        raise Exception(f"Missing argument '{sig[i]}' for function '{node.name}'")
                
                # Generate code for reordered args
                for arg in final_args:
                    self.generate(arg)
                
                self.emit(f'CALL {node.name}')
                
            else:
                # Dynamic call (variable or unknown function)
                # Generate positional args
                for arg in node.args:
                    self.generate(arg)
                
                if node.kwargs:
                    # Generate kwargs dict
                    self.emit('DICT_NEW')
                    for name, val in node.kwargs:
                        self.emit('DUP')
                        self.emit(f'PUSH "{name}"') # String key
                        self.generate(val)
                        self.emit('SET')
                    
                    # Load callable
                    try:
                        is_global, offset = self.get_var_offset(node.name)
                        if is_global:
                            self.emit(f'LOAD_GLOBAL {offset}')
                        else:
                            self.emit(f'LOAD {offset}')
                        self.emit(f'CALL_OBJECT_KW {len(node.args)}')
                    except Exception:
                         raise Exception(f"Unknown function '{node.name}' called with named arguments")
                else:
                    # No kwargs, existing logic
                    try:
                        is_global, offset = self.get_var_offset(node.name)
                        if is_global:
                            self.emit(f'LOAD_GLOBAL {offset}')
                        else:
                            self.emit(f'LOAD {offset}')
                        self.emit(f'CALL_OBJECT {len(node.args)}')
                    except Exception:
                        self.emit(f'CALL {node.name}')

    def visit_ArrayAccess(self, node):
        # Generate code for the array expression (could be a variable or another array access)
        self.generate(node.array)
        self.generate(node.index)
        self.emit('GET')

    def visit_Import(self, node):
        # Handle import?
        # Maybe just ignore for codegen if we assume it's already merged?
        # Or if we want to support it, we might need to compile that file too.
        # For this simple version, let's assume the compiler driver handles merging ASTs.
        pass

    def visit_PythonImport(self, node):
        # Track this as a Python module
        self.python_modules.add(node.module_name)
        # Emit instruction to import Python module
        self.emit(f'IMPORT_PYTHON {node.module_name}')

    def visit_AttributeAccess(self, node):
        # Generate code for object
        self.generate(node.obj)
        # Push attribute name and get it
        self.emit(f'GET_ATTR {node.attribute}')

    def visit_Break(self, node):
        if not self.loop_stack:
            raise Exception('break statement outside loop')
        _, break_label = self.loop_stack[-1]
        self.emit(f'JMP {break_label}')

    def visit_Continue(self, node):
        if not self.loop_stack:
            raise Exception('continue statement outside loop')
        continue_label, _ = self.loop_stack[-1]
        self.emit(f'JMP {continue_label}')

    def visit_TryCatch(self, node):
        catch_label = self.new_label()
        end_label = self.new_label()
        
        self.emit(f'TRY_BEGIN {catch_label}')
        self.try_stack.append(catch_label)
        self.generate(node.try_body)
        self.try_stack.pop()
        self.emit('TRY_END')
        self.emit(f'JMP {end_label}')
        
        self.emit(f'{catch_label}:')
        self.generate(node.catch_body)
        
        self.emit(f'{end_label}:')

    def visit_Throw(self, node):
        self.generate(node.expr)
        self.emit('THROW')

    def visit_Increment(self, node):
        # x++ → LOAD x, PUSH 1, ADD, STORE x
        is_global, offset = self.get_var_offset(node.var_name)
        if is_global:
            self.emit(f'LOAD_GLOBAL {offset}')
        else:
            self.emit(f'LOAD {offset}')
        self.emit('PUSH 1')
        self.emit('ADD')
        if is_global:
            self.emit(f'STORE_GLOBAL {offset}')
        else:
            self.emit(f'STORE {offset}')

    def visit_Decrement(self, node):
        # x-- → LOAD x, PUSH 1, SUB, STORE x
        is_global, offset = self.get_var_offset(node.var_name)
        if is_global:
            self.emit(f'LOAD_GLOBAL {offset}')
        else:
            self.emit(f'LOAD {offset}')
        self.emit('PUSH 1')
        self.emit('SUB')
        if is_global:
            self.emit(f'STORE_GLOBAL {offset}')
        else:
            self.emit(f'STORE {offset}')

    def visit_CompoundAssign(self, node):
        # x += expr → LOAD x, <expr>, ADD, STORE x
        is_global, offset = self.get_var_offset(node.left)
        if is_global:
            self.emit(f'LOAD_GLOBAL {offset}')
        else:
            self.emit(f'LOAD {offset}')
        self.generate(node.right)
        
        if node.op == '+=':
            self.emit('ADD')
        elif node.op == '-=':
            self.emit('SUB')
        elif node.op == '*=':
            self.emit('MUL')
        elif node.op == '/=':
            self.emit('DIV')
        
        if is_global:
            self.emit(f'STORE_GLOBAL {offset}')
        else:
            self.emit(f'STORE {offset}')

    def visit_ClassDef(self, node):
        # Store class metadata
        if not hasattr(self, 'classes'):
            self.classes = {}
        
        method_labels = {}
        for method in node.methods:
            method_label = f"CLASS_{node.name}_{method.name}"
            method_labels[method.name] = method_label
            
            self.emit(f'{method_label}:')
            self.enter_scope()
            
            for param_type, param_name in method.params:
                self.define_var(param_name)
            
            # method.body is a Block object, iterate over its statements
            for stmt in method.body.statements:
                self.generate(stmt)
            
            self.emit('PUSH 0')
            num_params = len(method.params)
            self.emit(f'RET {num_params}')
            self.exit_scope()
        
        self.classes[node.name] = {
            'methods': method_labels,
            'constructor': method_labels.get('constructor')
        }
    
    def visit_ThisAccess(self, node):
        self.emit('LOAD_THIS')
        self.emit(f'STRING_NEW "{node.attribute}"')
        self.emit('GET')
