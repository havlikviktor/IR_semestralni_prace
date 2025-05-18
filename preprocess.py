from abc import ABC
from tokenizer import Token, TokenType
from unidecode import unidecode
from ufal.udpipe import Model, Sentence
import subprocess


class TokenPreprocessor(ABC):
    def preprocess(self, token: Token, document: str) -> Token:
        return token

    def preprocess_all(self, tokens: list[Token], document: str) -> list[Token]:
        return self.filter_tokens([self.preprocess(token, document) for token in tokens])

    def filter_tokens(self, tokens: list[Token]) -> list[Token]:
        return tokens


class LowercasePreprocessor(TokenPreprocessor):
    def preprocess(self, token: Token, document: str) -> Token:
        token.processed_form = token.processed_form.lower()
        return token


class UnicodePreprocessor(TokenPreprocessor):
    def preprocess(self, token: Token, document: str) -> Token:
        token.processed_form = unidecode(token.processed_form)
        return token


class StopWordsPreprocessor(TokenPreprocessor):
    def __init__(self, flags: set[str]):
        self.stop_words: set[str] = set()

        if "-cz" in flags:
            with open('stopwords/stopwords-cs.txt', 'r', encoding='utf-8') as f:
                self.stop_words.update(word.strip() for word in f.readlines())

        if "-sk" in flags:
            with open('stopwords/stopwords-sk.txt', 'r', encoding='utf-8') as f:
                self.stop_words.update(word.strip() for word in f.readlines())

        if "-en" in flags:
            with open('stopwords/stopwords-en.txt', 'r', encoding='utf-8') as f:
                self.stop_words.update(word.strip() for word in f.readlines())

    def preprocess(self, token: Token, document: str) -> Token:
        if token.processed_form in self.stop_words:
            token.token_type = TokenType.STOP_W
        return token

    def filter_tokens(self, tokens: list[Token]) -> list[Token]:
        return [token for token in tokens if token.token_type != TokenType.STOP_W]


class StemmerPreprocessor(TokenPreprocessor):
    def __init__(self, stemmer_path: str, args: str):
        self.stemmer_path = stemmer_path
        self.args = args.split()

    def preprocess_all(self, tokens: list[Token], document: str) -> list[Token]:
        input_data = "\n".join([token.processed_form for token in tokens]) + "\n"

        process = subprocess.Popen(
            [self.stemmer_path] + self.args,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        stdout, stderr = process.communicate(input=input_data)

        if process.returncode != 0:
            raise RuntimeError(f"Stemmer failed: {stderr}")

        stemmed_words = stdout.splitlines()
        stemmed_tokens = []
        for original_token, stemmed_word in zip(tokens, stemmed_words):
            new_token = Token(processed_form=stemmed_word,
                              position=original_token.position,
                              length=len(stemmed_word),
                              token_type=original_token.token_type)
            stemmed_tokens.append(new_token)

        return stemmed_tokens


class LemmatizerPreprocessor(TokenPreprocessor):
    def __init__(self, model_path: str):
        self.model = Model.load(model_path)
        if not self.model:
            raise FileNotFoundError(f"Model {model_path} not found")

        self.reusable_sentence = Sentence()

    def preprocess(self, token: Token, document: str) -> Token:
        if not token.processed_form:
            return token

        self.reusable_sentence.clear()
        word = self.reusable_sentence.addWord(token.processed_form)
        self.model.tag(self.reusable_sentence, Model.DEFAULT)
        token.processed_form = word.lemma

        return token


class PunctuationPreprocessor(TokenPreprocessor):
    def filter_tokens(self, tokens: list[Token]) -> list[Token]:
        return [token for token in tokens if token.token_type != TokenType.PUNCT]


class HTMLTagPreprocessor(TokenPreprocessor):
    def filter_tokens(self, tokens: list[Token]) -> list[Token]:
        return [token for token in tokens if token.token_type != TokenType.TAG]


class PreprocessingPipeline:
    def __init__(self, preprocessors: list[TokenPreprocessor]):
        self.preprocessors = preprocessors

    def preprocess(self, tokens: list[Token], document: str) -> list[Token]:
        for preprocessor in self.preprocessors:
            tokens = preprocessor.preprocess_all(tokens, document)
        return tokens
