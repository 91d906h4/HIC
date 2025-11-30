#!/usr/bin/env python3
"""
Add class parsing methods to parser_enhanced.py - FINAL VERSION
"""

with open('src/parser_enhanced.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

output = []
i = 0

while i < len(lines):
    line = lines[i]
    
    # 1. Add class_def method before function_def (line 565)
    if i == 564:  # Just before function_def
        output.append('    def class_def(self):\n')
        output.append('        self.eat(TokenType.KEYWORD)  # class\n')
        output.append('        class_name = self.current_token.value\n')
        output.append('        self.eat(TokenType.ID)\n')
        output.append('        self.eat(TokenType.LBRACE)\n')
        output.append('        \n')
        output.append('        methods = []\n')
        output.append("        while self.current_token.type == TokenType.KEYWORD and self.current_token.value == 'function':\n")
        output.append('            methods.append(self.function_def())\n')
        output.append('        \n')
        output.append('        self.eat(TokenType.RBRACE)\n')
        output.append('        return ClassDef(class_name, methods)\n')
        output.append('\n')
    
    # 2. Update statement() to handle 'class' - add after line with "if token.value == 'function':"
    if "if token.value == 'function':" in line and i > 340:  # In statement method
        output.append(line)
        i += 1
        # Skip to next line and add class check
        output.append("        elif token.value == 'class':\n")
        output.append("            return self.class_def()\n")
        continue
    
    # 3. Update factor() to handle 'this' - add before "elif token.type == TokenType.ID:"
    if "elif token.type == TokenType.ID:" in line and i > 170 and i < 230:  # In factor method
        # Add this check before ID check
        output.append("        elif token.type == TokenType.KEYWORD and token.value == 'this':\n")
        output.append("            self.eat(TokenType.KEYWORD)  # this\n")
        output.append("            self.eat(TokenType.DOT)\n")
        output.append("            attr = self.current_token.value\n")
        output.append("            self.eat(TokenType.ID)\n")
        output.append("            return ThisAccess(attr)\n")
    
    output.append(line)
    i += 1

# Write final parser
with open('src/parser.py', 'w', encoding='utf-8') as f:
    f.writelines(output)

print("✓ Created complete parser.py with class support")
print(f"  Total lines: {len(output)}")
print("  - Added ClassDef and ThisAccess AST nodes")
print("  - Added class_def() method")
print("  - Updated statement() to handle 'class'")
print("  - Updated factor() to handle 'this'")
