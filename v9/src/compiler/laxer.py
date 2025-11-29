import re
from dataclasses import dataclass

@dataclass
class Token:
    type: str
    value: any
    line: int
    column: int
    def __repr__(self):
        return f"Token({self.type!r}, {self.value!r}, line={self.line}, col={self.column})"

class LexerError(Exception):
    pass

class Lexer:
    # Ordered token patterns (order matters for multi-char ops and comments)
    TOKEN_SPEC = [
        ("MLCOMMENT", r"/\*[\s\S]*?\*/"),            # multi-line comment (skip)
        ("COMMENT",   r"//[^\n]*"),                  # single-line comment (skip)
        ("NUMBER",    r"\d+"),                       # integer literals
        ("ID",        r"[A-Za-z_]\w*"),              # identifiers / keywords
        ("STRING",    r'"(?:\\.|[^"\\])*"'),         # double-quoted strings with escapes
        ("OP",        r"<=|>=|==|!=|\+\+|--|\+=|-=|\*=|/=|->|&&|\|\||[+\-*/%<>=]"),
        ("LPAREN",    r"\("),
        ("RPAREN",    r"\)"),
        ("LBRACE",    r"\{"),
        ("RBRACE",    r"\}"),
        ("SEMICOL",   r";"),
        ("COMMA",     r","),
        ("NEWLINE",   r"\n"),
        ("SKIP",      r"[ \t\r]+"),                  # spaces, tabs, carriage returns
        ("MISMATCH",  r"."),                         # any other single char -> error
    ]

    # Example keywords for the tiny language
    KEYWORDS = {"func", "if", "else", "return", "print", "while", "for", "break", "continue"}

    def __init__(self, source: str):
        self.source = source
        self.regex = re.compile(
            "|".join(f"(?P<{name}>{pattern})" for name, pattern in self.TOKEN_SPEC),
            flags=re.MULTILINE
        )

    def tokenize(self):
        """
        Generator that yields Token objects and ends with an EOF token.
        Tracks line and column numbers accurately (including inside skipped comments).
        """
        line = 1
        line_start = 0  # index of the first char of the current line
        for mo in self.regex.finditer(self.source):
            kind = mo.lastgroup
            text = mo.group()
            start = mo.start()
            col = start - line_start + 1

            # NEWLINE updates line / line_start
            if kind == "NEWLINE":
                line += 1
                line_start = mo.end()
                continue

            # Skip whitespace & comments but update line counters if they contain newlines
            if kind in ("SKIP", "COMMENT", "MLCOMMENT"):
                if "\n" in text:
                    nl_count = text.count("\n")
                    line += nl_count
                    # position after the last newline in this matched text
                    last_nl_pos = text.rfind("\n")
                    line_start = start + last_nl_pos + 1
                continue

            # Produce tokens
            if kind == "NUMBER":
                token = Token("NUMBER", int(text), line, col)
            elif kind == "ID":
                if text in self.KEYWORDS:
                    token = Token("KEYWORD", text, line, col)
                else:
                    token = Token("ID", text, line, col)
            elif kind == "STRING":
                # remove surrounding quotes and unescape common sequences
                inner = text[1:-1]
                try:
                    unescaped = bytes(inner, "utf-8").decode("unicode_escape")
                except Exception:
                    # fall back to raw inner if decode fails
                    unescaped = inner
                token = Token("STRING", unescaped, line, col)
            elif kind == "OP":
                token = Token("OP", text, line, col)
            elif kind in ("LPAREN", "RPAREN", "LBRACE", "RBRACE", "SEMICOL", "COMMA"):
                token = Token(kind, text, line, col)
            elif kind == "MISMATCH":
                raise LexerError(f"Unexpected character {text!r} at line {line} column {col}")
            else:
                token = Token(kind, text, line, col)

            # If token contains newlines (rare), update line counters for future tokens
            if "\n" in text:
                nl_count = text.count("\n")
                line += nl_count
                last_nl_pos = text.rfind("\n")
                line_start = start + last_nl_pos + 1

            yield token

        # end
        yield Token("EOF", None, line, 1)

# ---------- quick demo ----------
if __name__ == "__main__":
    sample = """
    func fib(n) {
        if n <= 1 {
            return 1;
        }
        return fib(n - 1) + fib(n - 2);
    }
    print fib(10);
    """

    lexer = Lexer(sample)
    for tok in lexer.tokenize():
        print(tok)
