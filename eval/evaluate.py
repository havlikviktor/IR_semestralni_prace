import json
import os
from datetime import datetime
from timeit import timeit

from documents_manager import *
from indexer import Indexer
from boolean_parser import BooleanParser, Node

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
    tokenizer: Tokenizer = RegexMatchTokenizer()

    with open(results_file, "w") as f:
        for query in tqdm(queries, desc="\033[92mEvaluating ranked queries"):
            query_doc: Document = Document(query["description"], "query").tokenize(tokenizer)
            preprocess_document(query_doc, flags)
            results = search_engine.search(query_doc)
            for i, (doc_id, score) in enumerate(results):
                f.write(f"{query['id']} Q0 {doc_id} {i + 1} {score} runindex1\n")
                if score < 0.05:
                    break

    run_trec_eval(f'eval_data_{language}/gold_relevancies.txt', results_file)


def evaluate_boolean(search_engine, queries):
    tokenizer: Tokenizer = BooleanMatchTokenizer()
    Node.initialize_docs(search_engine.inverted_index)

    for query_id, query in tqdm(enumerate(queries), desc="\033[92mEvaluating boolean queries"):
        query_doc: Document = Document(query, "query").tokenize(tokenizer)
        preprocess_document_boolean(query_doc, flags)
        parser = BooleanParser(query_doc.tokens)
        ast = parser.parse()
        ast.simplify()
        results = ast.evaluate(search_engine.inverted_index)
        assert len(results) > 0
        # print(len(results))


if __name__ == '__main__':
    language = 'cs'
    flags: set = {"-test", "-cz", "-l:cz"}

    ranked_queries = load_data_json(f'eval_data_{language}/full_text_queries.json')
    boolean_queries = load_queries(f'eval_data_{language}/boolean_queries_standard_100.txt')
    boolean_queries_10 = load_queries(f'eval_data_{language}/boolean_queries_standard_10.txt')

    indexer = Indexer()
    indexer.load_index("../cs_l")
    # print(f"Ranked evaluation took {timeit(lambda: evaluate_ranked(indexer, ranked_queries, language), number=1)} seconds.")
    # print(f"Boolean evaluation took {timeit(lambda: evaluate_boolean(indexer, boolean_queries), number=1)} seconds.")
    print(f"Boolean evaluation took {timeit(lambda: evaluate_boolean(indexer, boolean_queries_10), number=1)} seconds.")
