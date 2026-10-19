"""
PetVerde - Camada de acesso a dados (usada pela API FastAPI)

Centraliza a leitura e a escrita dos arquivos de Data/ para que a API
(Code/Deployment/api.py) fique enxuta e para que a lógica possa ser
testada sem subir o servidor (ver tests/).

Arquivos usados:
- Data/Processed/produtos_tratados.csv      -> base de produtos (amostra/mock)
- Data/Processed/produtos_enviados_api.csv  -> produtos enviados via POST /produtos
- Data/Processed/noticias_tratadas.csv      -> notícias (Google Notícias)
- Data/Processed/noticias_detalhadas.csv    -> notícias enriquecidas via Selenium (opcional)
- Data/Processed/corpus_llm.jsonl           -> corpus de textos preparado para LLMs
"""

from __future__ import annotations

import json
import os
import pathlib
import re
from collections import Counter

import pandas as pd

RAIZ = pathlib.Path(__file__).resolve().parents[2]

# A pasta de dados pode ser trocada por variável de ambiente (útil nos testes,
# para não sujar os arquivos versionados do repositório).
DATA_DIR = pathlib.Path(os.environ.get("PETVERDE_DATA_DIR", RAIZ / "Data"))
DATA_RAW = DATA_DIR / "Raw"
DATA_PROCESSED = DATA_DIR / "Processed"

ARQ_PRODUTOS_BASE = DATA_PROCESSED / "produtos_tratados.csv"
ARQ_PRODUTOS_API = DATA_PROCESSED / "produtos_enviados_api.csv"
ARQ_NOTICIAS = DATA_PROCESSED / "noticias_tratadas.csv"
ARQ_NOTICIAS_DETALHADAS = DATA_PROCESSED / "noticias_detalhadas.csv"
ARQ_CORPUS = DATA_PROCESSED / "corpus_llm.jsonl"

COLUNAS_PRODUTO = [
    "id_produto", "nome_produto", "categoria", "marca", "tipo_embalagem",
    "embalagem_reciclavel", "certificacao", "nota_sustentabilidade",
    "preco_reais", "pegada_carbono_kgco2", "ods_relacionado", "origem",
]

EMBALAGENS_RECICLAVEIS = {"Plástico reciclável", "Papel/Kraft", "Refil", "Vidro"}


# ---------------------------------------------------------------------------
# Utilitários
# ---------------------------------------------------------------------------
def df_para_registros(df: pd.DataFrame) -> list[dict]:
    """Converte um DataFrame em lista de dicionários prontos para JSON.

    Passar por to_json resolve NaN -> null, tipos numpy -> tipos nativos e
    datas -> texto ISO, evitando erros de serialização na API.
    """
    if df.empty:
        return []
    return json.loads(df.to_json(orient="records", force_ascii=False, date_format="iso"))


def _normalizar_bool(serie: pd.Series) -> pd.Series:
    mapa = {"true": True, "false": False, "1": True, "0": False, "sim": True, "não": False, "nao": False}
    return serie.map(lambda v: v if isinstance(v, bool) else mapa.get(str(v).strip().lower(), False)).astype(bool)


# ---------------------------------------------------------------------------
# Produtos
# ---------------------------------------------------------------------------
def carregar_produtos(incluir_enviados: bool = True) -> pd.DataFrame:
    """Base de produtos (mock) + produtos enviados pela API, numa só tabela."""
    partes = []
    if ARQ_PRODUTOS_BASE.exists():
        base = pd.read_csv(ARQ_PRODUTOS_BASE, encoding="utf-8-sig")
        base["origem"] = "amostra"
        partes.append(base)
    if incluir_enviados and ARQ_PRODUTOS_API.exists():
        enviados = pd.read_csv(ARQ_PRODUTOS_API, encoding="utf-8-sig")
        enviados["origem"] = "api"
        partes.append(enviados)
    if not partes:
        return pd.DataFrame(columns=COLUNAS_PRODUTO)
    df = pd.concat(partes, ignore_index=True, sort=False)
    df["embalagem_reciclavel"] = _normalizar_bool(df["embalagem_reciclavel"])
    return df


