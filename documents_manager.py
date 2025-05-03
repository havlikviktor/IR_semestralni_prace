import json
from typing import Iterable
from tokenizer import RegexMatchTokenizer
from preprocess import *
from collections import Counter
from tqdm import tqdm


class Document:
    def __init__(self, text: str, doc_id: str):
        self.text = text
        self.tokens = None
        self.doc_id = doc_id

    def tokenize(self):
        tokenizer = RegexMatchTokenizer()
        self.tokens = tokenizer.tokenize(self.text)
        return self

    def preprocess(self, preprocessing_pipeline: PreprocessingPipeline):
        self.tokens = preprocessing_pipeline.preprocess(self.tokens, self.text)
        return self


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

        if "-test" in flags:
            for doc in tqdm(data, desc="\033[92mLoading documents from file"):
                title = doc.get("title", "") or ""
                text = doc.get("text", "") or ""
                doc_id = doc.get("id", "invalid_ID")
                documents.append(Document(title + text, doc_id).tokenize())
        else:
            doc_id = 1
            for game in tqdm(data, desc="Loading game documents"):
                for e in game.get("easter_eggs", []):
                    documents.append(Document(e, "d" + str(doc_id)).tokenize())
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

    if "-l" in flags:
        pipeline.insert(4, LemmatizerPreprocessor('model.udpipe'))
    if "-s" in flags:
        pipeline.append(StemmerPreprocessor(r"stemmer.exe"))

    return PreprocessingPipeline(pipeline)


def get_boolean_pipe(flags: set[str]) -> PreprocessingPipeline:
    pile: PreprocessingPipeline = get_pipe(flags)
    pile.preprocessors.pop(2)
    pile.preprocessors.pop(1)
    return pile

