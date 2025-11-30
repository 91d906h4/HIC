#!/usr/bin/env python3
# Add class support to VM

with open('src/vm.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Add this_stack to __init__
init_pos = content.find('self.global_count = 0')
if init_pos == -1:
    print("ERROR: Could not find global_count in __init__")
    exit(1)

insert_pos = content.find('\n', init_pos) + 1
content = content[:insert_pos] + '        self.this_stack = []  # Stack of current instances for methods\n        self.classes = {}  # Class metadata\n' + content[insert_pos:]

# 2. Add LOAD_THIS opcode before IMPORT_PYTHON
import_python_pos = content.find("elif op == 'IMPORT_PYTHON':")
if import_python_pos == -1:
    print("ERROR: Could not find IMPORT_PYTHON")
    exit(1)

load_this_code = """            elif op == 'LOAD_THIS':
                # Push current instance onto stack
                if not self.this_stack:
                    raise RuntimeError("LOAD_THIS called outside of method context")
                self.stack.append(self.this_stack[-1])
"""

content = content[:import_python_pos] + load_this_code + '            ' + content[import_python_pos:]

with open('src/vm.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✓ Added this_stack and classes to VM.__init__")
print("✓ Added LOAD_THIS opcode")
