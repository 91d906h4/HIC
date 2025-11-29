import sys
import os
from lexer import Lexer
from parser import Parser, Import, FunctionDef
from codegen import CodeGen

def parse_file(filename):
    with open(filename, 'r') as f:
        text = f.read()
    
    lexer = Lexer(text)
    parser = Parser(lexer)
    return parser.parse()

def compile_program(filename):
    base_dir = os.path.dirname(os.path.abspath(filename))
    ast = parse_file(filename)
    
    # Handle imports
    # We will look for Import statements, parse the files, and add their functions to the main AST.
    # We'll remove the Import statements from the AST to avoid codegen errors.
    
    imported_functions = []
    statements_to_keep = []
    
    for stmt in ast.statements:
        if isinstance(stmt, Import):
            import_path = os.path.join(base_dir, stmt.filename)
            imported_ast = parse_file(import_path)
            # We only import functions from the other file for now
            for imported_stmt in imported_ast.statements:
                if isinstance(imported_stmt, FunctionDef):
                    imported_functions.append(imported_stmt)
        else:
            statements_to_keep.append(stmt)
            
    # Prepend imported functions to the AST
    ast.statements = imported_functions + statements_to_keep
    
    codegen = CodeGen()
    instructions = codegen.generate(ast)
    
    return instructions

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python compiler.py <source_file>")
        sys.exit(1)
        
    source_file = sys.argv[1]
    output_file = source_file.replace('.src', '.asm')
    
    try:
        instructions = compile_program(source_file)
        with open(output_file, 'w') as f:
            for instr in instructions:
                f.write(instr + '\n')
        print(f"Compiled {source_file} to {output_file}")
    except Exception as e:
        print(f"Compilation failed: {e}")
        sys.exit(1)
