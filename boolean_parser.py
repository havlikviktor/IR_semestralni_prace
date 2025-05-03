# File: boolean/parser.py
from indexer import Entry
from tokenizer import *
from documents_manager import Document


# AST Node definition
class Node:
    def evaluate(self, index: dict[str, list[Entry]]) -> set[str]:
        raise NotImplementedError()


class TermNode(Node):
    def __init__(self, value: str):
        self.value: str = value

    def __repr__(self) -> str:
        return f"Term({self.value})"

    def evaluate(self, index: dict[str, list[Entry]]) -> set[str]:
        return {entry.doc_index for entry in index.get(self.value, [])}


class NotNode(Node):
    def __init__(self, child: Node):
        self.child: Node = child

    def __repr__(self) -> str:
        return f"Not({self.child})"

    def evaluate(self, index: dict[str, list[Entry]]) -> set[str]:
        all_docs = {entry.doc_index for entries in index.values() for entry in entries}
        return all_docs - self.child.evaluate(index)


class AndNode(Node):
    def __init__(self, left: Node, right: Node):
        self.left: Node = left
        self.right: Node = right

    def __repr__(self) -> str:
        return f"And({self.left}, {self.right})"

    def evaluate(self, index: dict[str, list[Entry]]) -> set[str]:
        return self.left.evaluate(index) & self.right.evaluate(index)


class OrNode(Node):
    def __init__(self, left: Node, right: Node):
        self.left: Node = left
        self.right: Node = right

    def __repr__(self) -> str:
        return f"Or({self.left}, {self.right})"

    def evaluate(self, index: dict[str, list[Entry]]) -> set[str]:
        return self.left.evaluate(index) | self.right.evaluate(index)


class BooleanParser:
    def __init__(self, query: Document):
        self.tokens: list[tuple[str, str]] = self.tokenize(query)
        self.pos: int = 0

    def tokenize(self, document: Document) -> list[tuple[str, str]]:
        tokens: list[tuple[str, str]] = []

        for token in document.tokens:
            processed_str: str = token.processed_form
            if processed_str == "AND":
                tokens.append(('AND', processed_str))
            elif processed_str == "OR":
                tokens.append(('OR', processed_str))
            elif processed_str == "NOT":
                tokens.append(('NOT', processed_str))
            elif processed_str == "(":
                tokens.append(('LPAREN', processed_str))
            elif processed_str == ")":
                tokens.append(('RPAREN', processed_str))
            else:
                tokens.append(('TERM', processed_str))

        return tokens

    def current_token(self):
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None, None

    def consume(self, expected_kind):
        token = self.current_token()
        if token[0] is None:
            return token
        if expected_kind and token[0] != expected_kind:
            raise SyntaxError(f"Expected token {expected_kind} but got {token[0]}")
        self.pos += 1
        return token

    def parse(self) -> Node:
        result = self.parse_expr()
        if self.current_token()[0] is not None:
            print(f"token is {self.current_token()[0]}")
            raise SyntaxError("Unexpected token at the end")
        return result

    def parse_expr(self) -> Node:
        node = self.parse_term()
        while True:
            token = self.current_token()
            if token[0] == 'OR':
                self.consume('OR')
                right = self.parse_term()
                node = OrNode(node, right)
            else:
                break
        return node

    def parse_term(self) -> Node:
        node = self.parse_factor()
        while True:
            token = self.current_token()
            if token[0] == 'AND':
                self.consume('AND')
                right = self.parse_factor()
                node = AndNode(node, right)
            else:
                break
        return node

    def parse_factor(self) -> Node:
        token = self.current_token()
        if token[0] == 'NOT':
            self.consume('NOT')
            child = self.parse_base()
            return NotNode(child)
        else:
            return self.parse_base()

    def parse_base(self) -> Node:
        token = self.current_token()
        if token[0] == 'LPAREN':
            self.consume('LPAREN')
            node = self.parse_expr()
            self.consume('RPAREN')
            return node
        elif token[0] == 'TERM':
            term = self.consume('TERM')[1]
            return TermNode(term)
        else:
            raise SyntaxError("Unexpected token: " + str(token))
