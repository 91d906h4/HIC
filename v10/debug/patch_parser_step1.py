#!/usr/bin/env python3
"""
Script to add class support to parser.py
"""

# Read the current parser.py
with open('src/parser.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find where to insert ClassDef and ThisAccess (after NoneLiteral)
insert_point = content.find('class NoneLiteral(AST):\n    def __init__(self):\n        pass\n')
if insert_point == -1:
    print("ERROR: Could not find NoneLiteral class")
    exit(1)

# Find the end of NoneLiteral class
insert_point = content.find('\n\nclass Parser:', insert_point)
if insert_point == -1:
    print("ERROR: Could not find Parser class")
    exit(1)

# Insert the new AST nodes
new_classes = '''

class ClassDef(AST):
    def __init__(self, name, methods):
        self.name = name
        self.methods = methods  # list of FunctionDef nodes

class ThisAccess(AST):
    def __init__(self, attribute):
        self.attribute = attribute  # attribute name
'''

content = content[:insert_point] + new_classes + content[insert_point:]

# Write back
with open('src/parser.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✓ Added ClassDef and ThisAccess AST nodes")
