"""
PetVerde - Geracao do dataset de amostra (mock)

Gera uma planilha sintetica de produtos do mercado pet (racoes, petiscos,
acessorios), com indicadores de sustentabilidade (embalagem reciclavel,
nota de sustentabilidade, certificacoes), conforme descrito no Data
Summary Report do projeto. Uso de dados de amostra e explicitamente
documentado como tal (ver Docs/DataReport/data_summary_report.md).

Executar separadamente (fora do Streamlit):
    python Code/DataAcquisition/gerar_dados_amostra.py
"""

import pathlib

import numpy as np
import pandas as pd

RAIZ = pathlib.Path(__file__).resolve().parents[2]
SAIDA = RAIZ / "Data" / "Raw" / "sample_products.csv"

CATEGORIAS = ["Ração", "Petisco", "Higiene", "Acessório", "Brinquedo"]
MARCAS = [
    "Verde Pet", "EcoBicho", "Natura Animal", "BioRação", "PetConsciente",
    "Amiga Terra", "RaçãoViva", "Cão & Gato Sustentável", "PetLove Verde", "Reciclapet",
]
EMBALAGENS = ["Plástico não reciclável", "Plástico reciclável", "Papel/Kraft", "Refil", "Vidro"]
CERTIFICACOES = [
    "Nenhuma", "Selo ABNT Reciclável", "Certificação Vegana", "Rainforest Alliance",
    "Selo Cruelty-Free", "Carbono Neutro (autodeclarado)",
]
ODS_RELACIONADOS = ["ODS 12", "ODS 12 e 15", "ODS 15"]


def gerar_dataset(seed: int = 42, n_produtos: int = 120) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    linhas = []
    for i in range(1, n_produtos + 1):
        categoria = rng.choice(CATEGORIAS)
        marca = rng.choice(MARCAS)
        embalagem = rng.choice(EMBALAGENS, p=[0.30, 0.30, 0.20, 0.12, 0.08])
        reciclavel = embalagem in ("Plástico reciclável", "Papel/Kraft", "Refil", "Vidro")
        certificacao = rng.choice(CERTIFICACOES, p=[0.45, 0.20, 0.10, 0.08, 0.10, 0.07])
        nota_base = rng.uniform(3.0, 9.5)
        bonus_embalagem = 1.5 if reciclavel else 0
        bonus_certificacao = 0 if certificacao == "Nenhuma" else 0.8
        nota_sustentabilidade = round(min(10, nota_base + bonus_embalagem + bonus_certificacao), 1)
        preco = round(rng.uniform(9.90, 249.90), 2)
        pegada_carbono_kgco2 = round(rng.uniform(0.2, 8.5), 2)
        ods_relacionado = rng.choice(ODS_RELACIONADOS, p=[0.55, 0.35, 0.10])
        linhas.append({
            "id_produto": i,
            "nome_produto": f"{categoria} {marca} #{i}",
            "categoria": categoria,
            "marca": marca,
            "tipo_embalagem": embalagem,
            "embalagem_reciclavel": reciclavel,
            "certificacao": certificacao,
            "nota_sustentabilidade": nota_sustentabilidade,
            "preco_reais": preco,
            "pegada_carbono_kgco2": pegada_carbono_kgco2,
            "ods_relacionado": ods_relacionado,
        })
    return pd.DataFrame(linhas)


def main() -> None:
    SAIDA.parent.mkdir(parents=True, exist_ok=True)
    df = gerar_dataset()
    df.to_csv(SAIDA, index=False, encoding="utf-8-sig")
    print(f"{len(df)} produtos de amostra salvos em {SAIDA}")


if __name__ == "__main__":
    main()
