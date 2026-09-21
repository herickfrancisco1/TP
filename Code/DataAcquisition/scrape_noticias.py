"""
PetVerde - Coleta de dados (Web Scraping com Beautiful Soup)

Extrai manchetes de noticias publicas (via feed RSS do Google Noticias,
que e HTML/XML publico, sem necessidade de login ou chave de API) sobre
consumo consciente no mercado pet e sustentabilidade/ESG, e salva os
resultados em Data/Raw/noticias_petverde.csv.

Executar separadamente (fora do Streamlit):
    python Code/DataAcquisition/scrape_noticias.py
"""

import csv
import pathlib

import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120 Safari/537.36"
    )
}

RAIZ = pathlib.Path(__file__).resolve().parents[2]
SAIDA = RAIZ / "Data" / "Raw" / "noticias_petverde.csv"

TERMOS_BUSCA = [
    "consumo consciente pet",
    "sustentabilidade petshop",
    "abandono de animais adocao",
]

BASE_RSS = "https://news.google.com/rss/search?q={termo}&hl=pt-BR&gl=BR&ceid=BR:pt"


def coletar_noticias(termo: str, limite: int = 15) -> list[dict]:
    url = BASE_RSS.format(termo=requests.utils.quote(termo))
    resposta = requests.get(url, headers=HEADERS, timeout=15)
    resposta.raise_for_status()
    sopa = BeautifulSoup(resposta.content, "xml")
    itens = sopa.find_all("item")[:limite]
    noticias = []
    for item in itens:
        titulo = item.title.get_text(strip=True) if item.title else ""
        link = item.link.get_text(strip=True) if item.link else ""
        data_pub = item.pubDate.get_text(strip=True) if item.pubDate else ""
        fonte = item.source.get_text(strip=True) if item.source else ""
        noticias.append({
            "termo_busca": termo,
            "titulo": titulo,
            "fonte": fonte,
            "data_publicacao": data_pub,
            "link": link,
        })
    return noticias


def main() -> None:
    SAIDA.parent.mkdir(parents=True, exist_ok=True)
    todas_noticias = []
    for termo in TERMOS_BUSCA:
        print(f"Coletando noticias para: '{termo}'")
        noticias = coletar_noticias(termo)
        print(f"  -> {len(noticias)} noticias encontradas")
        todas_noticias.extend(noticias)

    with open(SAIDA, "w", newline="", encoding="utf-8-sig") as arquivo:
        campos = ["termo_busca", "titulo", "fonte", "data_publicacao", "link"]
        escritor = csv.DictWriter(arquivo, fieldnames=campos)
        escritor.writeheader()
        escritor.writerows(todas_noticias)

    print(f"Total: {len(todas_noticias)} noticias salvas em {SAIDA}")


if __name__ == "__main__":
    main()
