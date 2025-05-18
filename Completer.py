from prompt_toolkit import PromptSession
from prompt_toolkit.completion import Completer, Completion


class DynamicCompleter(Completer):
    def __init__(self):
        self.functions = {"help", "index", "load", "save", "add", "q", "bq", "top", "exit"}
        self.query_start = "$"
        self.query = set()

    def get_completions(self, document, complete_event):
        text = document.text
        splited = text.split(" ")

        if not text:
            yield from self.suggest_all(self.functions, 0)

        elif len(splited) == 1:
            yield from self.suggest_pattern(self.functions, splited[0])

        elif text.startswith("q"):

            if len(splited) == 2:
                if len(splited[1]) == 0:
                    yield Completion(self.query_start, start_position=0)  # start query with '$'
                elif len(splited[1]) == 1 and splited[1].startswith(self.query_start):
                    yield from self.suggest_all(self.query, 0)  # suggest all words after '$'
                elif len(splited[1]) > 1 and splited[1].startswith(self.query_start):
                    yield from self.suggest_pattern(self.query, splited[1])  # suggest all words after '$'
                else:
                    yield from self.suggest_all(set(), 0)  # query doesn't start with '$'

            elif len(splited) > 2:
                if len(splited[-1]) == 0:
                    yield from self.suggest_all(self.query, 0)        # suggest all words after '$'
                else:
                    yield from self.suggest_pattern(self.query, splited[-1])  # suggest matching words
        else:
            yield from self.suggest_all(set(), 0)  # is not query

    def suggest_all(self, words: set, position: int):
        for word in words:
            yield Completion(word, start_position=position)

    def suggest_pattern(self, words: set, text: str):
        if text.startswith(self.query_start):
            text = text[1:]

        for word in words:
            if word.startswith(text):
                yield Completion(word, start_position=-len(text))

    def set_key_words(self, keywords: set):
        self.query = keywords
