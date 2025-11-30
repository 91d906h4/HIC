#!/usr/bin/env python3
"""
Add class parsing methods to parser_enhanced.py
"""

# Read the enhanced parser
with open('src/parser_enhanced.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Add class_def method before the 'def program' method
class_def_method = '''
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

'''

# Find where to insert (before 'def program')
insert_pos = content.find('    def program(self):')
if insert_pos == -1:
    print("ERROR: Could not find program method")
    exit(1)

content = content[:insert_pos] + class_def_method + content[insert_pos:]

# 2. Update statement() to handle 'class'
# Find the statement method and add class handling
statement_method_start = content.find('    def statement(self):')
if statement_method_start == -1:
    print("ERROR: Could not find statement method")
    exit(1)

# Find the line with "if token.value == 'function':"
function_check = content.find("if token.value == 'function':", statement_method_start)
if function_check == -1:
    print("ERROR: Could not find function check in statement")
    exit(1)

# Insert class check before function check
class_check = """        elif token.value == 'class':
            return self.class_def()
"""

# Find the exact position (after the previous elif/if)
insert_at = content.rfind('\n', statement_method_start, function_check) + 1
content = content[:insert_at] + class_check + content[insert_at:]

# 3. Update factor() to handle 'this'
# Find "elif token.type == TokenType.ID:"
factor_method = content.find('    def factor(self):')
id_check = content.find("elif token.type == TokenType.ID:", factor_method)
if id_check == -1:
    print("ERROR: Could not find ID check in factor")
    exit(1)

# Add this check before ID check
this_check = """        elif token.type == TokenType.KEYWORD and token.value == 'this':
            self.eat(TokenType.KEYWORD)  # this
            self.eat(TokenType.DOT)
            attr = self.current_token.value
            self.eat(TokenType.ID)
            return ThisAccess(attr)
"""

insert_at = content.rfind('\n', factor_method, id_check) + 1
content = content[:insert_at] + this_check + content[insert_at:]

# Write the final parser
with open('src/parser.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✓ Created complete parser.py with class support")
print("  - Added class_def() method")
print("  - Updated statement() to handle 'class'")
print("  - Updated factor() to handle 'this'")
