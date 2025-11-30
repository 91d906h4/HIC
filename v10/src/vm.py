import sys
import re

class HeapPointer:
    def __init__(self, ptr):
        self.ptr = ptr
    def __repr__(self):
        return f"HeapPointer({self.ptr})"
    def __hash__(self):
        return hash(self.ptr)
    def __eq__(self, other):
        return isinstance(other, HeapPointer) and self.ptr == other.ptr

class VM:
    def __init__(self):
        self.stack = []
        self.fp = 0
        self.ip = 0
        self.code = []
        self.labels = {}
        self.heap = {}
        self.heap_ptr = 0
        self.exception_handlers = []  # Stack of (catch_label, stack_size) for try blocks
        self.current_exception = None
        self.modules = {}  # Registry for imported Python modules
        self.global_count = 0  # Number of global variables (to protect during stack unwinding)
        self.this_stack = []  # Stack of current instances for methods

    def to_string(self, val):
        if isinstance(val, HeapPointer):
            if val.ptr not in self.heap:
                return "<dangling pointer>"
            obj = self.heap[val.ptr]
            if isinstance(obj, list):
                # Array
                elements = [self.to_string(e) for e in obj]
                return "[" + ", ".join(elements) + "]"
            elif isinstance(obj, dict):
                # Dict
                pairs = []
                for k, v in obj.items():
                    pairs.append(f"{k}: {self.to_string(v)}")
                return "{" + ", ".join(pairs) + "}"
        if val is True: return "true"
        if val is False: return "false"
        if val is None: return "none"
        return str(val)
        
    def load_program(self, filename):
        with open(filename, 'r') as f:
            lines = f.readlines()
            
        # First pass: labels
        addr = 0
        cleaned_lines = []
        for line in lines:
            line = line.strip()
            if not line: continue
            
            if line.endswith(':'):
                label_name = line[:-1]
                self.labels[label_name] = addr
            else:
                cleaned_lines.append(line)
                addr += 1
                
        # Second pass: instructions
        for line in cleaned_lines:
            parts = line.split(None, 1)
            op = parts[0]
            arg = None
            if len(parts) > 1:
                arg_str = parts[1]
                if op == 'STRING_NEW':
                    if arg_str.startswith('"') and arg_str.endswith('"'):
                        arg = arg_str[1:-1]
                        arg = arg.replace('\\n', '\n').replace('\\t', '\t').replace('\\\\', '\\')
                else:
                    try:
                        # Try to parse as float if it contains a decimal point
                        if '.' in arg_str:
                            arg = float(arg_str)
                        else:
                            arg = int(arg_str)
                    except ValueError:
                        arg = arg_str
            
            self.code.append((op, arg))
    
    def to_python(self, val):
        """Convert HIC types (HeapPointer) to Python types (list/dict) for interop."""
        if isinstance(val, HeapPointer):
            if val.ptr in self.heap:
                obj = self.heap[val.ptr]
                if isinstance(obj, list):
                    return [self.to_python(x) for x in obj]
                elif isinstance(obj, dict):
                    return {k: self.to_python(v) for k, v in obj.items()}
        return val
            
    def run(self):
        # sys.stdout = open('vm.log', 'w')
        # print(f"DEBUG: Labels: {self.labels}", flush=True)
        while self.ip < len(self.code):
            op, arg = self.code[self.ip]
            # if self.ip > -1:
            #     print(f"DEBUG: {self.ip}: {op} {arg}", flush=True)
            self.ip += 1
            
            if op == 'PUSH':
                self.stack.append(arg)
            elif op == 'PUSH_TRUE':
                self.stack.append(True)
            elif op == 'PUSH_FALSE':
                self.stack.append(False)
            elif op == 'PUSH_MODULE':
                # Push module name as string for module reference
                self.stack.append(arg)
            elif op == 'POP':
                self.stack.pop()
            elif op == 'DUP':
                self.stack.append(self.stack[-1])
            elif op == 'LOAD':
                val = self.stack[self.fp + arg]
                self.stack.append(val)
            elif op == 'STORE':
                val = self.stack.pop()
                idx = self.fp + arg
                # Extend stack if necessary
                while len(self.stack) <= idx:
                    self.stack.append(0)
                self.stack[idx] = val
                # print(f"DEBUG STORE: fp={self.fp}, arg={arg}, idx={idx}, val={val}, stack_len={len(self.stack)}", flush=True)
            elif op == 'LOAD_GLOBAL':
                val = self.stack[arg]
                self.stack.append(val)
            elif op == 'STORE_GLOBAL':
                val = self.stack.pop()
                idx = arg
                # Extend stack if necessary (shouldn't happen for globals usually, but for safety)
                while len(self.stack) <= idx:
                    self.stack.append(0)
                self.stack[idx] = val
                # Track the highest global index to protect globals during exception unwinding
                if idx + 1 > self.global_count:
                    self.global_count = idx + 1
                    # print(f"DEBUG STORE_GLOBAL: idx={idx}, new global_count={self.global_count}", flush=True)
            elif op == 'ADD':
                b = self.stack.pop()
                a = self.stack.pop()
                # Check if either operand is a string
                if isinstance(a, str) or isinstance(b, str):
                    # String concatenation
                    a_str = a if isinstance(a, str) else str(a)
                    b_str = b if isinstance(b, str) else str(b)
                    result = a_str + b_str
                    self.stack.append(result)
                else:
                    # Numeric addition
                    self.stack.append(a + b)
            elif op == 'SUB':
                b = self.stack.pop()
                a = self.stack.pop()
                self.stack.append(a - b)
            elif op == 'MUL':
                b = self.stack.pop()
                a = self.stack.pop()
                self.stack.append(a * b)
            elif op == 'DIV':
                b = self.stack.pop()
                a = self.stack.pop()
                self.stack.append(int(a / b))
            elif op == 'STRING_NEW':
                # Create a string and push it directly on stack
                try:
                    self.stack.append(arg)
                except Exception as e:
                    print(f"CRITICAL ERROR in STRING_NEW: {e}")
                    sys.exit(1)
            elif op == 'PUSH_NONE':
                self.stack.append(None)
            elif op == 'NOT':
                a = self.stack.pop()
                # Truthiness: 0, None, empty string = false
                is_truthy = a not in (0, None, '', False)
                self.stack.append(0 if is_truthy else 1)
            elif op == 'AND':
                # Note: Short-circuit is handled in codegen, this is just for completeness
                b = self.stack.pop()
                a = self.stack.pop()
                a_truthy = a not in (0, None, '', False)
                b_truthy = b not in (0, None, '', False)
                self.stack.append(1 if (a_truthy and b_truthy) else 0)
            elif op == 'OR':
                # Note: Short-circuit is handled in codegen, this is just for completeness
                b = self.stack.pop()
                a = self.stack.pop()
                a_truthy = a not in (0, None, '', False)
                b_truthy = b not in (0, None, '', False)
                self.stack.append(1 if (a_truthy or b_truthy) else 0)
            elif op == 'EQ':
                b = self.stack.pop()
                a = self.stack.pop()
                self.stack.append(1 if a == b else 0)
            elif op == 'NEQ':
                b = self.stack.pop()
                a = self.stack.pop()
                self.stack.append(1 if a != b else 0)
            elif op == 'LT':
                b = self.stack.pop()
                a = self.stack.pop()
                self.stack.append(1 if a < b else 0)
            elif op == 'GT':
                b = self.stack.pop()
                a = self.stack.pop()
                self.stack.append(1 if a > b else 0)
            elif op == 'LE':
                b = self.stack.pop()
                a = self.stack.pop()
                self.stack.append(1 if a <= b else 0)
            elif op == 'GE':
                b = self.stack.pop()
                a = self.stack.pop()
                self.stack.append(1 if a >= b else 0)
            elif op == 'JMP':
                if isinstance(arg, str):
                    self.ip = self.labels[arg]
                else:
                    self.ip = arg
            elif op == 'JIF':
                cond = self.stack.pop()
                if not cond:
                    if isinstance(arg, str):
                        self.ip = self.labels[arg]
                    else:
                        self.ip = arg
            elif op == 'CALL':
                self.stack.append(self.ip)
                self.stack.append(self.fp)
                self.fp = len(self.stack)
                
                if isinstance(arg, str):
                    self.ip = self.labels[arg]
                else:
                    self.ip = arg
            elif op == 'RET':
                ret_val = self.stack.pop()
                # Discard locals
                while len(self.stack) > self.fp:
                    self.stack.pop()
                # Now stack: [args, IP, FP]
                old_fp = self.stack.pop()
                ret_addr = self.stack.pop()
                # Now stack: [args]
                # Clean up arguments if arg count is provided
                if arg is not None:
                    num_args = arg
                    for _ in range(num_args):
                        self.stack.pop()
                self.fp = old_fp
                self.ip = ret_addr
                self.stack.append(ret_val)
                if self.this_stack:
                    self.this_stack.pop()
            elif op == 'PRINT':
                val = self.stack.pop()
                print(self.to_string(val))
            elif op == 'ARRAY_NEW':
                size = self.stack.pop()
                arr = [0] * size
                ptr = self.heap_ptr
                self.heap[ptr] = arr
                self.heap_ptr += 1
                self.stack.append(HeapPointer(ptr))
            elif op == 'DICT_NEW':
                d = {}
                ptr = self.heap_ptr
                self.heap[ptr] = d
                self.heap_ptr += 1
                self.stack.append(HeapPointer(ptr))
            elif op == 'ARRAY_LITERAL':
                count = int(arg)
                elements = []
                for _ in range(count):
                    elements.insert(0, self.stack.pop())
                
                ptr = self.heap_ptr
                self.heap[ptr] = elements
                self.heap_ptr += 1
                self.stack.append(HeapPointer(ptr))
            elif op == 'GET':
                index_or_key = self.stack.pop()
                ptr = self.stack.pop()
                # Check if ptr is a string
                if isinstance(ptr, str):
                    # String indexing
                    self.stack.append(ptr[index_or_key])
                elif isinstance(ptr, HeapPointer):
                    # Array or dict
                    obj = self.heap[ptr.ptr]
                    if isinstance(obj, list):
                        self.stack.append(obj[index_or_key])
                    elif isinstance(obj, dict):
                        if index_or_key not in obj:
                            print(f"Runtime Error: Key not found {index_or_key}")
                            sys.exit(1)
                        self.stack.append(obj[index_or_key])
                else:
                    print(f"Runtime Error: GET requires string, array, or dict")
                    sys.exit(1)
            elif op == 'SET':
                val = self.stack.pop()
                index_or_key = self.stack.pop()
                ptr = self.stack.pop()
                if isinstance(ptr, HeapPointer):
                    obj = self.heap[ptr.ptr]
                    obj[index_or_key] = val
                else:
                    print(f"Runtime Error: SET requires array or dict")
                    sys.exit(1)
            elif op == 'HALT':
                break
            elif op == 'LEN':
                obj = self.stack.pop()
                if isinstance(obj, str):
                    self.stack.append(len(obj))
                elif isinstance(obj, HeapPointer) and obj.ptr in self.heap:
                    # Array or dict
                    self.stack.append(len(self.heap[obj.ptr]))
                else:
                    print(f"Runtime Error: len() requires string, array, or dict")
                    sys.exit(1)
            elif op == 'ABS':
                val = self.stack.pop()
                self.stack.append(abs(val))
            elif op == 'ARRAY_PUSH':
                # push(array, value)
                val = self.stack.pop()
                ptr = self.stack.pop()
                if isinstance(ptr, HeapPointer) and ptr.ptr in self.heap and isinstance(self.heap[ptr.ptr], list):
                    self.heap[ptr.ptr].append(val)
                else:
                    print(f"Runtime Error: push() requires array")
                    sys.exit(1)
            elif op == 'ARRAY_POP':
                # pop(array)
                ptr = self.stack.pop()
                if isinstance(ptr, HeapPointer) and ptr.ptr in self.heap and isinstance(self.heap[ptr.ptr], list):
                    if len(self.heap[ptr.ptr]) > 0:
                        self.stack.append(self.heap[ptr.ptr].pop())
                    else:
                        print(f"Runtime Error: pop() from empty array")
                        sys.exit(1)
                else:
                    print(f"Runtime Error: pop() requires array")
                    sys.exit(1)
            elif op == 'INPUT':
                # input(prompt)
                prompt = self.stack.pop()
                result = input(str(prompt))
                self.stack.append(result)
            elif op == 'READFILE':
                filename = self.stack.pop()
                try:
                    with open(filename, 'r') as f:
                        content = f.read()
                    self.stack.append(content)
                except Exception as e:
                    if self.exception_handlers:
                        self.current_exception = str(e)
                        catch_label, stack_size = self.exception_handlers[-1]
                        # Unwind stack to try block entry (same as THROW)
                        # print(f"DEBUG READFILE exception: Unwinding from {len(self.stack)} to {stack_size}", flush=True)
                        while len(self.stack) > stack_size:
                            self.stack.pop()
                        self.ip = self.labels[catch_label]
                    else:
                        print(f"Runtime Error: {e}")
                        sys.exit(1)
            elif op == 'WRITEFILE':
                content = self.stack.pop()
                filename = self.stack.pop()
                try:
                    with open(filename, 'w') as f:
                        f.write(str(content))
                    self.stack.append(None)
                except Exception as e:
                    if self.exception_handlers:
                        self.current_exception = str(e)
                        catch_label, stack_size = self.exception_handlers[-1]
                        # Unwind stack to try block entry
                        # print(f"DEBUG WRITEFILE exception: Unwinding from {len(self.stack)} to {stack_size}", flush=True)
                        while len(self.stack) > stack_size:
                            self.stack.pop()
                        self.ip = self.labels[catch_label]
                    else:
                        print(f"Runtime Error: {e}")
                        sys.exit(1)
            elif op == 'INT':
                val = self.stack.pop()
                try:
                    self.stack.append(int(val))
                except:
                    self.stack.append(0)
            elif op == 'STR':
                val = self.stack.pop()
                self.stack.append(self.to_string(val))
            elif op == 'TYPEOF':
                val = self.stack.pop()
                if val is None:
                    self.stack.append('none')
                elif isinstance(val, bool):  # Check bool before int since bool is subclass of int
                    self.stack.append('bool')
                elif isinstance(val, float):  # Check float before int
                    self.stack.append('float')
                elif isinstance(val, int):
                    self.stack.append('int')
                elif isinstance(val, str):
                    self.stack.append('string')
                elif isinstance(val, HeapPointer):
                    obj = self.heap[val.ptr]
                    if isinstance(obj, dict):
                        self.stack.append('dict')
                    elif isinstance(obj, list):
                        self.stack.append('array')
                    else:
                        self.stack.append('object')
                else:
                    self.stack.append('unknown')
            elif op == 'TRY_BEGIN':
                # arg is the catch label
                self.exception_handlers.append((arg, len(self.stack)))
                # print(f"DEBUG TRY_BEGIN: Saving stack_size={len(self.stack)}", flush=True)
            elif op == 'TRY_END':
                catch_label, stack_size = self.exception_handlers.pop()
                # Clean up any variables declared in the try block
                # print(f"DEBUG TRY_END: Restoring stack from {len(self.stack)} to {stack_size}", flush=True)
                while len(self.stack) > stack_size:
                    self.stack.pop()
            elif op == 'THROW':
                error_msg = self.stack.pop()
                if self.exception_handlers:
                    self.current_exception = error_msg
                    catch_label, stack_size = self.exception_handlers[-1]
                    # print(f"DEBUG THROW: Unwinding from {len(self.stack)} to {stack_size}", flush=True)
                    # print(f"DEBUG THROW: Stack before unwind: {self.stack[:min(20, len(self.stack))]}", flush=True)
                    # Unwind stack to try block entry
                    while len(self.stack) > stack_size:
                        self.stack.pop()
                    # print(f"DEBUG THROW: Stack after unwind: {self.stack[:min(20, len(self.stack))]}", flush=True)
                    self.ip = self.labels[catch_label]
                else:
                    print(f"Uncaught exception: {error_msg}")
                    sys.exit(1)
            elif op == 'LOAD_THIS':
                if not self.this_stack:
                    raise RuntimeError("LOAD_THIS called outside of method context")
                self.stack.append(self.this_stack[-1])
            elif op == 'CALL_CONSTRUCTOR':
                parts = arg.split()
                label = parts[0]
                num_args = int(parts[1])
                args = []
                for _ in range(num_args):
                    args.insert(0, self.stack.pop())
                instance = self.stack.pop()
                self.this_stack.append(instance)
                self.stack.append(self.ip)
                self.stack.append(self.fp)
                self.fp = len(self.stack)
                for a in args:
                    self.stack.append(a)
                if label not in self.labels:
                    raise RuntimeError(f"Constructor label '{label}' not found")
                self.ip = self.labels[label]
            elif op == 'IMPORT_PYTHON':
                # Import Python module (local file or installed package)
                module_name = arg
                try:
                    import importlib
                    import importlib.util
                    import os
                    
                    # First, try to import as a local Python file
                    local_file = f"{module_name}.py"
                    if os.path.exists(local_file):
                        # Import from local file
                        spec = importlib.util.spec_from_file_location(module_name, local_file)
                        if spec and spec.loader:
                            module = importlib.util.module_from_spec(spec)
                            sys.modules[module_name] = module
                            spec.loader.exec_module(module)
                            self.modules[module_name] = module
                        else:
                            raise ImportError(f"Cannot load module from {local_file}")
                    else:
                        # Fall back to importing as installed package
                        module = importlib.import_module(module_name)
                        self.modules[module_name] = module
                except ImportError as e:
                    print(f"Runtime Error: Cannot import module '{module_name}': {e}")
                    sys.exit(1)
            elif op == 'GET_ATTR':
                # Get attribute from object (module, dict, etc.)
                attr_name = arg
                obj = self.stack.pop()
                
                # Check if obj is a module name (string)
                if isinstance(obj, str) and obj in self.modules:
                    obj = self.modules[obj]
                
                try:
                    value = getattr(obj, attr_name)
                    self.stack.append(value)
                except AttributeError:
                    print(f"Runtime Error: Object has no attribute '{attr_name}'")
                    sys.exit(1)
            elif op == 'CALL_METHOD':
                # Call method on object
                # Format: CALL_METHOD method_name num_args
                parts = arg.split()
                method_name = parts[0]
                num_args = int(parts[1])
                
                # Pop arguments
                args = []
                for _ in range(num_args):
                    args.insert(0, self.to_python(self.stack.pop()))
                
                # Pop object
                obj = self.stack.pop()
                
                # Check if obj is a class instance (HeapPointer to dict)
                if isinstance(obj, HeapPointer) and obj.ptr in self.heap:
                    heap_obj = self.heap[obj.ptr]
                    if isinstance(heap_obj, dict):
                        # This is a class instance - find and call the method
                        # Push instance onto this_stack
                        self.this_stack.append(obj)
                        
                        # Find the method label
                        method_found = False
                        for label_name in self.labels:
                            if label_name.endswith(f"_{method_name}"):
                                # Push return address and frame pointer
                                self.stack.append(self.ip)
                                self.stack.append(self.fp)
                                self.fp = len(self.stack)
                                
                                # Push arguments
                                for a in args:
                                    self.stack.append(a)
                                
                                # Jump to method
                                self.ip = self.labels[label_name]
                                method_found = True
                                break
                        
                        if not method_found:
                            print(f"Runtime Error: Method '{method_name}' not found on class instance")
                            sys.exit(1)
                        continue  # Skip the rest of CALL_METHOD handling
                
                # Check if obj is a module name
                if isinstance(obj, str) and obj in self.modules:
                    obj = self.modules[obj]
                
                try:
                    # Get the method
                    method = getattr(obj, method_name)
                    # Call it with arguments
                    result = method(*args)
                    self.stack.append(result)
                except (AttributeError, TypeError) as e:
                    print(f"Runtime Error: Cannot call method '{method_name}': {e}")
                    sys.exit(1)
            elif op == 'CALL_METHOD_KW':
                # Call method on object with kwargs
                # Format: CALL_METHOD_KW method_name num_pos_args
                parts = arg.split()
                method_name = parts[0]
                num_pos_args = int(parts[1])
                
                # Pop kwargs dict
                kwargs_ptr = self.stack.pop()
                kwargs = {}
                if isinstance(kwargs_ptr, HeapPointer) and kwargs_ptr.ptr in self.heap:
                    kwargs = self.to_python(self.heap[kwargs_ptr.ptr])
                else:
                    print(f"Runtime Error: CALL_METHOD_KW expects dict for kwargs")
                    sys.exit(1)

                # Pop positional arguments
                args = []
                for _ in range(num_pos_args):
                    args.insert(0, self.to_python(self.stack.pop()))
                
                # Pop object
                obj = self.stack.pop()
                
                # Check if obj is a module name
                if isinstance(obj, str) and obj in self.modules:
                    obj = self.modules[obj]
                
                try:
                    # Get the method
                    method = getattr(obj, method_name)
                    # Call it with arguments
                    result = method(*args, **kwargs)
                    self.stack.append(result)
                except (AttributeError, TypeError) as e:
                    print(f"Runtime Error: Cannot call method '{method_name}': {e}")
                    sys.exit(1)
            elif op == 'CALL_OBJECT':
                # Call a callable object (e.g. Python object or closure)
                num_args = int(arg)
                
                # Object is at the top of the stack (pushed after args)
                obj = self.stack.pop()
                
                # Pop arguments
                args = []
                for _ in range(num_args):
                    args.insert(0, self.to_python(self.stack.pop()))
                
                # Check if obj is a module name (unlikely for direct call but possible)
                if isinstance(obj, str) and obj in self.modules:
                    print(f"Runtime Error: Cannot call module '{obj}' directly")
                    sys.exit(1)
                
                try:
                    # Call the object
                    result = obj(*args)
                    self.stack.append(result)
                except TypeError as e:
                    print(f"Runtime Error: Object is not callable: {e}")
                    sys.exit(1)
            elif op == 'CALL_OBJECT_KW':
                # Call a callable object with kwargs
                num_pos_args = int(arg)
                
                # Object is at the top of the stack
                obj = self.stack.pop()
                
                # Pop kwargs dict
                kwargs_ptr = self.stack.pop()
                kwargs = {}
                if isinstance(kwargs_ptr, HeapPointer) and kwargs_ptr.ptr in self.heap:
                    kwargs = self.to_python(self.heap[kwargs_ptr.ptr])
                else:
                    print(f"Runtime Error: CALL_OBJECT_KW expects dict for kwargs")
                    sys.exit(1)
                
                # Pop positional arguments
                args = []
                for _ in range(num_pos_args):
                    args.insert(0, self.to_python(self.stack.pop()))
                
                if isinstance(obj, str) and obj in self.modules:
                    print(f"Runtime Error: Cannot call module '{obj}' directly")
                    sys.exit(1)
                
                try:
                    # Call the object
                    result = obj(*args, **kwargs)
                    self.stack.append(result)
                except TypeError as e:
                    print(f"Runtime Error: Object is not callable or invalid arguments: {e}")
                    sys.exit(1)
            else:
                print(f"Unknown opcode: {op}")
                sys.exit(1)
            
            # if self.ip > -1:
            #     print(f"DEBUG: Finished {op}", flush=True)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python vm.py <program.asm>")
        sys.exit(1)
        
    vm = VM()
    try:
        vm.load_program(sys.argv[1])
        vm.run()
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"VM Crash at IP={vm.ip}, Op={vm.code[vm.ip] if vm.ip < len(vm.code) else 'EOF'}")
        sys.exit(1)
