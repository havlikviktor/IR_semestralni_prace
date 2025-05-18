@echo off
IF NOT EXIST .\stopwords (
    mkdir stopwords
    curl  -k -o .\stopwords\stopwords-cs.txt https://raw.githubusercontent.com/stopwords-iso/stopwords-cs/master/stopwords-cs.txt
    curl  -k -o .\stopwords\stopwords-sk.txt https://raw.githubusercontent.com/stopwords-iso/stopwords-sk/master/stopwords-sk.txt
    curl  -k -o .\stopwords\stopwords-en.txt https://raw.githubusercontent.com/stopwords-iso/stopwords-en/master/stopwords-en.txt
)

IF NOT EXIST .\model_cz.udpipe (
    curl -k https://lindat.mff.cuni.cz/repository/xmlui/bitstream/handle/11234/1-3131/czech-pdt-ud-2.5-191206.udpipe -o model_cz.udpipe
)

IF NOT EXIST .\model_en.udpipe (
    curl -k https://lindat.mff.cuni.cz/repository/xmlui/bitstream/handle/11234/1-3131/english-ewt-ud-2.5-191206.udpipe -o model_en.udpipe
)