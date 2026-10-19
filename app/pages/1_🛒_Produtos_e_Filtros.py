"""Página de produtos: tabela, filtros, upload/download de arquivos e gráficos."""

import io
import time

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

from comum import DATA_PROCESSED, DATA_RAW

# Inicializa as variáveis de sessão para os produtos
_DEFAULTS = {
    "df_produtos_completo": None,
    "arquivos_upload_processados": set(),
    "produtos_incluem_api": False,
}
for _chave, _valor in _DEFAULTS.items():
    if _chave not in st.session_state:
        st.session_state[_chave] = _valor


@st.cache_data(show_spinner=False)
def carregar_produtos_base() -> pd.DataFrame:
    caminho = DATA_PROCESSED / "produtos_tratados.csv"
    if not caminho.exists():
        caminho = DATA_RAW / "sample_products.csv"
    df = pd.read_csv(caminho, encoding="utf-8-sig")
    df["embalagem_reciclavel"] = df["embalagem_reciclavel"].astype(bool)
    return df


@st.cache_data(show_spinner=False, ttl=10)
def carregar_produtos_com_api() -> pd.DataFrame:
    """Base + produtos cadastrados via POST /produtos (mesma lógica usada pela API)."""
    import dados_petverde
    return dados_petverde.carregar_produtos(incluir_enviados=True)


def carregar_base(incluir_api: bool) -> pd.DataFrame:
    return carregar_produtos_com_api() if incluir_api else carregar_produtos_base()


def _ler_csv_com_encoding(conteudo: bytes) -> pd.DataFrame:
    for codificacao in ("utf-8-sig", "latin1"):
        try:
            return pd.read_csv(io.BytesIO(conteudo), sep=None, engine="python", encoding=codificacao)
        except UnicodeDecodeError:
            continue
    return pd.read_csv(io.BytesIO(conteudo), sep=None, engine="python", encoding="latin1")


def converter_para_csv(df: pd.DataFrame) -> bytes:
    return df.to_csv(index=False).encode("utf-8-sig")


def converter_para_xlsx(df: pd.DataFrame) -> bytes:
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="produtos")
    return buffer.getvalue()


# Barra lateral: origem dos dados e upload
with st.sidebar:
    st.subheader("🗂️ Origem dos dados")
    incluir_api = st.toggle(
        "Incluir produtos cadastrados via API",
        value=st.session_state["produtos_incluem_api"],
        help="Mostra também os produtos enviados pela rota POST /produtos da API PetVerde.",
    )
    if incluir_api != st.session_state["produtos_incluem_api"] or st.session_state["df_produtos_completo"] is None:
        st.session_state["produtos_incluem_api"] = incluir_api
        st.session_state["df_produtos_completo"] = carregar_base(incluir_api).copy()
        st.session_state["arquivos_upload_processados"] = set()

    st.subheader("📥 Adicionar mais produtos")
    arquivo_extra = st.file_uploader("Envie um CSV com mais produtos", type=["csv"], key="uploader_produtos")
    if arquivo_extra is not None:
        assinatura = f"{arquivo_extra.name}_{arquivo_extra.size}"
        if assinatura not in st.session_state["arquivos_upload_processados"]:
            barra = st.progress(0, text="Processando e mesclando dados...")
            df_novo = _ler_csv_com_encoding(arquivo_extra.getvalue())
            barra.progress(75)
            st.session_state["df_produtos_completo"] = pd.concat(
                [st.session_state["df_produtos_completo"], df_novo], ignore_index=True, sort=False
            )
            st.session_state["arquivos_upload_processados"].add(assinatura)
            barra.progress(100)
            time.sleep(0.3)
            barra.empty()
            st.success(f"{len(df_novo)} linha(s) adicionadas.")

    if st.button("↩️ Remover produtos adicionados", width="stretch"):
        st.session_state["df_produtos_completo"] = carregar_base(incluir_api).copy()
        st.session_state["arquivos_upload_processados"] = set()
        st.rerun()

# Interface Principal
st.title("🛒 Produtos & Filtros")
st.caption("Base de amostra (dados sintéticos) · complemente com upload de CSV ou com produtos "
           "cadastrados pela API.")
