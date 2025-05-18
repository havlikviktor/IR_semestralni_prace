import os
from boolean_parser import BooleanParser, Node
from documents_manager import *
from indexer import Indexer
from colorama import Fore, init, Style
from prompt_toolkit import PromptSession
from Completer import DynamicCompleter


# ############################# USER HELPERS #########################################

def show_help():
    help_text = """
    Usage:

    1) index [flags] <path>
       Create new index from a JSON file at the given path.
       Used flags:
           -cz     Filter Czech stopwords
           -en     Filter English stopwords
           -sk     Filter Slovak stopwords
           -l:<language> Use lemmatization in preprocessing
           -s:<language> Use stemming in preprocessing
        Example: index -cz -l:cz myData

    2) q $query words$
       Query the created index. The query must be surrounded by '$' symbols.
       Example: q $cancer treatment$

    3) bq $boolean query$
       Perform a boolean query using AND, OR, NOT operators.
       The query must be surrounded by '$' symbols.
       Example: bq $cancer AND treatment$

    4) top <number>
       Set how many of the most relevant results should be shown for queries.
       Example: top 10

    5) add <path>
       Add additional documents from a JSON file at the given path to the existing index.

    6) save <filename>
       Save the current index to the given filename.

    7) load <filename>
       Load an existing index from the given filename.

    8) help
       Show this help message.

    9) exit
       Exit the program.
    """
    print(help_text.strip())


# ########################## HANDLE FUNCTIONS ##########################################


def handle_user_index(user_input: list[str]) -> tuple[Indexer, set[str]]:
    path = user_input[-1] + ".json"
    flags = set(user_input[1:])

    documents: list[Document] = load_documents(path, flags)
    preprocess_documents(documents, flags)
    indexer = Indexer()
    indexer.index_documents(documents)

    if indexer.inverted_index:
        Node.initialize_docs(indexer.inverted_index)
        completer.set_key_words(indexer.inverted_index.keys())
        indexer.index_name = os.path.splitext(os.path.basename(path))[0]

    return indexer, flags


def handle_user_query(indexer: Indexer, query: str, top_finds: int, flags: set[str]):
    if not indexer or not indexer.indexed_documents:
        print(f"{indexer.index_name}> " + Fore.RED + "Not existing index. run index <path> to initialize it")
        return

    tokenizer: Tokenizer = RegexMatchTokenizer()
    query: Document = Document(query, "query").tokenize(tokenizer)
    preprocess_document(query, flags)
    relevant: list[tuple[str, float]] = indexer.search(query)

    print(f"query='{query.text}' found={len(relevant)} listing top {top_finds}:")
    show_query_results(relevant, indexer.documents, top_finds, query.tokens)


def show_query_results(relevant: list[tuple[str, float]], documents: list[Document], top_finds: int,
                       query_tokens: list[Token]) -> None:
    query_terms = {t.processed_form for t in query_tokens}
    for i in range(min(len(relevant), top_finds)):
        doc_id, weight = relevant[i]
        doc = documents[int(doc_id[1:]) - 1]
        text = doc.text
        highlighted = ""

        last_pos = 0
        for token in sorted(doc.tokens, key=lambda t: t.position):
            highlighted += text[last_pos:token.position]

            word = text[token.position:token.position + token.length]
            if token.processed_form in query_terms:
                highlighted += Fore.LIGHTGREEN_EX + word + Style.RESET_ALL
            else:
                highlighted += word
            last_pos = token.position + token.length

        highlighted += text[last_pos:]

        print(f"doc_id[{doc_id}] w:[{round(weight, 3)}]: {highlighted}")


def handle_user_boolean_query(indexer: Indexer, query: str, flags: set[str]):
    if not indexer or not indexer.indexed_documents:
        print(f"{indexer.index_name}> " + Fore.RED + "Not existing index. run index <path> to initialize it")
        return

    tokenizer: Tokenizer = BooleanMatchTokenizer()
    query_doc: Document = Document(query, "query").tokenize(tokenizer)
    preprocess_document_boolean(query_doc, flags)
    parser = BooleanParser(query_doc.tokens)
    ast = parser.parse()
    ast.simplify()
    results = ast.evaluate(indexer.inverted_index)

    print(f"relevant docs for {query_doc.text}")
    for r in results:
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
        print(f"{indexer.index_name}> " + Fore.LIGHTGREEN_EX + "Index saved")
    else:
        print(f"{indexer.index_name}> " + Fore.RED + "Couldn't save index")


def handle_user_load(path: str) -> Indexer:
    indexer = Indexer()
    if indexer.load_index(path, True):
        Node.initialize_docs(indexer.inverted_index)
        completer.set_key_words(indexer.inverted_index.keys())
        print(f"{indexer.index_name}> " + Fore.LIGHTGREEN_EX + f"Index '{indexer.index_name}' loaded")
        return indexer
    else:
        print(f"{indexer.index_name}> " + Fore.RED + "Couldn't load index")
        return indexer


def main():
    indexer: Indexer = Indexer()
    top_finds: int = 3
    flags: set[str] = set()

    while True:
        user_input_raw: str = session.prompt(f"{indexer.index_name}> ").rstrip()
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

        elif user_input[0] == "add":
            if input_len != 2:
                print(f"{indexer.index_name}> " + Fore.RED + f"Invalid number of arguments expected 2 got {input_len}")
            else:
                handle_user_add(indexer, user_input[1], flags)

        elif user_input[0] == "help":
            show_help()

        else:
            print(f"{indexer.index_name}> " + Fore.RED + f"Unknown command")


if __name__ == '__main__':
    init(autoreset=True)
    completer = DynamicCompleter()
    session = PromptSession(completer=completer)
    print("> Indexer started, run help for details")
    main()
