"""
main.py: třetí projekt

author: Jana Zamachajeva
email: janazamachajeva@seznam.cz

"""

import argparse
import requests
from bs4 import BeautifulSoup
import csv
from urllib.parse import urlparse, parse_qs
#import time

oddelovac = "-"*50

# vyparsuji obsah webu volby.cz
def nacti_obsah_stranky(url: str):
    headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115 Safari/537.36"
    }
    odpoved = requests.get(url, headers=headers, timeout=10)
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

# ze zadaneho url vytahnu parametry potrebne pro tvorbu odkazu na detail obce
def extrahuj_parametry(url: str) -> dict:
    parsed = urlparse(url)
    params = parse_qs(parsed.query)
    return {
            "xkraj": params.get("xkraj", [""])[0],
            "xvyber": params.get("xnumnuts", [""])[0]
            }

# vytvorim odkaz pomoci cisla obce a parametru ze zadaneho url
def naformatuj_odkaz(cislo_obce: int, parametry: dict) -> str:
    return (f"https://www.volby.cz/pls/ps2017nss/ps311?xjazyk=CZ&"
            f"xkraj={parametry['xkraj']}&"
            f"xobec={cislo_obce}&"
            f"xvyber={parametry['xvyber']}"
            )

print(oddelovac)
 
def main(url, nazev_souboru):
    rozdelene = nacti_obsah_stranky(url)

    seznam_cisel_obci = vytvor_seznam_cisel_obci(rozdelene) # sloupec 1 
    seznam_nazvu_obci = vytvor_seznam_nazvu_obci(rozdelene) # sloupec 2

    kraj = rozdelene.find("h3", string=lambda text: text and "Kraj" in text)
    okres = rozdelene.find("h3", string=lambda text: text and "Okres" in text)
    if okres:
        print(f"Stahuji data pro okres {okres.text.split(":")[-1].strip()} "
            f"v kraji {kraj.text.split(":")[-1].strip()}")
    else:
        print("Stahuji vysledky pro Prahu")
    
    # vytvorim odkazy pro jednotlive obce a zbytek seznamu
    volici_v_seznamu = list()
    vydane_obalky = list()
    platne_hlasy = list()

    # vytvorim seznam kandidujicich stran a promenne pro zbyle sloupce (6 =<)
    seznam_stran = list()
    data_stran = dict()

    prvni_obec = True # pomocna prommena pro vytvoreni hlavicky

    parametry = extrahuj_parametry(url)

    # prochazim odkazy na jednotlive obce
    for cislo in seznam_cisel_obci:
        odkaz = naformatuj_odkaz(cislo, parametry)
        obsah_stranky_obec = nacti_obsah_stranky(odkaz)
        #time.sleep(2)

        volic = obsah_stranky_obec.find("td", {"headers":"sa2"})
        obalka = obsah_stranky_obec.find("td", {"headers":"sa3"})
        hlas = obsah_stranky_obec.find("td", {"headers":"sa6"})
        
        volici_v_seznamu.append(volic.text.strip()) # sloupec 3
        vydane_obalky.append(obalka.text.strip()) # sloupec 4
        platne_hlasy.append(hlas.text.strip()) # sloupec 5

        # vytvorim hlavicku a pripravim slovnik data_stran 
        # (klice budou tvorit jednotlive strany 
        # a hodnoty - seznamy hlasu pro tyto strany)
        if prvni_obec:
            hlavicka = [
                        "Číslo obce", 
                        "Název obce", 
                        "Voliči v seznamu", 
                        "Vydané obálky", 
                        "Platné hlasy"
                        ]
            for strana_raw in obsah_stranky_obec.find_all(
                "td", {"class": "overflow_name"}):
                strana = strana_raw.text.strip()
                seznam_stran.append(strana)
                data_stran[strana] = []
            hlavicka.extend(seznam_stran)
            prvni_obec = False
 
        x = 0 # prepinac mezi stranami

        # zaplnim prazdne seznamy hlasu
        vsechny_hlasy = obsah_stranky_obec.find_all("td", {"headers": ["t1sa2 t1sb3", "t2sa2 t2sb3"]})
        for strana in seznam_stran:
            if x < len(vsechny_hlasy):
                data_stran[strana].append(vsechny_hlasy[x].text.strip())
            else:
                data_stran[strana].append("0")
            x += 1
    
    # vytvorim vysledny CSV soubor
    with open(nazev_souboru, mode="w",
              encoding="utf-8-sig", newline="") as vysledky:
        print(f"Ukládám do souboru {nazev_souboru}")
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
        help="Odkaz na stránku s výsledky pro okres, napr. https://www.volby.cz/pls/ps2017nss/ps32?xjazyk=CZ&xkraj=2&xnumnuts=2106")
    parser.add_argument("vystupny_soubor", help="Název výstupního CSV souboru vcetne pripony .csv")
    args = parser.parse_args()

    main(args.url, args.vystupny_soubor)
