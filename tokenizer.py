import re
from dataclasses import dataclass
from enum import Enum


class TokenType(Enum):
    NUMBER = 1
    WORD = 2
    TAG = 3
    PUNCT = 4
    STOP_W = 5
    MEANINGLESS = 6


@dataclass
class Token:
    processed_form: str
    position: int
    length: int
    token_type: TokenType = TokenType.WORD

    def __repr__(self):
        return self.processed_form


class RegexMatchTokenizer:
    num_pattern = r'(\d+[.,]?\d*)'
    word_pattern = r'(\w+)'  # matches words
    html_tag_pattern = r'(<[^>]*>)'  # matches html tags
    punctuation_pattern = r'([^\w\s]+)'  # matches punctuation
    default_pattern = f'{num_pattern}|{word_pattern}|{html_tag_pattern}|{punctuation_pattern}'

    def __init__(self, pattern: str = default_pattern):
        self.pattern = pattern

    def tokenize(self, document: str) -> list[Token]:
        tokens = []
        for match in re.finditer(re.compile(self.pattern, re.UNICODE), document):
            token = Token(match.group(), match.start(), match.end() - match.start(), TokenType(match.lastindex))
            tokens.append(token)
        return tokens