def filtrar_produtos(
    df: pd.DataFrame,
    categoria: str | None = None,
    reciclavel: bool | None = None,
    nota_min: float | None = None,
    nota_max: float | None = None,
    busca: str | None = None,
    ordenar_por: str = "nota_sustentabilidade",
    decrescente: bool = True,
    limite: int = 50,
    deslocamento: int = 0,
) -> pd.DataFrame:
    """Aplica os mesmos filtros oferecidos na página de produtos do Streamlit."""
    if categoria:
        df = df[df["categoria"].str.lower() == categoria.lower()]
    if reciclavel is not None:
        df = df[df["embalagem_reciclavel"] == reciclavel]
    if nota_min is not None:
        df = df[df["nota_sustentabilidade"] >= nota_min]
    if nota_max is not None:
        df = df[df["nota_sustentabilidade"] <= nota_max]
    if busca:
        df = df[df["nome_produto"].str.contains(busca, case=False, na=False, regex=False)]
    if ordenar_por in df.columns:
        df = df.sort_values(ordenar_por, ascending=not decrescente, kind="stable")
    return df.iloc[deslocamento: deslocamento + limite]


def buscar_produto(id_produto: int) -> dict | None:
    df = carregar_produtos()
    linha = df[df["id_produto"] == id_produto]
    if linha.empty:
        return None
    return df_para_registros(linha)[0]


def calcular_nota_sustentabilidade(tipo_embalagem: str, certificacao: str, pegada_carbono_kgco2: float) -> float:
    """Regra simples e transparente para estimar a nota de um produto novo.

    Parte de 5,0; soma 2,5 se a embalagem é reciclável e 1,5 se há certificação;
    desconta até 2,5 pontos conforme a pegada de carbono (escala de 0 a 8,5 kg CO2).
    """
    nota = 5.0
    if tipo_embalagem in EMBALAGENS_RECICLAVEIS:
        nota += 2.5
    if certificacao and certificacao.strip().lower() != "nenhuma":
        nota += 1.5
    nota -= min(max(pegada_carbono_kgco2, 0), 8.5) / 8.5 * 2.5
    return round(min(max(nota, 0.0), 10.0), 1)


def adicionar_produto(dados: dict) -> dict:
    """Grava um novo produto em produtos_enviados_api.csv e devolve o registro."""
    df_atual = carregar_produtos()
    proximo_id = int(df_atual["id_produto"].max()) + 1 if not df_atual.empty else 1

    registro = {
        "id_produto": proximo_id,
        "nome_produto": dados["nome_produto"].strip(),
        "categoria": dados["categoria"],
        "marca": dados["marca"].strip(),
        "tipo_embalagem": dados["tipo_embalagem"],
        "embalagem_reciclavel": dados["tipo_embalagem"] in EMBALAGENS_RECICLAVEIS,
        "certificacao": dados.get("certificacao") or "Nenhuma",
        "nota_sustentabilidade": dados.get("nota_sustentabilidade"),
        "preco_reais": round(float(dados["preco_reais"]), 2),
        "pegada_carbono_kgco2": round(float(dados["pegada_carbono_kgco2"]), 2),
        "ods_relacionado": dados.get("ods_relacionado") or "ODS 12",
    }
    if registro["nota_sustentabilidade"] is None:
        registro["nota_sustentabilidade"] = calcular_nota_sustentabilidade(
            registro["tipo_embalagem"], registro["certificacao"], registro["pegada_carbono_kgco2"]
        )

    ARQ_PRODUTOS_API.parent.mkdir(parents=True, exist_ok=True)
    novo = pd.DataFrame([registro])
    novo.to_csv(
        ARQ_PRODUTOS_API, mode="a", index=False, encoding="utf-8-sig",
        header=not ARQ_PRODUTOS_API.exists(),
    )
    registro["origem"] = "api"
    return registro


