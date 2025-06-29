"""
main.py: třetí projekt

author: Jana Zamachajeva
email: janazamachajeva@seznam.cz

Komentar autorky:
* Promenne a komentare jsou uvedeny v cestine

"""

import argparse
import requests
from bs4 import BeautifulSoup
import csv

oddelovac = "-"*50

# vyparsuji obsah webu volby.cz
def nacti_obsah_stranky(url: str):
    odpoved = requests.get(url)
    if odpoved.status_code == 200:
        rozdelene = BeautifulSoup(odpoved.text, features="html.parser")
        return rozdelene
    else:
        print("Chyba při načítání stránky")
        return None

# vytvorim seznam cisel obci
def vytvor_seznam_cisel_obci(obsah_stranky) -> list:
    cisla_obci_list = list()
    for cislo_obce in obsah_stranky.find_all("td", {"class": "cislo"}):
        cisla_obci_list.append(cislo_obce.text.strip())
    return cisla_obci_list

# vytvorim seznam nazvu obci
def vytvor_seznam_nazvu_obci(obsah_stranky) -> list:
    nazvy_obci_list = list()
    for nazev_obce in obsah_stranky.find_all("td", {"class": "overflow_name"}):
        nazvy_obci_list.append(nazev_obce.text.strip())
    return nazvy_obci_list

# vytvorim odkaz pomoci cisla obce
def naformatuj_odkaz(cislo_obce: int) -> str:
    return f"https://www.volby.cz/pls/ps2017nss/ps311?xjazyk=CZ&xkraj=2&xobec={cislo_obce}&xvyber=2106"

print(oddelovac)
 
def main(url, nazev_souboru):
    rozdelene = nacti_obsah_stranky(url)
    print("Stahuji data pro Mělník")
    seznam_cisel_obci = vytvor_seznam_cisel_obci(rozdelene) # sloupec 1 
    seznam_nazvu_obci = vytvor_seznam_nazvu_obci(rozdelene) # sloupec 2
    
    # vytvorim odkazy pro jednotlive obce a zbytek seznamu
    volici_v_seznamu = list()
    vydane_obalky = list()
    platne_hlasy = list()

    # vytvorim seznam kandidujicich stran a promenne pro zbyle sloupce (6 =<)
    seznam_stran = list()
    data_stran = dict()

    # promenna pro vytvoreni seznamu stran a pripravu prazdnych seznamu 
    # hlasu (hodnot v seznamu)
    prvni_obec = True

    # prochazim odkazy na jednotlive obce
    for cislo in seznam_cisel_obci:
        odkaz = naformatuj_odkaz(cislo)
        obsah_stranky_obec = nacti_obsah_stranky(odkaz)

        volic = obsah_stranky_obec.find("td", {"headers":"sa2"})
        obalka = obsah_stranky_obec.find("td", {"headers":"sa3"})
        hlas = obsah_stranky_obec.find("td", {"headers":"sa6"})
        
        volici_v_seznamu.append(volic.text.strip()) # sloupec 3
        vydane_obalky.append(obalka.text.strip()) # sloupec 4
        platne_hlasy.append(hlas.text.strip()) # sloupec 5

        # pripravim slovnik data_stran (klice budou tvorit jednotlive strany 
        # a hodnoty - seznamy hlasu pro tyto strany)
        if prvni_obec:
            for strana_raw in obsah_stranky_obec.find_all(
                "td", {"class": "overflow_name"}):
                strana = strana_raw.text.strip()
                seznam_stran.append(strana)
                data_stran[strana] = []
            prvni_obec = False
 
        x = 0 # prepinac mezi stranami

        # zaplnim prazdne seznamy hlasu
        for pocet_hlasu in obsah_stranky_obec.find_all("td", 
                                                {"headers":"t1sa2 t1sb3"}):
            (data_stran[seznam_stran[x]]).append(pocet_hlasu.text.strip())
            x += 1
        for pocet_hlasu in obsah_stranky_obec.find_all("td", 
                                                {"headers":"t2sa2 t2sb3"}):
            (data_stran[seznam_stran[x]]).append(pocet_hlasu.text.strip())
            x += 1

    # vytvorim hlavicku
    hlavicka = [
                "Číslo obce", 
                "Název obce", 
                "Voliči v seznamu", 
                "Vydané obálky", 
                "Platné hlasy"
                ]
    hlavicka.extend(seznam_stran)
    
    # vytvorim vysledny CSV soubor
    with open(nazev_souboru, mode="w",
              encoding="utf-8-sig", newline="") as vysledky:
        print(f"Ukládám do souboru: {nazev_souboru}")
        zapisovac = csv.DictWriter(vysledky, fieldnames=hlavicka)
        zapisovac.writeheader()
        for radek in range(len(seznam_cisel_obci)):
            radek_dict = {
                    "Číslo obce": seznam_cisel_obci[radek], 
                    "Název obce": seznam_nazvu_obci[radek],
                    "Voliči v seznamu": volici_v_seznamu[radek],
                    "Vydané obálky": vydane_obalky[radek],
                    "Platné hlasy": platne_hlasy[radek],
                    }
            for strana in seznam_stran:
                radek_dict[strana] = data_stran[strana][radek]
            zapisovac.writerow(radek_dict)
    print(f"Ukončuji zápis do {nazev_souboru}")

if __name__ == "__main__":

    #uzivatel zada odkaz a nazev vysledneho souboru jako argumenty
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "url", 
        help="Odkaz na stránku s výsledky pro Mělník: https://www.volby.cz/pls/ps2017nss/ps32?xjazyk=CZ&xkraj=2&xnumnuts=2106")
    parser.add_argument("vystupny_soubor", help="Název výstupního CSV souboru")
    args = parser.parse_args()

    main(args.url, args.vystupny_soubor)
