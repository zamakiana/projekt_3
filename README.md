# Projekt 3

Cilem tohoto projektu je vytvoreni skriptu, ktery slouzi k extrahovani vysledku parlamentnich voleb v roce 2017 pro všechny obce s vyjímkou yahraničí. Repozitar obsahuje samotny program **main.py**, seznam nainstalovanych knihoven **requirements.txt**, vysledny soubor, ktery se vygeneruje po spusteni skriptu **vysledky_melnik.csv** a tento **README** soubor.

## Instalace knihoven

Instalace knihoven probehla ve virtualnim prostredi, vysledny seznam instalovanych knihoven je uveden v souboru requirements.txt.

## Spusteni skriptu

Spusteni skriptu v prikazovem radku vyzaduje 2 povinne argumenty: odkaz na volebni vysledky a nazev vysledneho souboru.
```
python main.py "https://www.volby.cz/pls/ps2017nss/ps32?xjazyk=CZ&xkraj=2&xnumnuts=2106" "vysledky_melnik.csv"
```

Prubeh stahovani:
```
--------------------------------------------------
Stahuji data pro okres Mělník v kraji Středočeský kraj
Ukládám do souboru vysledky_melnik.csv
Ukončuji zápis do vysledky_melnik.csv
```
Castecny vystup:
```
Číslo obce,Název obce,Voliči v seznamu,Vydané obálky,Platné hlasy,...
534714,Býkev,341,212,210,...
534722,Byšice,1 061,630,626,...
```
