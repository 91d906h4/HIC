"""Command line entry points.

    hyc <file.hy> [-o out.hyb]   compile source to bytecode (default: <file>.hyb)
    hy  <file>                   run a .hy source or a .hyb bytecode file

A single ``main`` dispatches on ``argv[0]``-style command names so both can live
in one module; see ``__main__.py`` for the executable wrappers.
"""

from __future__ import annotations

import argparse
import os
import sys
import time
from typing import List, Optional

from .errors import HyError
from .driver import compile_file
from .asm import dumps, loads, link
from .vm import VM


def _fail(err: HyError, source: Optional[str], filename: str) -> int:
    print(err.render(source, filename), file=sys.stderr)
    return 1


def cmd_compile(argv: List[str]) -> int:
    ap = argparse.ArgumentParser(prog="hyc", description="Compile HyLang to bytecode.")
    ap.add_argument("source", help="input .hy file")
    ap.add_argument("-o", "--output", help="output .hyb file")
    args = ap.parse_args(argv)

    output = args.output or os.path.splitext(args.source)[0] + ".hyb"
    source_text = None
    try:
        with open(args.source, "r", encoding="utf-8") as fh:
            source_text = fh.read()
        start = time.time()
        instrs = compile_file(args.source)
        with open(output, "w", encoding="utf-8") as fh:
            fh.write(dumps(instrs))
        elapsed = time.time() - start
    except HyError as err:
        return _fail(err, source_text, args.source)
    except OSError as err:
        print(f"Input Error: {err}", file=sys.stderr)
        return 1

    print(f"Compiled successfully -> {output}")
    print(f"Total compile time: {elapsed:.6f}s")
    return 0


def cmd_run(argv: List[str]) -> int:
    ap = argparse.ArgumentParser(prog="hy", description="Run HyLang source or bytecode.")
    ap.add_argument("file", help="a .hy source file or a .hyb bytecode file")
    args = ap.parse_args(argv)

    source_text = None
    try:
        if args.file.endswith(".hyb"):
            with open(args.file, "r", encoding="utf-8") as fh:
                instrs = loads(fh.read())
        else:
            with open(args.file, "r", encoding="utf-8") as fh:
                source_text = fh.read()
            instrs = compile_file(args.file)
        VM(link(instrs)).run()
    except HyError as err:
        return _fail(err, source_text, args.file)
    except OSError as err:
        print(f"Input Error: {err}", file=sys.stderr)
        return 1
    return 0


def main(argv: Optional[List[str]] = None) -> int:
    """Dispatch: ``hylang compile ...`` / ``hylang run ...``."""
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv or argv[0] not in ("compile", "run"):
        print("usage: python -m hylang {compile|run} ...", file=sys.stderr)
        return 2
    command, rest = argv[0], argv[1:]
    return cmd_compile(rest) if command == "compile" else cmd_run(rest)


if __name__ == "__main__":
    raise SystemExit(main())
