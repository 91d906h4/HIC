"""Parser package: token stream -> AST."""

from . import ast
from .parser import Parser, parse

__all__ = ["ast", "Parser", "parse"]
