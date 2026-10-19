"""
PetVerde - Funções compartilhadas pelas páginas do Streamlit.

Centraliza caminhos, carregamento de dados com cache e o cliente HTTP da
API FastAPI, para que cada página cuide só da sua própria interface.
"""

from __future__ import annotations

import json
import os
import pathlib
import sys

import pandas as pd
import requests
import streamlit as st

RAIZ = pathlib.Path(__file__).resolve().parent.parent
DATA_RAW = RAIZ / "Data" / "Raw"
DATA_PROCESSED = RAIZ / "Data" / "Processed"

# Permite reaproveitar nas páginas a mesma lógica usada pela API e pelos scripts de IA.
for _pasta in (RAIZ / "Code" / "Deployment", RAIZ / "Code" / "Modeling"):
    if str(_pasta) not in sys.path:
        sys.path.insert(0, str(_pasta))

API_URL = os.environ.get("PETVERDE_API_URL", "http://127.0.0.1:8000").rstrip("/")
COMANDO_API = "uvicorn Code.Deployment.api:app --reload"


# ---------------------------------------------------------------------------
# Dados locais (com cache)
# ---------------------------------------------------------------------------
@st.cache_data(show_spinner=False)
def carregar_csv(nome: str, pasta: str = "Processed") -> pd.DataFrame:
    caminho = (DATA_PROCESSED if pasta == "Processed" else DATA_RAW) / nome
    if not caminho.exists():
        return pd.DataFrame()
    return pd.read_csv(caminho, encoding="utf-8-sig")


@st.cache_data(show_spinner=False)
def carregar_noticias() -> pd.DataFrame:
    """Usa as notícias enriquecidas pelo Selenium quando existirem."""
    detalhadas = carregar_csv("noticias_detalhadas.csv")
    if not detalhadas.empty:
        return detalhadas
    noticias = carregar_csv("noticias_tratadas.csv")
    return noticias if not noticias.empty else carregar_csv("noticias_petverde.csv", "Raw")


@st.cache_data(show_spinner=False)
def carregar_corpus() -> pd.DataFrame:
    caminho = DATA_PROCESSED / "corpus_llm.jsonl"
    if not caminho.exists():
        return pd.DataFrame()
    with open(caminho, encoding="utf-8") as arquivo:
        return pd.DataFrame([json.loads(linha) for linha in arquivo if linha.strip()])


@st.cache_data(show_spinner=False)
def carregar_texto(nome_arquivo: str) -> str:
    caminho = DATA_RAW / nome_arquivo
    return caminho.read_text(encoding="utf-8") if caminho.exists() else ""


def formatar_numero(valor: float, casas: int = 0) -> str:
    """1234.5 -> '1.234,5' (padrão brasileiro)."""
    texto = f"{valor:,.{casas}f}"
    return texto.replace(",", "X").replace(".", ",").replace("X", ".")


# ---------------------------------------------------------------------------
# Cliente da API FastAPI
# ---------------------------------------------------------------------------
def chamar_api(metodo: str, rota: str, **kwargs) -> tuple[bool, object, int | None]:
    """Faz a requisição e devolve (sucesso, dados_ou_mensagem, status_http)."""
    try:
        resposta = requests.request(metodo, f"{API_URL}{rota}", timeout=5, **kwargs)
    except requests.RequestException:
        return False, f"Não foi possível conectar à API em {API_URL}.", None
    try:
        corpo = resposta.json()
    except ValueError:
        corpo = resposta.text
    return resposta.ok, corpo, resposta.status_code


def api_disponivel() -> bool:
    ok, _, _ = chamar_api("GET", "/saude")
    return ok


def aviso_api_offline() -> None:
    st.error(f"A API PetVerde não está respondendo em `{API_URL}`.")
    st.markdown("Abra **outro terminal** na raiz do projeto e inicie a API:")
    st.code(COMANDO_API, language="bash")
    st.caption("Depois, clique em **Testar conexão** novamente. "
               "Para usar outro endereço, defina a variável de ambiente `PETVERDE_API_URL`.")
