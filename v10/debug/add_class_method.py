#!/usr/bin/env python3
# Add class_def method to parser.py

with open('src/parser.py', 'r') as f:
    content = f.read()

# Find the function_def method
func_def_pos = content.find('    def function_def(self):')
if func_def_pos == -1:
    print("ERROR: Could not find function_def")
    exit(1)

# Insert class_def before function_def
class_def_method = '''    def class_def(self):
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

content = content[:func_def_pos] + class_def_method + content[func_def_pos:]

# Update parse() to handle class
parse_pos = content.find("if self.current_token.type == TokenType.KEYWORD and self.current_token.value == 'function':")
if parse_pos == -1:
    print("ERROR: Could not find parse function check")
    exit(1)

# Find the line after function check
next_line_pos = content.find('\n', parse_pos)
insert_pos = content.find('\n', next_line_pos + 1) + 1

class_check = "            elif self.current_token.type == TokenType.KEYWORD and self.current_token.value == 'class':\n                statements.append(self.class_def())\n"

content = content[:insert_pos] + class_check + content[insert_pos:]

with open('src/parser.py', 'w') as f:
    f.write(content)

print("✓ Added class_def() method")
print("✓ Updated parse() to handle 'class'")
