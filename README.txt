
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





