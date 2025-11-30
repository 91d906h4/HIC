#!/usr/bin/env python3
# Add CALL_CONSTRUCTOR and update CALL_METHOD in VM

with open('src/vm.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find CALL_METHOD and add CALL_CONSTRUCTOR before it
call_method_pos = content.find("elif op == 'CALL_METHOD':")
if call_method_pos == -1:
    print("ERROR: Could not find CALL_METHOD")
    exit(1)

call_constructor_code = """            elif op == 'CALL_CONSTRUCTOR':
                # Call class constructor: CALL_CONSTRUCTOR label num_args
                # Stack: [instance, arg1, arg2, ...]
                parts = arg.split()
                label = parts[0]
                num_args = int(parts[1])
                
                # Pop arguments
                args = []
                for _ in range(num_args):
                    args.insert(0, self.stack.pop())
                
                # Pop instance (will be bound to 'this')
                instance = self.stack.pop()
                
                # Push instance onto this_stack
                self.this_stack.append(instance)
                
                # Push return address and frame pointer
                self.stack.append(self.ip)
                self.stack.append(self.fp)
                self.fp = len(self.stack)
                
                # Push arguments
                for a in args:
                    self.stack.append(a)
                
                # Jump to constructor
                if label not in self.labels:
                    raise RuntimeError(f"Constructor label '{label}' not found")
                self.ip = self.labels[label] - 1
                
                # Note: constructor will RET, which will pop this_stack
            """

content = content[:call_method_pos] + call_constructor_code + content[call_method_pos:]

# Now update CALL_METHOD to handle this_stack
# Find the CALL_METHOD implementation and update it
call_method_impl = content.find("elif op == 'CALL_METHOD':", call_method_pos + len(call_constructor_code))
if call_method_impl == -1:
    print("ERROR: Could not find CALL_METHOD after insertion")
    exit(1)

# Find the end of CALL_METHOD (next elif or end of run method)
next_elif = content.find("\n            elif op ==", call_method_impl + 1)
if next_elif == -1:
    next_elif = content.find("\n        except", call_method_impl)

# Replace CALL_METHOD implementation
old_call_method = content[call_method_impl:next_elif]

new_call_method = """            elif op == 'CALL_METHOD':
                # Method call: obj.method(args)
                # Parse: CALL_METHOD method_name num_args
                parts = arg.split()
                method_name = parts[0]
                num_args = int(parts[1])
                
                # Pop arguments
                args = []
                for _ in range(num_args):
                    args.insert(0, self.stack.pop())
                
                # Pop object
                obj = self.stack.pop()
                
                # Convert to Python if needed
                args = [self.to_python(a) for a in args]
                obj_py = self.to_python(obj)
                
                # Check if obj is an instance (dict with methods)
                if isinstance(obj_py, dict):
                    # This is a class instance - bind 'this' and call method
                    self.this_stack.append(obj)
                    
                    # Find the method label (stored during class definition)
                    # For now, we'll look for CLASS_*_methodname pattern
                    # This is a simplified approach
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
                            self.ip = self.labels[label_name] - 1
                            method_found = True
                            break
                    
                    if not method_found:
                        raise RuntimeError(f"Method '{method_name}' not found on instance")
                else:
                    # Python object method call
                    method = getattr(obj_py, method_name)
                    result = method(*args)
                    self.stack.append(result if result is not None else 0)
"""

content = content[:call_method_impl] + new_call_method + content[next_elif:]

# Update RET to pop from this_stack if it exists
ret_pos = content.find("elif op == 'RET':")
if ret_pos != -1:
    # Find the end of RET implementation
    ret_end = content.find("\n            elif op ==", ret_pos + 1)
    if ret_end == -1:
        ret_end = content.find("\n        except", ret_pos)
    
    old_ret = content[ret_pos:ret_end]
    # Add this_stack pop at the end of RET
    new_ret = old_ret.rstrip() + "\n                # Pop from this_stack if we were in a method\n                if self.this_stack and len(self.stack) == self.fp:\n                    self.this_stack.pop()\n"
    content = content[:ret_pos] + new_ret + content[ret_end:]

with open('src/vm.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✓ Added CALL_CONSTRUCTOR opcode")
print("✓ Updated CALL_METHOD to handle class instances")
print("✓ Updated RET to pop from this_stack")
