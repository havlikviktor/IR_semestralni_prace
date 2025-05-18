from prompt_toolkit import PromptSession
from prompt_toolkit.completion import Completer, Completion


class DynamicCompleter(Completer):
    def __init__(self):
        self.words1 = ['apple', 'banana', 'cherry']
        self.words2 = ['query', 'quick', 'vole', 'vaha', 'ahoj']

    def get_completions(self, document, complete_event):
        text = document.text
        line_start: bool = False
        if not text:
            line_start = True
            words = self.words1

        elif len(text.split()) == 1:
            words = self.words1

        elif text.startswith("q"):
            words = self.words2

        else:
            words = []

        for word in words:
            if line_start or word.startswith(text.split()[-1]):
                yield Completion(word, start_position=-len(text))


session = PromptSession(completer=DynamicCompleter())

while True:
    try:
        text = session.prompt('Zadej text: ')
        print(f'Zadal jsi: {text}')
    except (EOFError, KeyboardInterrupt):
        break
