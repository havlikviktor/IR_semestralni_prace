import json
from typing import Iterable
from tokenizer import Tokenizer, RegexMatchTokenizer, BooleanMatchTokenizer
from preprocess import *
from collections import Counter
from tqdm import tqdm


class Document:
    def __init__(self, text: str, doc_id: str):
        self.text = text
        self.tokens = None
        self.doc_id = doc_id

    def tokenize(self, tokenizer: Tokenizer):
        self.tokens = tokenizer.tokenize(self.text)
        return self

    def preprocess(self, preprocessing_pipeline: PreprocessingPipeline):
        self.tokens = preprocessing_pipeline.preprocess(self.tokens, self.text)
        return self

    def to_dict(self):
        return {
            "text": self.text,
            "doc_id": self.doc_id,
            "tokens": [token.to_dict() for token in self.tokens] if self.tokens else None
        }

    @staticmethod
    def from_dict(data):
        doc = Document(text=data["text"], doc_id=data["doc_id"])
        if data.get("tokens") is not None:
            doc.tokens = [Token.from_dict(t) for t in data["tokens"]]
        return doc


def build_dictionary(documents: Iterable[Document]):
    vocab = Counter()
    for doc in documents:
        vocab.update((token.processed_form for token in doc.tokens))
    return vocab


def print_weighted_dictionary(dictionary: [Document]):
    for key, value in sorted(dictionary.items(), key=lambda x: x[1], reverse=True):
        print(f"{key} {value}")


def load_documents(source_file: str, flags: set[str]) -> [Document]:
    documents = []

    with open(source_file, 'r', encoding="utf-8") as f:
        data = json.load(f)
        tokenizer = RegexMatchTokenizer()
        if "-test" in flags:
            for doc in tqdm(data, desc="\033[92mLoading documents from file"):
                title = doc.get("title", "") or ""
                text = doc.get("text", "") or ""
                doc_id = doc.get("id", "invalid_ID")
                documents.append(Document(title + text, doc_id).tokenize(tokenizer))
        else:
            doc_id = 1
            for game in tqdm(data, desc="\033[92mLoading documents from file"):
                for e in game.get("easter_eggs", []):
                    documents.append(Document(e, "d" + str(doc_id)).tokenize(tokenizer))
                    doc_id += 1

    return documents


def preprocess_document(document: Document, flags: set[str]) -> Document:
    pipeline = get_pipe(flags)
    return document.preprocess(pipeline)


def preprocess_document_boolean(document: Document, flags: set[str]) -> Document:
    pipeline = get_boolean_pipe(flags)
    return document.preprocess(pipeline)


def preprocess_documents(documents: list[Document], flags: set[str]):
    pipeline = get_pipe(flags)
    for doc in tqdm(documents, desc="\033[92mPreprocessing documents"):
        doc.preprocess(pipeline)


def get_pipe(flags: set[str]):
    pipeline = [
        HTMLTagPreprocessor(),
        LowercasePreprocessor(),
        PunctuationPreprocessor(),
        StopWordsPreprocessor(flags),
        UnicodePreprocessor()
    ]

    if "-l:cz" in flags:
        pipeline.insert(4, LemmatizerPreprocessor('model_cz.udpipe'))

    if "-l:en" in flags:
        pipeline.insert(4, LemmatizerPreprocessor('model_en.udpipe'))

    if "-s:cz" in flags:
        pipeline.append(StemmerPreprocessor(r"stemmer.exe", ""))

    if "-s:en" in flags:
        pipeline.append(StemmerPreprocessor(r"stemmer.exe", "-l en"))

    return PreprocessingPipeline(pipeline)


def get_boolean_pipe(flags: set[str]) -> PreprocessingPipeline:
    pipeline = [
        LowercasePreprocessor(),
        UnicodePreprocessor()
    ]

    if "-l:cz" in flags:
        pipeline.insert(1, LemmatizerPreprocessor('model_cz.udpipe'))

    if "-l:en" in flags:
        pipeline.insert(1, LemmatizerPreprocessor('model_en.udpipe'))

    if "-s:cz" in flags:
        pipeline.append(StemmerPreprocessor(r"stemmer.exe", ""))

    if "-s:en" in flags:
        pipeline.append(StemmerPreprocessor(r"stemmer.exe", "-l en"))

    return PreprocessingPipeline(pipeline)
