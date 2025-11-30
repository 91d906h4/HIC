#!/usr/bin/env python3
"""
Generate enhanced parser.py with class support
"""
import re

# Read original parser
with open('src/parser.py.backup', 'r', encoding='utf-8') as f:
    lines = f.readlines()

output = []
i = 0

while i < len(lines):
    line = lines[i]
    output.append(line)
    
    # After StringLiteral class, add ClassDef and ThisAccess
    if line.strip() == 'class StringLiteral(AST):':
        # Add the rest of StringLiteral
        i += 1
        while i < len(lines) and not lines[i].startswith('class '):
            output.append(lines[i])
            i += 1
        
        # Now add our new classes
        output.append('\n')
        output.append('class ClassDef(AST):\n')
        output.append('    def __init__(self, name, methods):\n')
        output.append('        self.name = name\n')
        output.append('        self.methods = methods  # list of FunctionDef nodes\n')
        output.append('\n')
        output.append('class ThisAccess(AST):\n')
        output.append('    def __init__(self, attribute):\n')
        output.append('        self.attribute = attribute  # attribute name\n')
        
        continue
    
    i += 1

# Write enhanced parser
with open('src/parser_enhanced.py', 'w', encoding='utf-8') as f:
    f.writelines(output)

print("✓ Created parser_enhanced.py with ClassDef and ThisAccess")
print(f"  Original: {len(lines)} lines")
print(f"  Enhanced: {len(output)} lines")
