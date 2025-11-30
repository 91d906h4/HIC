#!/usr/bin/env python3
# Add 'this' support to parser.py

with open('src/parser.py', 'r') as f:
    lines = f.readlines()

# Find the line with "elif token.type == TokenType.ID:" in factor()
# We want to add 'this' handling before it
output = []
i = 0
added_this_in_factor = False
added_this_in_statement = False

while i < len(lines):
    line = lines[i]
    
    # Add 'this' in factor() before ID check (around line 220-230)
    if not added_this_in_factor and "elif token.type == TokenType.ID:" in line and i > 170 and i < 240:
        # Add this handling before ID
        output.append("        elif token.type == TokenType.KEYWORD and token.value == 'this':\n")
        output.append("            self.eat(TokenType.KEYWORD)  # this\n")
        output.append("            self.eat(TokenType.DOT)\n")
        output.append("            attr = self.current_token.value\n")
        output.append("            self.eat(TokenType.ID)\n")
        output.append("            return ThisAccess(attr)\n")
        added_this_in_factor = True
    
    # Add 'this' in statement() before ID check (around line 360-370)
    if not added_this_in_statement and "elif token.type == TokenType.ID:" in line and i > 340:
        # Add this handling before ID
        output.append("            elif token.value == 'this':\n")
        output.append("                self.eat(TokenType.KEYWORD)  # this\n")
        output.append("                self.eat(TokenType.DOT)\n")
        output.append("                attr = self.current_token.value\n")
        output.append("                self.eat(TokenType.ID)\n")
        output.append("                if self.current_token.type == TokenType.ASSIGN:\n")
        output.append("                    self.eat(TokenType.ASSIGN)\n")
        output.append("                    right = self.expr()\n")
        output.append("                    self.eat(TokenType.SEMICOLON)\n")
        output.append("                    return Assign(ThisAccess(attr), right)\n")
        output.append("                else:\n")
        output.append("                    self.error('Expected assignment after this.attribute')\n")
        added_this_in_statement = True
    
    output.append(line)
    i += 1

with open('src/parser.py', 'w') as f:
    f.writelines(output)

print(f"✓ Added 'this' to factor(): {added_this_in_factor}")
print(f"✓ Added 'this' to statement(): {added_this_in_statement}")
