import re
from abc import ABC
from dataclasses import dataclass, asdict
from enum import Enum


class TokenType(Enum):
    NUMBER = 1
    WORD = 2
    TAG = 3
    PUNCT = 4
    STOP_W = 5
    AND = 6
    OR = 7
    NOT = 8
    LPAREN = 9
    RPAREN = 10



@dataclass
class Token:
    processed_form: str
    position: int
    length: int
    token_type: TokenType = TokenType.WORD

    def __repr__(self):
        return self.processed_form

    def to_dict(self):
        data = asdict(self)
        data["token_type"] = self.token_type.name  # Enum jako string
        return data

    @staticmethod
    def from_dict(data):
        return Token(
            processed_form=data["processed_form"],
            position=data["position"],
            length=data["length"],
            token_type=TokenType[data["token_type"]]  # zpět na enum
        )


class Tokenizer(ABC):

    def tokenize(self, text: str) -> list[Token]:
        raise NotImplementedError


class RegexMatchTokenizer(Tokenizer):
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


class BooleanMatchTokenizer(Tokenizer):
    token_spec = [
        ("AND", r'\bAND\b', TokenType.AND),
        ("OR", r'\bOR\b', TokenType.OR),
        ("NOT", r'\bNOT\b', TokenType.NOT),
        ("LPAREN", r'\(', TokenType.LPAREN),
        ("RPAREN", r'\)', TokenType.RPAREN),
        ("TERM", r'\w+(?:\.\w+)*', TokenType.WORD),
        ("SKIP", r'\s+', None),
    ]

    def __init__(self):
        pattern = "|".join(f"(?P<{name}>{regex})" for name, regex, *_ in self.token_spec)
        self.regex = re.compile(pattern, re.UNICODE)

    def tokenize(self, document: str) -> list[Token]:
        tokens = []
        for match in self.regex.finditer(document):
            kind = match.lastgroup
            if kind == "SKIP":
                continue
            value = match.group()
            token_type = next(t for name, _, t in self.token_spec if name == kind)
            tokens.append(Token(value, match.start(), len(value), token_type))
        return tokens
