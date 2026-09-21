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


def main() -> None:
    PROCESSADO.mkdir(parents=True, exist_ok=True)

    produtos = preparar_produtos()
    produtos.to_csv(PROCESSADO / "produtos_tratados.csv", index=False, encoding="utf-8-sig")
    print(f"produtos_tratados.csv: {len(produtos)} linhas")

    noticias = preparar_noticias()
    if not noticias.empty:
        noticias.to_csv(PROCESSADO / "noticias_tratadas.csv", index=False, encoding="utf-8-sig")
        print(f"noticias_tratadas.csv: {len(noticias)} linhas")


if __name__ == "__main__":
    main()
