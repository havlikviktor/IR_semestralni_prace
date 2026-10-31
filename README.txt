
################################################ INICIALIZACE ########################################################

před prvním spuštěním programu je třeba
	1)  pustit script build.bat, který zajistí: a) stažení udPipe modelu pro lematizaci
							b) stažení stopWords pro dostupné jazyky

	2) stáhnout soubor games.json z níže přiložené adresy a uložit je do kořenového adresáře projektu.

	3) zkontrolovat závislosti projektu v souboru requirements.txt, který se nachází v kořenovém adresáři projektu
	   případně je instalovat příkazem: pip install -r requirements.txt

* URL pro stažení dat: https://drive.google.com/file/d/1y8BIdKfq1bQveitXxSqSKuhWE_V4STW3/view?usp=drive_link
* Pro správnou funkčnosti build.bat scriptu je třeba mít na počítači dostupný curl

################################################## SPUŠTĚNÍ ###########################################################

Samotný program spustíte bez parametrů pomocí příkazu:  py .\main.py
Pro nápovědu na práci s programem využijte příkaz: help


################################################# EVALUACE ############################################################

		________________________________________________________________________________________________________________________________
		| data         | preprocessing | doba indexace | čas queries.json |   MAP  | čas bool_queries_100.txt | čas bool_queries_10.txt|
		‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾
		| eval_data_cs | lemmatizace   |     16 min    |         2:39     | 0.164  |           06:45          |		  05:15        |
		--------------------------------------------------------------------------------------------------------------------------------	
		| eval_data_cs | stemming      |     41 min    |         0:05     | 0.120  |           01:41          |           00:11        |
		--------------------------------------------------------------------------------------------------------------------------------	
		| eval_data_en | lemmatizace   |     22 sec    |         1:37     | 0.561  |	       01:42          |           01:37        |
		--------------------------------------------------------------------------------------------------------------------------------
		| eval_data_en | stemming      |     19 sec    |         0:03     | 0.542  |	       00:03          |           00:02        |	
		‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾

########################################## NADSTANDARTNÍ FUNKČNOST ############################################################	

	✅ File-based index
	✅ pozdější doindexování dat
	✅ ošetření HTML tagů
	✅ vylepšení vyhledávání (redukce AST u boolean search podle zákona o dvojité negaci + omezeni AND)
	✅ další předzpracování normalizace (lemmatizace / stemming)
	✅ napovídání keywords
	✅ zvýraznění hledaného textu v náhledu výsledků
	✅ vlastní implementace parsování dotazů bez použití externí knihovny
	✅ podpora více jazyků


########################################## boolean_parser.py ################################################################## 
Obsahuje třídy pro zpracování a vyhodnocení booleovských dotazů:

Node: Abstraktní třída pro uzly AST, definuje evaluate a simplify.
TermNode, NotNode, AndNode, OrNode: Uzly AST reprezentující termín, negaci, konjunkci a disjunkci. Každý má metodu evaluate pro vyhodnocení dotazu nad invertovaným indexem.
BooleanParser: Parser, který převádí tokenizovaný booleovský dotaz do AST (parse, parse_expr, parse_term, parse_factor, parse_base).

########################################## Completer.py #########################################################################
Obsahuje třídu pro doplňování příkazů v konzoli:


DynamicCompleter: Dědí z Completer. Hlavní metody:

get_completions: Generuje návrhy pro doplňování podle aktuálního vstupu uživatele.
suggest_all: Navrhne všechny možné klíčová slova nebo příkazy.
suggest_pattern: Navrhne pouze ty klíčová slova, která odpovídají zadanému vzoru.
set_key_words: Nastaví množinu klíčových slov, která se mají nabízet.

Nápověda se přizpůsobuje podle aktuálního kontextu vstupu a podle něj vybírá vhodné nápovědy.

########################################## tokenizer.py #########################################################################
Tokenizace dotazů a dokumentů:

Tokenizer: Abstraktní třída pro tokenizaci textu.
RegexMatchTokenizer: Tokenizuje text na základě regulárních výrazů, vhodné pro běžné dotazy.
BooleanMatchTokenizer: Tokenizuje text pro booleovské dotazy, rozpoznává operátory AND, OR, NOT, závorky a termy.
Token: Reprezentuje jeden token (slovo, operátor, atd.) s informací o pozici, délce a typu.
TokenType: Enum typy tokenů (slovo, operátor, závorka, stop slovo, atd.).

########################################## documents_manager.py #################################################################
Správa dokumentů a jejich předzpracování:


Document: Reprezentuje dokument, obsahuje text, id a tokeny. Hlavní metody:

tokenize: Provede tokenizaci textu dokumentu pomocí zvoleného tokenizéru.
preprocess: Aplikuje předzpracovací pipeline na tokeny dokumentu.
to_dict/from_dict: Serializace a deserializace dokumentu do/ze slovníku.

Funkce:
load_documents: Načte dokumenty ze souboru a provede jejich tokenizaci.
preprocess_document/preprocess_document_boolean: Předzpracuje jeden dokument podle zvolených příznaků (včetně boolean varianty).
preprocess_documents: Hromadně předzpracuje seznam dokumentů.
get_pipe/get_boolean_pipe: Sestaví pipeline předzpracování podle příznaků (lemmatizace, stemming, stopwords atd.).
build_dictionary: Vytvoří slovník všech termů v dokumentech.

########################################## indexer.py ###########################################################################
Indexace a vyhledávání:

Entry: Pomocná třída pro položku v invertovaném indexu (doc_id, tf).
Indexer: Dědí ze SearchEngine. Spravuje invertovaný index, indexované dokumenty a jejich váhy. Hlavní metody:

index_documents: Vytvoří invertovaný index a vypočítá váhy dokumentů z předaného seznamu dokumentů.
add_to_index: Přidá nové dokumenty do již existujícího indexu a aktualizuje váhy.
normalize_doc_weight: Normalizuje váhy termů v dokumentech pro lepší porovnání.
search: Provede vektorové vyhledávání na základě dotazu a vrátí seřazené výsledky podle relevance.
boolean_search: Provede booleovské vyhledávání (AND, OR, NOT) nad indexem a vrátí odpovídající dokumenty.
save_index: Uloží aktuální index a dokumenty do souboru.
load_index: Načte index a dokumenty ze souboru.

########################################## preprocess.py ########################################################################
Předzpracování tokenů:

TokenPreprocessor: Abstraktní třída pro preprocesory tokenů.
LowercasePreprocessor: UnicodePreprocessor: Převod na malá písmena, odstranění diakritiky.
StopWordsPreprocessor: Odstraňuje stop slova podle jazykových příznaků.
StemmerPreprocessor: Volá externí stemmer pro stemming.
LemmatizerPreprocessor: Lemmatizace pomocí modelu UDPipe.
PunctuationPreprocessor: HTMLTagPreprocessor: Odstraňují interpunkci a HTML tagy.
PreprocessingPipeline: Řetězí více preprocesorů a aplikuje je na tokeny.

