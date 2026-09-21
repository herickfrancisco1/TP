"""
PetVerde - Coleta de dados (Web Scraping com Beautiful Soup)

Extrai o texto de artigos da Wikipedia relacionados ao tema do projeto
(consumo consciente / ODS 12 e abandono de animais / ODS 15) e salva o
conteudo em arquivos .txt em Data/Raw/, para uso posterior na aplicacao
(nuvem de palavras e estatisticas basicas de texto).

Executar separadamente (fora do Streamlit):
    python Code/DataAcquisition/scrape_wikipedia.py
"""

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
SAIDA = RAIZ / "Data" / "Raw"

PAGINAS = {
    "wiki_consumo_sustentavel.txt": "https://pt.wikipedia.org/wiki/Consumo_sustent%C3%A1vel",
    "wiki_abandono_animais.txt": "https://pt.wikipedia.org/wiki/Abandono_de_animais",
}


def extrair_texto_artigo(url: str) -> str:
    resposta = requests.get(url, headers=HEADERS, timeout=15)
    resposta.raise_for_status()
    sopa = BeautifulSoup(resposta.text, "lxml")
    paragrafos = sopa.select("#mw-content-text p")
    texto = "\n\n".join(p.get_text(" ", strip=True) for p in paragrafos if p.get_text(strip=True))
    return texto


def main() -> None:
    SAIDA.mkdir(parents=True, exist_ok=True)
    for nome_arquivo, url in PAGINAS.items():
        print(f"Coletando: {url}")
        texto = extrair_texto_artigo(url)
        destino = SAIDA / nome_arquivo
        destino.write_text(texto, encoding="utf-8")
        print(f"  -> salvo em {destino} ({len(texto)} caracteres)")


if __name__ == "__main__":
    main()
