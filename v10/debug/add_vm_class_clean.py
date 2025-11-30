#!/usr/bin/env python3
"""
Clean script to add class support to VM
"""

# Read VM file
with open('src/vm.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find line numbers for insertions
init_line = None
throw_end_line = None

for i, line in enumerate(lines):
    if 'self.global_count = 0' in line:
        init_line = i + 1  # Insert after this line
    if 'sys.exit(1)' in line and i > 400 and i < 460:  # In THROW block
        throw_end_line = i + 1  # Insert after this line

if init_line is None or throw_end_line is None:
    print(f"ERROR: Could not find insertion points (init={init_line}, throw={throw_end_line})")
    exit(1)

# Insert this_stack in __init__
lines.insert(init_line, '        self.this_stack = []  # Stack of current instances for methods\n')

# Insert LOAD_THIS and CALL_CONSTRUCTOR after THROW
opcodes = '''            elif op == 'LOAD_THIS':
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
'''

lines.insert(throw_end_line + 1, opcodes)  # +1 because we inserted one line earlier

# Find RET opcode and add this_stack pop
for i, line in enumerate(lines):
    if 'self.stack.append(ret_val)' in line and i > 200 and i < 300:
        lines.insert(i + 1, '                if self.this_stack:\n')
        lines.insert(i + 2, '                    self.this_stack.pop()\n')
        break

# Write back
with open('src/vm.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print("✓ Added this_stack to __init__")
print("✓ Added LOAD_THIS opcode")
print("✓ Added CALL_CONSTRUCTOR opcode")
print("✓ Updated RET to pop from this_stack")
