#!/usr/bin/env python3
# Update visit_FunctionCall to handle class instantiation

with open('src/codegen.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find visit_FunctionCall and add class check at the beginning
output = []
i = 0
added_class_check = False

while i < len(lines):
    line = lines[i]
    
    # After the builtins definition in visit_FunctionCall, add class check
    if not added_class_check and "builtins = ['print', 'len'," in line:
        output.append(line)
        i += 1
        # Skip the void_builtins line
        output.append(lines[i])
        i += 1
        # Add empty line
        output.append(lines[i])
        i += 1
        
        # Add class instantiation check
        output.append("    # Check if this is a class instantiation\n")
        output.append("    if hasattr(self, 'classes') and node.name in self.classes:\n")
        output.append("        # Create new instance (dict)\n")
        output.append("        self.emit('DICT_NEW')\n")
        output.append("        self.emit('DUP')  # Keep instance on stack\n")
        output.append("        \n")
        output.append("        # Call constructor if it exists\n")
        output.append("        class_info = self.classes[node.name]\n")
        output.append("        if 'constructor' in class_info['methods']:\n")
        output.append("            # Push instance as 'this'\n")
        output.append("            self.emit('DUP')\n")
        output.append("            # Generate constructor arguments\n")
        output.append("            for arg in node.args:\n")
        output.append("                self.generate(arg)\n")
        output.append("            # Call constructor\n")
        output.append("            self.emit(f\"CALL_CONSTRUCTOR {class_info['methods']['constructor']} {len(node.args)}\")\n")
        output.append("            self.emit('POP')  # Discard constructor return value\n")
        output.append("        # Instance is left on stack\n")
        output.append("        return\n")
        output.append("    \n")
        added_class_check = True
        continue
    
    output.append(line)
    i += 1

with open('src/codegen.py', 'w', encoding='utf-8') as f:
    f.writelines(output)

print(f"✓ Added class instantiation to visit_FunctionCall: {added_class_check}")
