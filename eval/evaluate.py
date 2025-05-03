import json
import os
from datetime import datetime
import subprocess
from timeit import timeit

from documents_manager import *
from indexer import Indexer


def load_queries(file_path):
    queries = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            query = line.strip()
            queries.append(query)
    return queries


def load_data_json(path):
    """
    Load documents from a json file
    :param path:
    :return:
    """
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def dump_data_json(data, path):
    """
    Dump data to a json file
    :param data:
    :param path:
    :return:
    """
    with open(path, 'w') as f:
        json.dump(data, f, indent=4)


def run_trec_eval(gold_file, results_file):
    p = subprocess.Popen(['trec_eval', '-m', 'all_trec', gold_file, results_file],
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()
    out = out.decode('utf-8')
    err = err.decode('utf-8')
    print(out)
    print(err)


def evaluate_ranked(search_engine, queries, language='en'):
    os.makedirs("output", exist_ok=True)
    results_file = f"output/ranked_results_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.txt"

    with open(results_file, "w") as f:
        for query in tqdm(queries, desc="\033[92mEvaluating ranked queries"):
            query_doc: Document = Document(query["description"], "query").tokenize()
            preprocess_document(query_doc, flags)
            results = search_engine.search(query_doc)
            for i, (doc_id, score) in enumerate(results):
                f.write(f"{query['id']} Q0 {doc_id} {i + 1} {score} runindex1\n")

    run_trec_eval(f'eval_data_{language}/gold_relevancies.txt', results_file)


def evaluate_boolean(search_engine, queries):
    for query_id, query in enumerate(queries):
        results = search_engine.boolean_search(query)
        assert len(results) > 0
        print(len(results))


if __name__ == '__main__':
    language = 'cs'
    flags: set = {"-test", "-cz", "-l"}
    # boolean_queries = load_queries(f'eval_data_{language}/boolean_queries_standard_100.txt')

    # documents: list[Document] = load_documents(f'eval_data_{language}/documents.json', flags)
    ranked_queries = load_data_json(f'eval_data_{language}/full_text_queries.json')
    # preprocess_documents(documents, flags)
    indexer = Indexer()
    # indexer.index_documents(documents)
    indexer.load_index("../saved_cs_stemm_title+text.pickle")
    print(f"Ranked evaluation took {timeit(lambda: evaluate_ranked(indexer, ranked_queries, language), number=1)} seconds.")
    # print(f"Boolean evaluation took {timeit(lambda: evaluate_boolean(indexer, boolean_queries), number=1)} seconds.")
