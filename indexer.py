import math
import os
import json

from tqdm import tqdm
from documents_manager import Document
from eval.interface import SearchEngine


class Entry:
    def __init__(self, doc_id: str, tf: int):
        self.doc_id = doc_id
        self.tf = tf


class Indexer(SearchEngine):
    def __init__(self):
        self.inverted_index = None
        self.indexed_documents = None
        self.documents = None
        self.index_name = ""

    def index_documents(self, documents: list[Document]) -> None:
        self.documents = documents
        self.inverted_index: dict[str, list[Entry]] = {}
        self.indexed_documents: dict[str, dict[str, float]] = {}

        for doc in tqdm(documents, desc="\033[92mIndexing documents"):
            term_freq = {}

            for token in doc.tokens:
                term = token.processed_form
                term_freq[term] = term_freq.get(term, 0) + 1

            self.indexed_documents[doc.doc_id] = {}
            for term, tf in term_freq.items():
                if term not in self.inverted_index:
                    self.inverted_index[term] = []
                self.inverted_index[term].append(Entry(doc.doc_id, tf))
                self.indexed_documents[doc.doc_id][term] = 1 + math.log10(tf)

        self.normalize_doc_weight()

    def add_to_index(self, documents: list[Document]):
        for doc in tqdm(documents, desc="\033[92mAdding documents"):
            term_freq = {}

            for token in doc.tokens:
                term = token.processed_form
                term_freq[term] = term_freq.get(term, 0) + 1

            self.indexed_documents[doc.doc_id] = {}
            for term, tf in term_freq.items():
                if term not in self.inverted_index:
                    self.inverted_index[term] = []
                self.inverted_index[term].append(Entry(doc.doc_id, tf))
                self.indexed_documents[doc.doc_id][term] = 1 + math.log10(tf)

        self.normalize_doc_weight()

    def normalize_doc_weight(self):
        for doc_terms in self.indexed_documents.values():
            norm = sum(weight ** 2 for weight in doc_terms.values()) ** 0.5
            if norm == 0:
                continue
            for term, weight in doc_terms.items():
                doc_terms[term] /= norm

    def search(self, query: Document) -> list[tuple[str, float]]:
        query_weights = self.get_query_weight(query)
        relevant_documents: dict[str, dict[str, float]] = {}
        # find all relevant documents that contains words from query
        for key in query_weights:
            for entry in self.inverted_index[key]:
                if entry.doc_id not in relevant_documents:
                    relevant_documents[entry.doc_id] = self.indexed_documents[entry.doc_id]

        doc_scores: dict[str, float] = {}

        # basically scalar product
        for doc_id, doc_terms in relevant_documents.items():
            score = sum(query_weights.get(term, 0) * doc_terms.get(term, 0) for term in query_weights)
            doc_scores[doc_id] = score

        return sorted(doc_scores.items(), key=lambda item: item[1], reverse=True)

    def get_query_weight(self, query: Document):
        query_dict: dict[str, float] = {}
        # calculate tf_raw (no need to calculate words that are not indexed)
        for token in query.tokens:
            if token.processed_form in self.inverted_index:
                if token.processed_form in query_dict:
                    query_dict[token.processed_form] += 1
                else:
                    query_dict[token.processed_form] = 1

        for key in query_dict:
            # add weight tf_weight
            tf_weight = 1 + math.log10(query_dict[key])
            # calculate idf
            idf = math.log10(len(self.indexed_documents) / len(self.inverted_index[key]))
            # calculate final weight
            query_dict[key] = tf_weight * idf

        return query_dict

    def save_index(self, path: str) -> bool:
        try:
            total_entries = sum(len(entries) for entries in self.inverted_index.values())
            progress = tqdm(total=total_entries, desc="\033[92mSerializing inverted index")

            inverted_index_serialized = {}
            for term, entries in self.inverted_index.items():
                serialized_entries = []
                for entry in entries:
                    serialized_entries.append({"doc_id": entry.doc_id, "tf": entry.tf})
                    progress.update(1)
                inverted_index_serialized[term] = serialized_entries

            progress.close()

            index_data = {
                "inverted_index": inverted_index_serialized,
                "indexed_documents": self.indexed_documents,
                "index_name": self.index_name
            }

            print("\033[92mSaving index into JSON file")
            with open(path + ".json", "w", encoding="utf-8") as f:
                json.dump(index_data, f, ensure_ascii=False, indent=2)

            print("\033[92mSaving documents into JSON file")
            with open(path + "-doc.json", "w", encoding="utf-8") as f_docs:
                json.dump([doc.to_dict() for doc in self.documents], f_docs, ensure_ascii=False, indent=2)

            return True

        except (TypeError, OSError) as e:
            print(e)
            return False

    def load_index(self, path: str, load_doc: bool = False) -> bool:
        if not os.path.exists(path + ".json"):
            return False

        try:
            print("\033[92mOpening index file")
            with open(path + ".json", "r", encoding="utf-8") as f:
                data = json.load(f)

            self.inverted_index = {}
            for term, entries in tqdm(data["inverted_index"].items(), desc="\033[92mLoading inverted index"):
                self.inverted_index[term] = [Entry(entry["doc_id"], entry["tf"]) for entry in entries]

            self.indexed_documents = data["indexed_documents"]
            self.index_name = data.get("index_name", "")

            if load_doc:
                print("\033[92mOpening documents JSON file")
                with open(path + "-doc.json", "r", encoding="utf-8") as f_docs:
                    self.documents = [Document.from_dict(d) for d in json.load(f_docs)]

            return True

        except (json.JSONDecodeError, KeyError, OSError):
            return False

    def boolean_search(self, query: str) -> set[str]:
        pass