def estatisticas_produtos() -> dict:
    """Indicadores-resumo de sustentabilidade (geral e por categoria)."""
    df = carregar_produtos()
    if df.empty:
        return {"total_produtos": 0, "por_categoria": []}
    por_categoria = (
        df.groupby("categoria")
        .agg(
            produtos=("id_produto", "count"),
            nota_media=("nota_sustentabilidade", "mean"),
            pct_reciclavel=("embalagem_reciclavel", "mean"),
            preco_medio=("preco_reais", "mean"),
            carbono_medio=("pegada_carbono_kgco2", "mean"),
        )
        .reset_index()
    )
    por_categoria["pct_reciclavel"] *= 100
    por_categoria = por_categoria.round(2)
    return {
        "total_produtos": int(len(df)),
        "enviados_via_api": int((df["origem"] == "api").sum()),
        "nota_media": round(float(df["nota_sustentabilidade"].mean()), 2),
        "pct_embalagem_reciclavel": round(float(df["embalagem_reciclavel"].mean() * 100), 1),
        "pegada_carbono_media_kgco2": round(float(df["pegada_carbono_kgco2"].mean()), 2),
        "preco_medio_reais": round(float(df["preco_reais"].mean()), 2),
        "por_categoria": df_para_registros(por_categoria),
    }


# ---------------------------------------------------------------------------
# Notícias
# ---------------------------------------------------------------------------
def carregar_noticias() -> pd.DataFrame:
    """Notícias tratadas; se houver a versão enriquecida via Selenium, usa ela."""
    if ARQ_NOTICIAS_DETALHADAS.exists():
        return pd.read_csv(ARQ_NOTICIAS_DETALHADAS, encoding="utf-8-sig")
    if ARQ_NOTICIAS.exists():
        return pd.read_csv(ARQ_NOTICIAS, encoding="utf-8-sig")
    return pd.DataFrame()


def filtrar_noticias(termo: str | None = None, busca: str | None = None, limite: int = 50) -> pd.DataFrame:
    df = carregar_noticias()
    if df.empty:
        return df
    if termo:
        df = df[df["termo_busca"].str.lower() == termo.lower()]
    if busca:
        df = df[df["titulo"].str.contains(busca, case=False, na=False, regex=False)]
    return df.head(limite)


# ---------------------------------------------------------------------------
# Corpus para LLM
# ---------------------------------------------------------------------------
def carregar_corpus() -> list[dict]:
    if not ARQ_CORPUS.exists():
        return []
    with open(ARQ_CORPUS, encoding="utf-8") as arquivo:
        return [json.loads(linha) for linha in arquivo if linha.strip()]


_PALAVRAS_VAZIAS = {
    "de", "a", "o", "que", "e", "do", "da", "em", "um", "uma", "para", "com", "não", "os", "as",
    "no", "na", "se", "por", "mais", "dos", "das", "como", "ao", "à", "ou", "é", "são", "qual",
    "quais", "quem", "onde", "quando", "sobre", "seu", "sua", "nos", "nas", "pelo", "pela",
}


def _tokenizar(texto: str) -> list[str]:
    return [p for p in re.findall(r"[a-zà-ÿ0-9]{3,}", texto.lower()) if p not in _PALAVRAS_VAZIAS]


def buscar_trechos(pergunta: str, k: int = 3, fonte: str | None = None) -> list[dict]:
    """Recuperação simples por sobreposição de palavras (baseline do futuro RAG).

    Na próxima etapa esta função pode ser trocada por busca vetorial
    (embeddings) sem alterar a rota da API.
    """
    corpus = carregar_corpus()
    if fonte:
        corpus = [c for c in corpus if c["fonte"] == fonte]
    termos = Counter(_tokenizar(pergunta))
    if not termos:
        return []
    resultados = []
    for trecho in corpus:
        tokens = Counter(_tokenizar(trecho["texto"] + " " + trecho.get("titulo", "")))
        pontuacao = sum(min(tokens[t], 3) for t in termos if t in tokens)
        if pontuacao:
            resultados.append({**trecho, "pontuacao": pontuacao})
    resultados.sort(key=lambda r: r["pontuacao"], reverse=True)
    return resultados[:k]
