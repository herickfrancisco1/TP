"""
PetVerde - Preparacao de dados (fase Data Preparation do TDSP)

Le os dados brutos gerados/coletados em Data/Raw/, faz limpeza basica
(tipos, duplicatas, texto) e grava a versao tratada em Data/Processed/,
pronta para ser consumida pela aplicacao Streamlit.

Executar separadamente (fora do Streamlit):
    python Code/DataPreparation/prepare_data.py
"""

import pathlib

import pandas as pd

RAIZ = pathlib.Path(__file__).resolve().parents[2]
BRUTO = RAIZ / "Data" / "Raw"
PROCESSADO = RAIZ / "Data" / "Processed"


def preparar_produtos() -> pd.DataFrame:
    df = pd.read_csv(BRUTO / "sample_products.csv", encoding="utf-8-sig")
    df = df.drop_duplicates(subset="id_produto").reset_index(drop=True)
    df["embalagem_reciclavel"] = df["embalagem_reciclavel"].astype(bool)
    df["nota_sustentabilidade"] = df["nota_sustentabilidade"].clip(0, 10)
    for coluna in ["categoria", "marca", "tipo_embalagem", "certificacao", "ods_relacionado"]:
        df[coluna] = df[coluna].astype(str).str.strip()
    return df


def preparar_noticias() -> pd.DataFrame:
    caminho = BRUTO / "noticias_petverde.csv"
    if not caminho.exists():
        return pd.DataFrame()
    df = pd.read_csv(caminho, encoding="utf-8-sig")
    df = df.drop_duplicates(subset="titulo").reset_index(drop=True)
    df["data_publicacao"] = pd.to_datetime(df["data_publicacao"], errors="coerce", utc=True)
    return df.sort_values("data_publicacao", ascending=False)


def preparar_noticias_detalhadas(noticias: pd.DataFrame) -> pd.DataFrame:
    """TP3: junta às notícias tratadas o que o Selenium coletou (URL final + descrição).

    A junção é feita pelo link do Google Notícias (left join), então todas as
    notícias continuam na tabela mesmo que o Selenium tenha visitado só parte delas
    (ex.: --limite 10) ou não tenha conseguido ler a descrição de alguma página.
    """
    caminho = BRUTO / "noticias_detalhadas_selenium.csv"
    if noticias.empty or not caminho.exists():
        return pd.DataFrame()
    selenium = pd.read_csv(caminho, encoding="utf-8-sig")
    colunas_extras = ["link", "url_final", "titulo_pagina", "descricao", "status_coleta"]
    selenium = selenium[colunas_extras].drop_duplicates(subset="link")
    df = noticias.merge(selenium, on="link", how="left")
    df["descricao"] = df["descricao"].fillna("").astype(str).str.strip()
    df["status_coleta"] = df["status_coleta"].fillna("nao_visitada")
    return df


def preparar_openpetfoodfacts() -> pd.DataFrame:
    """TP3: produtos reais coletados da API do Open Pet Food Facts."""
    caminho = BRUTO / "openpetfoodfacts_produtos.csv"
    if not caminho.exists():
        return pd.DataFrame()
    df = pd.read_csv(caminho, encoding="utf-8-sig", dtype={"codigo_barras": str})
    df = df.drop_duplicates(subset="codigo_barras").reset_index(drop=True)
    df["nome_produto"] = df["nome_produto"].astype(str).str.strip()
    df = df[df["nome_produto"].str.len() > 0]
    # Embalagem: True / False / vazio (desconhecido) -> texto amigável para o painel
    df["embalagem_reciclavel"] = df["embalagem_reciclavel"].map(
        {True: "Sim", False: "Não", "True": "Sim", "False": "Não"}
    ).fillna("Sem informação")
    for coluna in ["marcas", "embalagem", "selos", "ecoscore"]:
        df[coluna] = df[coluna].fillna("").astype(str).str.strip()
    return df


def main() -> None:
    PROCESSADO.mkdir(parents=True, exist_ok=True)

    produtos = preparar_produtos()
    produtos.to_csv(PROCESSADO / "produtos_tratados.csv", index=False, encoding="utf-8-sig")
    print(f"produtos_tratados.csv: {len(produtos)} linhas")

    noticias = preparar_noticias()
    if not noticias.empty:
        noticias.to_csv(PROCESSADO / "noticias_tratadas.csv", index=False, encoding="utf-8-sig")
        print(f"noticias_tratadas.csv: {len(noticias)} linhas")

    detalhadas = preparar_noticias_detalhadas(noticias)
    if not detalhadas.empty:
        detalhadas.to_csv(PROCESSADO / "noticias_detalhadas.csv", index=False, encoding="utf-8-sig")
        print(f"noticias_detalhadas.csv: {len(detalhadas)} linhas "
              f"({(detalhadas['descricao'] != '').sum()} com descrição)")

    reais = preparar_openpetfoodfacts()
    if not reais.empty:
        reais.to_csv(PROCESSADO / "produtos_reais_opff.csv", index=False, encoding="utf-8-sig")
        print(f"produtos_reais_opff.csv: {len(reais)} linhas")


if __name__ == "__main__":
    main()
