import os
from boolean_parser import BooleanParser
from documents_manager import *
from indexer import Indexer
from colorama import Fore, init


def show_help():
    help_text = """
    Usage:
    1) index [flags] <path>
       Create new index from a JSON file at the given path.
       Used flags:
           -cz     Filter Czech stopwords
           -en     Filter English stopwords
           -sk     Filter Slovak stopwords
           -l      Use lemmatization in preprocessing
           -s      Use stemming in preprocessing
    2) q $query words$
       Query the created index. The query must be surrounded by '$' symbols.

    3) top X
       Set how many of the most relevant results should be shown for queries.

    4) exit
       Exit the program.
    """
    print(help_text.strip())


def handle_user_index(user_input: list[str]) -> tuple[Indexer, set[str]]:
    path = user_input[-1] + ".json"
    flags = set(user_input[1:])

    documents: list[Document] = load_documents(path, flags)
    preprocess_documents(documents, flags)
    indexer = Indexer()
    indexer.index_documents(documents)

    if indexer.documents:
        indexer.index_name = os.path.splitext(os.path.basename(path))[0]

    return indexer, flags


def handle_user_query(indexer: Indexer, query: str, top_finds: int, flags: set[str]):
    if not indexer or not indexer.indexed_documents:
        print(f"{indexer.index_name}> " + Fore.RED + "Not existing index. run index <path> to initialize it")
        return

    query: Document = Document(query, "query").tokenize()
    preprocess_document(query, flags)
    relevant = indexer.search(query)
    relevant = dict(sorted(relevant.items(), key=lambda x: x[1], reverse=True))

    print(f"query='{query.text}' found={len(relevant)} listing top {top_finds}:")
    for i in range(min(len(relevant), top_finds)):
        doc_id, weight = list(relevant.items())[i]
        print(f"doc_id[{doc_id}] w:[{round(weight, 3)}]: {indexer.documents[int(doc_id[1:])].text}")


def handle_user_boolean_query(indexer: Indexer, query: str, flags: set[str]):
    if not indexer or not indexer.indexed_documents:
        print(f"{indexer.index_name}> " + Fore.RED + "Not existing index. run index <path> to initialize it")
        return

    query: Document = Document(query, "query").tokenize()
    preprocess_document_boolean(query, flags)
    parser = BooleanParser(query)
    ast = parser.parse()

    result = ast.evaluate(indexer.inverted_index)

    print(f"relevant docs for {query.text}")
    for r in result:
        print(r)


def handle_user_add(indexer: Indexer, path: str, flags: set[str]):
    if not indexer or not indexer.indexed_documents:
        print(f"{indexer.index_name}> " + Fore.RED + "Not existing index. run index <path> to initialize it")
        return

    documents: list[Document] = load_documents(path, flags)
    preprocess_documents(documents, flags)
    indexer.add_to_index(documents)


def handle_user_save(indexer: Indexer, path: str):
    if not indexer or not indexer.indexed_documents:
        print(f"{indexer.index_name}> " + Fore.RED + "Not existing index. run index <path> to initialize it")
        return

    if not indexer.inverted_index:
        print(f"{indexer.index_name}> " + Fore.RED + "Couldn't save index")
    if indexer.save_index(path):
        print(f"{indexer.index_name}> " + Fore.GREEN + "Index saved")
    else:
        print(f"{indexer.index_name}> " + Fore.RED + "Couldn't save index")


def handle_user_load(path: str) -> Indexer:
    indexer = Indexer()
    if indexer.load_index(path):
        print(f"{indexer.index_name}> " + Fore.GREEN + f"Index '{indexer.index_name}' loaded")
        return indexer
    else:
        print(f"{indexer.index_name}> " + Fore.RED + "Couldn't load index")
        return indexer


def main():
    indexer: Indexer = Indexer()
    top_finds: int = 3
    flags: set[str] = set()

    while True:
        user_input_raw: str = input(f"{indexer.index_name}> ").rstrip()
        user_input: list[str] = user_input_raw.split()
        input_len: int = len(user_input)

        if input_len == 0:
            continue

        elif user_input[0] == "q":
            if len(user_input_raw.split("$")) != 3:
                print(
                    f"{indexer.index_name}> " + Fore.RED + f"Invalid number of arguments expected 2 got {len(user_input_raw.split('$'))}")
            else:
                handle_user_query(indexer, user_input_raw.split('$')[1], top_finds, flags)

        elif user_input[0] == "bq":
            if len(user_input_raw.split("$")) != 3:
                print(
                    f"{indexer.index_name}> " + Fore.RED + f"Invalid number of arguments expected 2 got {len(user_input_raw.split('$'))}")
            else:
                handle_user_boolean_query(indexer, user_input_raw.split('$')[1], flags)

        elif user_input[0] == "index":
            if input_len < 2:
                print(
                    f"{indexer.index_name}> " + Fore.RED + f"Invalid number of arguments expected at least 2 got {input_len}")
            else:
                indexer, flags = handle_user_index(user_input)

        elif user_input[0] == "exit":
            exit(0)

        elif user_input[0] == "top":
            if input_len != 2:
                print(f"{indexer.index_name}> " + Fore.RED + f"Invalid number of arguments expected 2 got {input_len}")
            else:
                try:
                    top_finds = int(user_input[1])
                except ValueError:
                    print(f"{indexer.index_name}> " + Fore.RED + f"Second argument must be a number")

        elif user_input[0] == "save":
            if input_len != 2:
                print(f"{indexer.index_name}> " + Fore.RED + f"Invalid number of arguments expected 2 got {input_len}")
            else:
                handle_user_save(indexer, user_input[1])

        elif user_input[0] == "load":
            if input_len != 2:
                print(f"{indexer.index_name}> " + Fore.RED + f"Invalid number of arguments expected 2 got {input_len}")
            else:
                indexer = handle_user_load(user_input[1])

        elif user_input[0] == "help":
            show_help()

        else:
            print(f"{indexer.index_name}> " + Fore.RED + f"Unknown command")


if __name__ == '__main__':
    init(autoreset=True)
    print("> Indexer started, run help for details")
    main()