df = st.session_state["df_produtos_completo"]

if "embalagem_reciclavel" in df.columns:
    df["embalagem_reciclavel"] = df["embalagem_reciclavel"].fillna(False).astype(bool)
colunas_numericas = [c for c in df.select_dtypes(include=np.number).columns if c != "id_produto"]
colunas_categoricas = [c for c in df.columns if c not in colunas_numericas and c not in ("id_produto", "nome_produto")]

st.subheader(f"Base de produtos ({len(df)} itens)")
st.dataframe(df, width="stretch", height=220)

st.divider()
st.subheader("🔍 Filtros")
col_a, col_b, col_c = st.columns(3)

with col_a:
    categorias_disponiveis = sorted(df["categoria"].dropna().unique().tolist())
    categorias_selecionadas = st.multiselect("Categoria do produto", categorias_disponiveis, default=categorias_disponiveis)
    filtro_reciclavel = st.radio("Filtrar por embalagem", ["Todas", "Somente recicláveis", "Somente não recicláveis"])

with col_b:
    st.markdown("**Colunas a exibir**")
    colunas_marcadas = [coluna for coluna in df.columns if st.checkbox(coluna, value=True)]
    if not colunas_marcadas:
        colunas_marcadas = list(df.columns)

with col_c:
    nota_min, nota_max = float(df["nota_sustentabilidade"].min()), float(df["nota_sustentabilidade"].max())
    faixa_nota = st.slider("Nota de sustentabilidade", nota_min, nota_max, (nota_min, nota_max))
    ordem = st.radio("Direção da ordenação", ["Crescente", "Decrescente"], horizontal=True)

# Aplicação dos Filtros
df_linhas_filtradas = df[df["categoria"].isin(categorias_selecionadas)]
if filtro_reciclavel == "Somente recicláveis":
    df_linhas_filtradas = df_linhas_filtradas[df_linhas_filtradas["embalagem_reciclavel"]]
elif filtro_reciclavel == "Somente não recicláveis":
    df_linhas_filtradas = df_linhas_filtradas[~df_linhas_filtradas["embalagem_reciclavel"]]
df_linhas_filtradas = df_linhas_filtradas[df_linhas_filtradas["nota_sustentabilidade"].between(*faixa_nota)]
df_linhas_filtradas = df_linhas_filtradas.sort_values("nota_sustentabilidade", ascending=(ordem == "Crescente"))

df_filtrado = df_linhas_filtradas[colunas_marcadas]

st.divider()
st.subheader(f"📋 Tabela filtrada ({len(df_filtrado)} itens)")
st.dataframe(df_filtrado, width="stretch", height=300)

col_dl1, col_dl2 = st.columns(2)
with col_dl1:
    st.download_button("⬇️ Baixar dados (CSV)", data=converter_para_csv(df_filtrado), file_name="filtrado.csv", mime="text/csv", width="stretch")
with col_dl2:
    st.download_button("⬇️ Baixar dados (XLSX)", data=converter_para_xlsx(df_filtrado), file_name="filtrado.xlsx", width="stretch")

st.divider()
st.subheader("📈 Gráficos")
if colunas_categoricas and colunas_numericas and len(df_linhas_filtradas):
    col_x, col_y = st.columns(2)
    with col_x:
        eixo_categorico = st.selectbox("Categoria (eixo X)", colunas_categoricas)
    with col_y:
        metrica = st.selectbox("Métrica", colunas_numericas)

    resumo = df_linhas_filtradas.groupby(eixo_categorico, as_index=False)[metrica].mean()
    tab_barras, tab_linhas, tab_pizza = st.tabs(["Barras", "Linhas", "Pizza"])
    with tab_barras:
        st.plotly_chart(px.bar(resumo, x=eixo_categorico, y=metrica, color=eixo_categorico), width="stretch")
    with tab_linhas:
        st.plotly_chart(px.line(resumo, x=eixo_categorico, y=metrica, markers=True), width="stretch")
    with tab_pizza:
        st.plotly_chart(px.pie(resumo, names=eixo_categorico, values=metrica), width="stretch")
else:
    st.info("Nenhum dado para os filtros selecionados.")
