"""Allow ``python -m hylang {compile|run} ...``."""

from .cli import main

if __name__ == "__main__":
    raise SystemExit(main())
