"""Shared test helpers."""

from __future__ import annotations

import os
from typing import List, Optional

from hylang.driver import compile_source
from hylang.asm import dumps, loads, link
from hylang.vm import VM

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXAMPLES_DIR = os.path.join(PROJECT_ROOT, "examples")


def run(source: str, base_dir: Optional[str] = None,
        roundtrip: bool = False) -> List[str]:
    """Compile and run ``source``; return printed lines.

    If ``roundtrip`` is set, the program is serialised to .hyb text and reloaded
    before execution, exercising the assembler.
    """
    instrs = compile_source(source, base_dir=base_dir)
    if roundtrip:
        instrs = loads(dumps(instrs))
    out: List[str] = []
    VM(link(instrs), out=out.append).run()
    return out


def run_file(path: str, roundtrip: bool = False) -> List[str]:
    with open(path, "r", encoding="utf-8") as fh:
        source = fh.read()
    return run(source, base_dir=os.path.dirname(os.path.abspath(path)),
               roundtrip=roundtrip)
