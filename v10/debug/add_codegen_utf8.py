#!/usr/bin/env python3
# Add class support to codegen.py - with UTF-8 encoding

with open('src/codegen.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Add visit_ClassDef and visit_ThisAccess at the end
# Find the last method (visit_CompoundAssign)
last_method_end = content.rfind('        self.emit(f\'STORE {offset}\')')
if last_method_end == -1:
    print("ERROR: Could not find end of last method")
    exit(1)

# Find the end of that line
insert_pos = content.find('\n', last_method_end) + 1

new_methods = '''
    def visit_ClassDef(self, node):
        # Store class metadata
        if not hasattr(self, 'classes'):
            self.classes = {}
        
        method_labels = {}
        for method in node.methods:
            method_label = f"CLASS_{node.name}_{method.name}"
            method_labels[method.name] = method_label
            
            self.emit(f'{method_label}:')
            self.enter_scope()
            
            for param_type, param_name in method.params:
                self.define_var(param_name)
            
            for stmt in method.body:
                self.generate(stmt)
            
            self.emit('PUSH 0')
            num_params = len(method.params)
            self.emit(f'RET {num_params}')
            self.exit_scope()
        
        self.classes[node.name] = {
            'methods': method_labels,
            'constructor': method_labels.get('constructor')
        }
    
    def visit_ThisAccess(self, node):
        self.emit('LOAD_THIS')
        self.emit(f'STRING_NEW {node.attribute}')
        self.emit('GET')
'''

content = content[:insert_pos] + new_methods + content[insert_pos:]

with open('src/codegen.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✓ Added visit_ClassDef() method")
print("✓ Added visit_ThisAccess() method")
