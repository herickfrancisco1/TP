"""Página de textos: nuvem de palavras, estatísticas de texto e notícias coletadas."""

import io
import re
from collections import Counter

import matplotlib
import pandas as pd
import streamlit as st

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from wordcloud import STOPWORDS as WC_STOPWORDS  # noqa: E402
from wordcloud import WordCloud  # noqa: E402

from comum import carregar_noticias, carregar_texto, formatar_numero  # noqa: E402

STOPWORDS_PT = {
    "de", "a", "o", "que", "e", "do", "da", "em", "um", "para", "com", "não", "uma", "os",
    "no", "se", "na", "por", "mais", "as", "dos", "como", "mas", "ao", "ele", "das", "seu",
    "sua", "ou", "quando", "muito", "nos", "já", "eu", "também", "só", "pelo", "pela", "até",
    "isso", "ela", "entre", "depois", "sem", "mesmo", "aos", "seus", "quem", "nas", "me",
    "esse", "eles", "você", "essa", "num", "nem", "suas", "meu", "às", "minha", "numa",
    "pelos", "elas", "qual", "será", "nós", "tenho", "lhe", "deles", "essas", "esses",
    "pelas", "este", "dele", "tu", "te", "vocês", "vos", "lhes", "meus", "minhas", "teu",
    "tua", "teus", "tuas", "nosso", "nossa", "nossos", "nossas", "dela", "delas", "esta",
    "estes", "estas", "aquele", "aquela", "aqueles", "aquelas", "isto", "aquilo", "sobre",
    "ser", "tem", "foi", "são", "pode", "podem", "seja", "sendo", "assim", "cada", "onde",
    "outra", "outro", "outras", "outros", "então", "ainda", "todo", "toda", "todos", "todas",
    "há", "the", "of", "and", "to", "in", "editar", "editar código", "ver também",
}


@st.cache_data(show_spinner=False)
def gerar_nuvem_palavras_png(texto: str) -> bytes:
    stopwords = STOPWORDS_PT | set(WC_STOPWORDS)
    nuvem = WordCloud(
        width=1000, height=450, background_color="white",
        stopwords=stopwords, colormap="Greens", collocations=False,
    ).generate(texto)
    fig, eixo = plt.subplots(figsize=(10, 4.5))
    eixo.imshow(nuvem, interpolation="bilinear")
    eixo.axis("off")
    buffer = io.BytesIO()
    fig.savefig(buffer, format="png", bbox_inches="tight", pad_inches=0)
    plt.close(fig)
    return buffer.getvalue()


def calcular_frequencia_palavras(texto: str, top_n: int = 15) -> pd.DataFrame:
    palavras = re.findall(r"[A-Za-zÀ-ÿ]{3,}", texto.lower())
    contagem = Counter(p for p in palavras if p not in STOPWORDS_PT)
    return pd.DataFrame(contagem.most_common(top_n), columns=["Palavra", "Ocorrências"])


st.title("📰 Notícias & Nuvem de Palavras")
st.caption("Exploração dos textos coletados (Beautiful Soup + Selenium) — base para as tarefas com LLM")

df_noticias = carregar_noticias()

# Textos disponíveis: artigos da Wikipedia + manchetes/descrições das notícias
textos_disponiveis = {
    "Consumo sustentável (Wikipedia · ODS 12)": carregar_texto("wiki_consumo_sustentavel.txt"),
    "Abandono de animais (Wikipedia · ODS 15)": carregar_texto("wiki_abandono_animais.txt"),
}
if not df_noticias.empty:
    # Remove o nome do veículo que o Google Notícias coloca no fim do título
    partes = df_noticias["titulo"].fillna("").astype(str).str.replace(r" - [^-]+$", "", regex=True)
    if "descricao" in df_noticias.columns:
        partes = partes + ". " + df_noticias["descricao"].fillna("").astype(str)
    textos_disponiveis["Notícias coletadas (títulos e descrições)"] = "\n".join(partes)

st.subheader("☁️ Nuvem de palavras")
escolha_texto = st.selectbox("Fonte de texto", list(textos_disponiveis.keys()))
texto = textos_disponiveis[escolha_texto]

if texto:
    st.image(gerar_nuvem_palavras_png(texto), width="stretch")

    palavras = re.findall(r"[A-Za-zÀ-ÿ]{3,}", texto.lower())
    e1, e2, e3 = st.columns(3)
    e1.metric("Caracteres", formatar_numero(len(texto)))
    e2.metric("Palavras", formatar_numero(len(palavras)))
    e3.metric("Palavras únicas", formatar_numero(len(set(palavras))))

    st.markdown("**Palavras mais frequentes**")
    st.dataframe(calcular_frequencia_palavras(texto), width="stretch", height=250)
else:
    st.warning("Nenhum texto encontrado. Execute os scripts de Code/DataAcquisition.")

st.divider()
st.subheader("📰 Notícias coletadas (Google Notícias)")

if df_noticias.empty:
    st.warning("Nenhuma notícia encontrada.")
else:
    tem_selenium = "descricao" in df_noticias.columns
    c1, c2, c3 = st.columns(3)
    c1.metric("Notícias", len(df_noticias))
    c2.metric("Veículos diferentes", df_noticias["fonte"].nunique())
    if tem_selenium:
        c3.metric("Com descrição (Selenium)", int((df_noticias["descricao"].fillna("") != "").sum()))
    else:
        c3.metric("Com descrição (Selenium)", "—")
        st.info("Para coletar a descrição de cada notícia (página dinâmica), rode "
                "`python Code/DataAcquisition/scrape_noticias_selenium.py` e depois "
                "`python Code/DataPreparation/prepare_data.py`.")

    termos = sorted(df_noticias["termo_busca"].dropna().unique().tolist())
    termos_selecionados = st.multiselect("Filtrar por termo de busca", termos, default=termos)
    busca = st.text_input("Buscar no título", placeholder="ex.: adoção")
    df_noticias_filtrado = df_noticias[df_noticias["termo_busca"].isin(termos_selecionados)]
    if busca:
        df_noticias_filtrado = df_noticias_filtrado[
            df_noticias_filtrado["titulo"].str.contains(busca, case=False, na=False, regex=False)
        ]

    colunas = ["termo_busca", "titulo", "fonte", "data_publicacao"]
    if tem_selenium:
        colunas += ["descricao", "url_final", "status_coleta"]
    else:
        colunas += ["link"]
    st.dataframe(
        df_noticias_filtrado[[c for c in colunas if c in df_noticias_filtrado.columns]],
        width="stretch", height=380,
        column_config={
            "link": st.column_config.LinkColumn("Link"),
            "url_final": st.column_config.LinkColumn("Notícia (URL final)"),
        },
    )
