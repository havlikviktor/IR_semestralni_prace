# File: boolean/parser.py
from indexer import Entry
from tokenizer import *
from documents_manager import Document


# AST Node definition
class Node:
    all_docs: set[str] = {}

    def evaluate(self, index: dict[str, list[Entry]], available_docs=None) -> set[str]:
        raise NotImplementedError()

    def simplify(self) -> 'Node':
        return self

    @classmethod
    def initialize_docs(cls, index: dict[str, list[Entry]]):
        cls.all_docs = {entry.doc_id for entries in index.values() for entry in entries}

    @classmethod
    def get_all_docs(cls) -> set[str]:
        return cls.all_docs


class TermNode(Node):
    def __init__(self, value: str):
        self.value: str = value

    def __repr__(self) -> str:
        return f"Term({self.value})"

    def evaluate(self, index: dict[str, list[Entry]],  available_docs=None) -> set[str]:
        return {entry.doc_id for entry in index.get(self.value, [])}


class NotNode(Node):
    def __init__(self, child: Node):
        self.child: Node = child

    def __repr__(self) -> str:
        return f"Not({self.child})"

    def evaluate(self, index, available_docs=None):
        base = available_docs if available_docs is not None else Node.all_docs
        return base - self.child.evaluate(index)

    def simplify(self) -> 'Node':
        # Apply De Morgan's Law: NOT(NOT(A)) -> A
        if isinstance(self.child, NotNode):
            return self.child.child.simplify()  # Simplify nested NOT

        return self


class AndNode(Node):
    def __init__(self, left: Node, right: Node):
        self.left: Node = left
        self.right: Node = right

    def __repr__(self) -> str:
        return f"And({self.left}, {self.right})"

    def evaluate(self, index, available_docs=None):
        left_result = self.left.evaluate(index, available_docs)
        right_result = self.right.evaluate(index, left_result)
        return left_result & right_result


class OrNode(Node):
    def __init__(self, left: Node, right: Node):
        self.left: Node = left
        self.right: Node = right

    def __repr__(self) -> str:
        return f"Or({self.left}, {self.right})"

    def evaluate(self, index: dict[str, list[Entry]], available_docs=None) -> set[str]:
        return self.left.evaluate(index) | self.right.evaluate(index)


class BooleanParser:
    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.pos = 0

    def current_token(self):
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None

    def consume(self, expected_type=None):
        token = self.current_token()
        if token is None:
            return None
        if expected_type and token.token_type != expected_type:
            raise SyntaxError(f"Expected {expected_type}, got {token.token_type}")
        self.pos += 1
        return token

    def parse(self) -> Node:
        result = self.parse_expr()
        if self.current_token() is not None:
            raise SyntaxError("Unexpected token at the end")
        return result

    def parse_expr(self) -> Node:
        node = self.parse_term()
        while self.current_token() and self.current_token().token_type == TokenType.OR:
            self.consume(TokenType.OR)
            right = self.parse_term()
            node = OrNode(node, right)
        return node

    def parse_term(self) -> Node:
        node = self.parse_factor()
        while self.current_token() and self.current_token().token_type == TokenType.AND:
            self.consume(TokenType.AND)
            right = self.parse_factor()
            node = AndNode(node, right)
        return node

    def parse_factor(self) -> Node:
        token = self.current_token()
        if token and token.token_type == TokenType.NOT:
            self.consume(TokenType.NOT)
            child = self.parse_base()
            return NotNode(child)
        else:
            return self.parse_base()

    def parse_base(self) -> Node:
        token = self.current_token()
        if token is None:
            raise SyntaxError("Unexpected end of input")
        if token.token_type == TokenType.LPAREN:
            self.consume(TokenType.LPAREN)
            node = self.parse_expr()
            self.consume(TokenType.RPAREN)
            return node
        elif token.token_type == TokenType.WORD:
            value = self.consume(TokenType.WORD).processed_form
            return TermNode(value)
        else:
            raise SyntaxError(f"Unexpected token: {token}")
