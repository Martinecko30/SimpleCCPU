import re
from enum import Enum
from typing import Any


class TokenType(Enum):
    WHITESPACE = r"\s+"
    COMMENT = r"//.*"

    COMPARE_EQUALS = r"=="
    NOT_EQUAL = r"\!="
    LESS_OR_EQUAL = r"\<="
    MORE_OR_EQUAL = r"\>="
    LESS_THAN = r"\<"
    MORE_THAN = r"\>"

    LOGICAL_AND = r"\&\&"
    LOGICAL_OR = r"\|\|"
    LOGICAL_NOT = r"\!"

    L_BRACKET = r"\("
    R_BRACKET = r"\)"
    L_CURLY = r"\{"
    R_CURLY = r"\}"
    L_SQUARE = r"\["
    R_SQUARE = r"\]"

    AMPERSAND = r"\&"

    DOT = r"\."
    COMMA = r"\,"

    PLUS = r"\+"
    MINUS = r"\-"
    STAR = r"\*"
    DIV = r"\/"

    EQUAL_SIGN = r"\="

    # KEYWORDS
    KEY_LET = r"let\b"
    KEY_WHILE = r"while\b"

    KEY_IF = r"if\b"
    KEY_ELSE = r"else\b"

    KEY_FUNC = r"func\b"
    KEY_RETURN = r"return\b"


    NUMBER = r"\d+(\.\d+)?"
    CHAR = r"'[^']*'"
    STRING = r'"[^"]*"'
    IDENTIFIER = r"[a-zA-Z_][a-zA-Z0-9_]*"

    INVALID = r"\?"

    def __init__(self, pattern: str):
        self.p_type: TokenType = self
        self.pattern = re.compile(pattern)

class Token:
    def __init__(self, t_type: TokenType, value: str, line: int, column: int):
        self.token_type = t_type
        self.value = value
        self.line = line
        self.column = column

    def __str__(self):
        return f"<{self.token_type.name}: '{self.value}' @ L{self.line}:C{self.column}>"

    def __repr__(self):
        return f"<{self.token_type.name}: '{self.value}' @ L{self.line}:C{self.column}>"

INVALID_TOKEN = Token(TokenType.INVALID, "", -1, -1)


class Tokenizer:
    def __init__(self, source_code: str):
        self.tokens: list[Token] = []
        self.lines = []

        for line in source_code.split('\n'):
            line = line.strip()
            if line:
                self.lines.append(line)

        self.parse()

    def parse(self):
        for i, line in enumerate(self.lines):
            position = 0
            while position < len(line):
                matched = False
                for token in TokenType:
                    match = token.pattern.match(line, position)
                    if match:
                        value = match.group()

                        if token not in (TokenType.WHITESPACE, TokenType.COMMENT):
                            self.tokens.append(Token(token.p_type, value, i + 1, position + 1))

                        position = match.end()
                        matched = True
                        break

                if not matched:
                    bad_char = line[position]
                    print(f"Unexpected character ({bad_char}) at position: {position}")
                    position += 1


if __name__ == "__main__":
    with open("../minilang/test.mini", 'r') as file:
        source = file.read()

    tokenizer = Tokenizer(source)
    for token in tokenizer.tokens:
        print(token)