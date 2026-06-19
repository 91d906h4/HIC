"""High-level pipeline: source -> tokens -> AST -> bytecode, with #import expansion."""

from __future__ import annotations

import os
from typing import List, Optional

from .errors import HyError
from .lexer import tokenize
from .parser import parse
from .parser import ast
from .codegen import compile_program
from .codegen.isa import Instruction


def _resolve_module(module: str, base_dir: Optional[str]) -> str:
    """Locate an imported module file (searches ``<base>/hmodule`` then cwd)."""
    candidates = []
    if base_dir:
        candidates.append(os.path.join(base_dir, "hmodule", module))
    candidates.append(os.path.join("hmodule", module))
    candidates.append(module)
    for path in candidates:
        if os.path.isfile(path):
            return path
    raise HyError(f"Import module {module!r} not found.")


def _expand_imports(program: ast.Program, base_dir: Optional[str],
                    seen: set) -> List[ast.Stmt]:
    """Replace Import statements with the imported file's statements."""
    main_stmts: List[ast.Stmt] = []
    imported_stmts: List[ast.Stmt] = []
    for stmt in program.statements:
        if isinstance(stmt, ast.Import):
            path = _resolve_module(stmt.module, base_dir)
            if path in seen:
                continue
            seen.add(path)
            with open(path, "r", encoding="utf-8") as fh:
                sub = parse(tokenize(fh.read()))
            imported_stmts.extend(
                _expand_imports(sub, os.path.dirname(path) or base_dir, seen)
            )
        else:
            main_stmts.append(stmt)
    # Imported declarations/functions go after the main statements, matching the
    # original behaviour (functions resolve by name, so order is irrelevant).
    return main_stmts + imported_stmts


def compile_source(source: str, base_dir: Optional[str] = None) -> List[Instruction]:
    """Compile HyLang source text into a flat instruction list."""
    program = parse(tokenize(source))
    expanded = ast.Program(_expand_imports(program, base_dir, set()))
    return compile_program(expanded)


def compile_file(path: str) -> List[Instruction]:
    """Compile a ``.hy`` file into instructions."""
    with open(path, "r", encoding="utf-8") as fh:
        source = fh.read()
    return compile_source(source, base_dir=os.path.dirname(os.path.abspath(path)))
