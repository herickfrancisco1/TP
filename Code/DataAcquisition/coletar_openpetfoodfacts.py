"""
PetVerde - Coleta de produtos REAIS via API pública do Open Pet Food Facts (TP3)

O Open Pet Food Facts é uma base colaborativa e aberta (licença ODbL) de
rações e petiscos, irmã do Open Food Facts. Diferente do Google Notícias,
ele oferece uma API REST em JSON, então NÃO é preciso Selenium: basta
`requests`, o que mantém a coleta simples (como recomenda o enunciado).

Para cada espécie (cães e gatos), a coleta tenta primeiro produtos vendidos
no Brasil; se houver poucos, completa com produtos de outros países.

Saída: Data/Raw/openpetfoodfacts_produtos.csv

Executar separadamente (fora do Streamlit):
    python Code/DataAcquisition/coletar_openpetfoodfacts.py
"""

from __future__ import annotations

import csv
import pathlib
import time

import requests

RAIZ = pathlib.Path(__file__).resolve().parents[2]
SAIDA = RAIZ / "Data" / "Raw" / "openpetfoodfacts_produtos.csv"

URL_BUSCA = "https://world.openpetfoodfacts.org/api/v2/search"
# A Open Food Facts pede um User-Agent que identifique o projeto.
HEADERS = {"User-Agent": "PetVerde/3.0 (projeto academico - github.com/herickfrancisco1/TP)"}

ESPECIES = {"Cão": "en:dog-food", "Gato": "en:cat-food"}
CAMPOS_API = [
    "code", "product_name", "product_name_pt", "brands", "categories_tags",
    "packaging_tags", "labels_tags", "countries_tags", "ecoscore_grade",
]
POR_PAGINA = 100
MINIMO_BRASIL = 30
PAUSA = 6  # segundos - a API de busca permite ~10 requisições por minuto

PALAVRAS_RECICLAVEL = ("paper", "cardboard", "carton", "glass", "metal", "aluminium", "steel",
                       "recycl", "papel", "papelao", "vidro")
PALAVRAS_PLASTICO = ("plastic", "plastico", "pp-", "pe-", "pet-")

CAMPOS_SAIDA = [
    "codigo_barras", "nome_produto", "marcas", "especie", "embalagem",
    "embalagem_reciclavel", "selos", "vendido_no_brasil", "ecoscore", "url",
]


def buscar_pagina(categoria: str, pais: str | None, pagina: int) -> dict:
    parametros = {
        "categories_tags": categoria,
        "fields": ",".join(CAMPOS_API),
        "page_size": POR_PAGINA,
        "page": pagina,
    }
    if pais:
        parametros["countries_tags"] = pais
    resposta = requests.get(URL_BUSCA, params=parametros, headers=HEADERS, timeout=30)
    resposta.raise_for_status()
    return resposta.json()


def limpar_tags(tags: list[str] | None) -> str:
    """'en:plastic-bag' -> 'plastic bag' (sem prefixo de idioma)."""
    return "; ".join(t.split(":", 1)[-1].replace("-", " ") for t in (tags or []))


def classificar_embalagem(tags: list[str] | None) -> str:
    """Retorna 'True', 'False' ou '' (desconhecido) a partir das tags de embalagem."""
    texto = " ".join(tags or []).lower()
    if not texto:
        return ""
    if any(p in texto for p in PALAVRAS_RECICLAVEL):
        return "True"
    if any(p in texto for p in PALAVRAS_PLASTICO):
        return "False"
    return ""


def converter(produto: dict, especie: str) -> dict:
    codigo = produto.get("code", "")
    return {
        "codigo_barras": codigo,
        "nome_produto": produto.get("product_name_pt") or produto.get("product_name") or "",
        "marcas": produto.get("brands", ""),
        "especie": especie,
        "embalagem": limpar_tags(produto.get("packaging_tags")),
        "embalagem_reciclavel": classificar_embalagem(produto.get("packaging_tags")),
        "selos": limpar_tags(produto.get("labels_tags")),
        "vendido_no_brasil": "en:brazil" in (produto.get("countries_tags") or []),
        "ecoscore": produto.get("ecoscore_grade", ""),
        "url": f"https://world.openpetfoodfacts.org/product/{codigo}" if codigo else "",
    }


def coletar_especie(especie: str, categoria: str, max_produtos: int = 150) -> list[dict]:
    coletados: dict[str, dict] = {}
    for pais in ("en:brazil", None):
        pagina = 1
        while len(coletados) < max_produtos:
            dados = buscar_pagina(categoria, pais, pagina)
            produtos = dados.get("products", [])
            for produto in produtos:
                if produto.get("code") and (produto.get("product_name") or produto.get("product_name_pt")):
                    coletados.setdefault(produto["code"], converter(produto, especie))
            print(f"  {especie} | país={pais or 'todos'} | página {pagina}: {len(produtos)} itens "
                  f"(acumulado {len(coletados)})")
            time.sleep(PAUSA)
            if len(produtos) < POR_PAGINA:
                break
            pagina += 1
        if pais and len(coletados) >= MINIMO_BRASIL:
            break  # já há produtos brasileiros suficientes
    return list(coletados.values())[:max_produtos]


def main() -> None:
    SAIDA.parent.mkdir(parents=True, exist_ok=True)
    todos = []
    for especie, categoria in ESPECIES.items():
        print(f"Coletando {especie} ({categoria})...")
        try:
            todos.extend(coletar_especie(especie, categoria))
        except requests.RequestException as erro:
            print(f"  Falha na coleta de {especie}: {erro}")

    if not todos:
        raise SystemExit("Nenhum produto coletado (verifique a conexão com a internet).")

    with open(SAIDA, "w", newline="", encoding="utf-8-sig") as arquivo:
        escritor = csv.DictWriter(arquivo, fieldnames=CAMPOS_SAIDA)
        escritor.writeheader()
        escritor.writerows(todos)
    print(f"Total: {len(todos)} produtos reais salvos em {SAIDA}")


if __name__ == "__main__":
    main()
