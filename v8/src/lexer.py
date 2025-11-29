import re

# Define token types with regex patterns (longest match first)
TOKENS = [
    # Keywords
    ("IF", r"if"),
    ("VAR", r"var"),
    ("FOR", r"for"),
    ("FUNC", r"func"),
    ("ELIF", r"elif"),
    ("ELSE", r"else"),
    ("WHILE", r"while"),
    ("RETURN", r"return"),

    # Identifiers
    ("ID", r"[a-zA-Z_][a-zA-Z0-9_]*"),
    ("STRING", r"\"[^\"]*\""),
    ("NUMBER", r"\d+"),
    
    # Multi-character operators
    ("EQ", r"=="),
    ("NEQ", r"!="),
    ("GTE", r">="),
    ("LTE", r"<="),
    ("AND", r"&&"),
    ("OR", r"\|\|"),

    # Single-character operators
    ("ASSIGN", r"="),
    ("GT", r">"),
    ("LT", r"<"),
    ("PLUS", r"\+"),
    ("MINUS", r"-"),
    ("MULT", r"\*"),
    ("DIV", r"/"),
    ("LPAREN", r"\("),
    ("RPAREN", r"\)"),
    ("LBRACE", r"\{"),
    ("RBRACE", r"\}"),
    ("SEMICOLON", r";"),
    ("COMMA", r","),

    # Whitespace (to skip)
    ("WS", r"\s+"),
]

class Lexer:
    def __init__(self, rules):
        self.rules = [(name, re.compile(pattern)) for name, pattern in rules]

    def tokenize(self, text):
        tokens = []
        pos = 0

        while pos < len(text):
            best_match = None
            best_token = None

            # Try matching the longest token
            for name, pattern in self.rules:
                match = pattern.match(text, pos)

                # Skip if no match
                if not match:
                    continue

                match_text = match.group(0)

                if best_match is None or len(match_text) > len(best_match):
                    best_match = match_text
                    best_token = name

            if best_match:
                # Skip whitespace
                if best_token != "WS":
                    tokens.append((best_token, best_match))

                pos += len(best_match)

            else:
                raise ValueError(f"Unexpected character at position {pos}: {text[pos]}")

        return tokens


if __name__ == "__main__":
    lexer = Lexer(TOKENS)
    input_text = """
    func fib(n) {
        if (n <= 1) {
            return n;
        }

        return fib(n - 1) + fib(n - 2);
    }
    func main() {
        var result = fib(10);

        print("Hello, world!");
        print(result);

        return 0;
    }
    """
    tokens = lexer.tokenize(input_text)

    # Print tokens
    for token in tokens:
        print(token)
