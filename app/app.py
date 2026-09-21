"""
PetVerde - Consumo Consciente para o Mercado Pet
TP2 - Projeto de Bloco (PB) - Aplicacao Streamlit evoluida

Autor: Herick Francisco
ODS: 12 (Consumo e Producao Responsaveis - primario) e 15 (Vida Terrestre - secundario)

Fontes de dados desta etapa (ver Docs/DataReport/data_summary_report.md):
- Data/Raw/sample_products.csv: dataset de amostra (mock) de produtos pet,
  com indicadores de sustentabilidade (documentado como dado ilustrativo).
- Data/Raw/wiki_*.txt: texto extraido via Beautiful Soup de artigos da
  Wikipedia sobre consumo sustentavel e abandono de animais
  (Code/DataAcquisition/scrape_wikipedia.py).
- Data/Raw/noticias_petverde.csv: manchetes extraidas via Beautiful Soup
  do feed publico de noticias do Google Noticias
  (Code/DataAcquisition/scrape_noticias.py).
"""

import io
import pathlib
import re
import time
from collections import Counter

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st
from wordcloud import STOPWORDS as WC_STOPWORDS
from wordcloud import WordCloud

RAIZ = pathlib.Path(__file__).resolve().parent.parent
DATA_RAW = RAIZ / "Data" / "Raw"
DATA_PROCESSED = RAIZ / "Data" / "Processed"

AGENDA_2030_URL = "https://brasil.un.org/pt-br/sdgs"
OPEN_PET_FOOD_FACTS_URL = "https://world.openpetfoodfacts.org/"
IBGE_SIDRA_URL = "https://sidra.ibge.gov.br/"

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

st.set_page_config(
    page_title="PetVerde - Consumo Consciente no Mercado Pet",
    page_icon="🐾",
    layout="wide",
    initial_sidebar_state="expanded",
)

_DEFAULTS = {
    "df_produtos_completo": None,
    "arquivos_upload_processados": set(),
}
for _chave, _valor in _DEFAULTS.items():
    if _chave not in st.session_state:
        st.session_state[_chave] = _valor


# ---------------------------------------------------------------------------
# Cache: dados de produtos, noticias e textos (evita reprocessar a cada
# interacao do usuario)
# ---------------------------------------------------------------------------
@st.cache_data(show_spinner=False)
def carregar_produtos_base() -> pd.DataFrame:
    caminho = DATA_PROCESSED / "produtos_tratados.csv"
    if not caminho.exists():
        caminho = DATA_RAW / "sample_products.csv"
    df = pd.read_csv(caminho, encoding="utf-8-sig")
    df["embalagem_reciclavel"] = df["embalagem_reciclavel"].astype(bool)
    return df


@st.cache_data(show_spinner=False)
def carregar_noticias() -> pd.DataFrame:
    caminho = DATA_PROCESSED / "noticias_tratadas.csv"
    if not caminho.exists():
        caminho = DATA_RAW / "noticias_petverde.csv"
    if not caminho.exists():
        return pd.DataFrame()
    df = pd.read_csv(caminho, encoding="utf-8-sig")
    return df


@st.cache_data(show_spinner=False)
def carregar_texto(nome_arquivo: str) -> str:
    caminho = DATA_RAW / nome_arquivo
    if not caminho.exists():
        return ""
    return caminho.read_text(encoding="utf-8")


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


if st.session_state["df_produtos_completo"] is None:
    st.session_state["df_produtos_completo"] = carregar_produtos_base()

# ---------------------------------------------------------------------------
# Barra lateral
# ---------------------------------------------------------------------------
with st.sidebar:
    st.title("🐾 PetVerde")
    st.caption("TP2 · Streamlit · Consumo consciente no mercado pet")

    st.subheader("📥 Adicionar mais produtos")
    arquivo_extra = st.file_uploader(
        "Envie um CSV com mais produtos (mesmas colunas do dataset base)",
        type=["csv"], key="uploader_produtos_extra",
    )
    if arquivo_extra is not None:
        assinatura = f"{arquivo_extra.name}_{arquivo_extra.size}"
        if assinatura not in st.session_state["arquivos_upload_processados"]:
            barra = st.progress(0, text="Lendo arquivo enviado...")
            with st.spinner("Processando e mesclando dados..."):
                barra.progress(40, text="Convertendo CSV...")
                df_novo = _ler_csv_com_encoding(arquivo_extra.getvalue())
                barra.progress(75, text="Mesclando com dados existentes...")
                st.session_state["df_produtos_completo"] = pd.concat(
                    [st.session_state["df_produtos_completo"], df_novo],
                    ignore_index=True, sort=False,
                )
                st.session_state["arquivos_upload_processados"].add(assinatura)
                time.sleep(0.2)
                barra.progress(100, text="Concluído!")
            time.sleep(0.3)
            barra.empty()
            st.success(f"{len(df_novo)} linha(s) adicionadas de '{arquivo_extra.name}'.")

    if st.button("↩️ Remover produtos adicionados via upload", width="stretch"):
        st.session_state["df_produtos_completo"] = carregar_produtos_base()
        st.session_state["arquivos_upload_processados"] = set()
        st.rerun()

    st.divider()
    st.subheader("🔗 Fontes e referências")
    st.caption(f"[Agenda 2030 - ODS]({AGENDA_2030_URL})")
    st.caption(f"[Open Pet Food Facts]({OPEN_PET_FOOD_FACTS_URL})")
    st.caption(f"[IBGE - SIDRA]({IBGE_SIDRA_URL})")

df = st.session_state["df_produtos_completo"]
if "embalagem_reciclavel" in df.columns:
    df["embalagem_reciclavel"] = df["embalagem_reciclavel"].fillna(False).astype(bool)
colunas_numericas = [c for c in df.select_dtypes(include=np.number).columns if c != "id_produto"]
colunas_categoricas = [c for c in df.columns if c not in colunas_numericas and c != "id_produto"]

st.title("🐾 PetVerde — Consumo Consciente no Mercado Pet")
st.caption(
    "Dashboard de dados a serviço de um petshop sustentável · ODS 12 (primário) e ODS 15 (secundário) · "
    "Agenda 2030"
)

aba_sobre, aba_produtos, aba_noticias = st.tabs(
    ["ℹ️ Sobre o Projeto", "🛒 Produtos & Filtros", "📰 Notícias & Nuvem de Palavras"]
)

# ---------------------------------------------------------------------------
# Aba: Sobre o Projeto
# ---------------------------------------------------------------------------
with aba_sobre:
    st.header("Problema de negócio")
    st.markdown(
        """
O mercado pet brasileiro cresce rapidamente, mas carrega custos socioambientais pouco
visíveis ao consumidor final: embalagens plásticas não recicláveis, alta pegada de carbono
na cadeia produtiva de ração e uma das maiores populações de animais abandonados do mundo.

**Pergunta de negócio:** como ajudar tutores de pets e pequenos petshops a tomar decisões de
compra e de gestão mais sustentáveis, usando dados públicos sobre produtos, abandono/adoção
de animais e boas práticas ESG do setor?

O **PetVerde** reúne dados sobre produtos pet, traduz esses dados em indicadores simples de
sustentabilidade e, nesta etapa (TP2), passa a extrair conteúdo público da web (notícias e
artigos) para complementar a análise.
        """
    )

    st.header("Alinhamento com os ODS (Agenda 2030)")
    col_ods12, col_ods15 = st.columns(2)
    with col_ods12:
        st.success(
            "**ODS 12 — Consumo e Produção Responsáveis** (primário)\n\n"
            "Meta 12.5 (reduzir a geração de resíduos) e Meta 12.8 (garantir acesso à "
            "informação relevante para o desenvolvimento sustentável)."
        )
    with col_ods15:
        st.info(
            "**ODS 15 — Vida Terrestre** (secundário)\n\n"
            "Visibilidade a dados de abandono/adoção de animais, contribuindo para o "
            "bem-estar animal e a conscientização sobre guarda responsável."
        )

    st.header("O que evoluiu no TP2")
    st.markdown(
        """
1. **Interface dinâmica**: abas, filtros por radio/checkbox/multiselect/slider e tabela
   interativa e pesquisável;
2. **Extração de conteúdo da web** com Beautiful Soup (`Code/DataAcquisition/`), salva em
   CSV/TXT em `Data/Raw/`: notícias sobre consumo consciente pet e artigos da Wikipedia
   sobre consumo sustentável e abandono de animais;
3. **Nuvem de palavras e estatísticas básicas** geradas a partir do conteúdo coletado;
4. **Cache** (`st.cache_data`) e **estado de sessão** (`st.session_state`) para performance
   e persistência dos dados entre interações;
5. **Upload/Download de arquivos**: usuário envia um CSV com mais produtos, que passa a
   compor a base exibida no painel, e pode baixar o resultado filtrado em CSV/XLSX.
        """
    )
    st.caption(
        "Dados de produtos são uma amostra (mock), conforme documentado no "
        "[Data Summary Report](../Docs/DataReport/data_summary_report.md); "
        "as notícias e os textos da Wikipedia são reais, coletados via scraping."
    )

# ---------------------------------------------------------------------------
# Aba: Produtos & Filtros
# ---------------------------------------------------------------------------
with aba_produtos:
    st.subheader(f"Base de produtos ({len(df)} itens)")
    st.dataframe(df, width="stretch", height=220)

    st.divider()
    st.subheader("🔍 Filtros")
    col_a, col_b, col_c = st.columns(3)

    with col_a:
        st.markdown("**Categorias (multiselect)**")
        categorias_disponiveis = sorted(df["categoria"].dropna().unique().tolist())
        categorias_selecionadas = st.multiselect(
            "Categoria do produto", categorias_disponiveis, default=categorias_disponiveis,
            key="multiselect_categoria",
        )
        st.markdown("**Embalagem reciclável? (radio)**")
        filtro_reciclavel = st.radio(
            "Filtrar por embalagem", ["Todas", "Somente recicláveis", "Somente não recicláveis"],
            key="radio_reciclavel",
        )

    with col_b:
        st.markdown("**Colunas a exibir (checkbox)**")
        colunas_marcadas = []
        for coluna in df.columns:
            marcado = st.checkbox(coluna, value=True, key=f"chk_col_{coluna}")
            if marcado:
                colunas_marcadas.append(coluna)
        if not colunas_marcadas:
            colunas_marcadas = list(df.columns)

    with col_c:
        st.markdown("**Faixa de nota de sustentabilidade (slider)**")
        nota_min, nota_max = float(df["nota_sustentabilidade"].min()), float(df["nota_sustentabilidade"].max())
        faixa_nota = st.slider(
            "Nota de sustentabilidade", nota_min, nota_max, (nota_min, nota_max), key="slider_nota",
        )
        st.markdown("**Ordenação (radio)**")
        ordem = st.radio("Direção da ordenação", ["Crescente", "Decrescente"], horizontal=True, key="radio_ordem")

    df_linhas_filtradas = df[df["categoria"].isin(categorias_selecionadas)]
    if filtro_reciclavel == "Somente recicláveis":
        df_linhas_filtradas = df_linhas_filtradas[df_linhas_filtradas["embalagem_reciclavel"]]
    elif filtro_reciclavel == "Somente não recicláveis":
        df_linhas_filtradas = df_linhas_filtradas[~df_linhas_filtradas["embalagem_reciclavel"]]
    df_linhas_filtradas = df_linhas_filtradas[df_linhas_filtradas["nota_sustentabilidade"].between(*faixa_nota)]
    if "nota_sustentabilidade" in df_linhas_filtradas.columns:
        df_linhas_filtradas = df_linhas_filtradas.sort_values(
            "nota_sustentabilidade", ascending=(ordem == "Crescente")
        )
    df_filtrado = df_linhas_filtradas[colunas_marcadas]

    st.divider()
    st.subheader("📋 Tabela filtrada")
    st.caption("Clique no cabeçalho de uma coluna para ordenar ou use a busca da própria tabela.")
    st.dataframe(df_filtrado, width="stretch", height=300)

    col_dl1, col_dl2 = st.columns(2)
    with col_dl1:
        st.download_button(
            "⬇️ Baixar dados filtrados (CSV)", data=converter_para_csv(df_filtrado),
            file_name="petverde_produtos_filtrado.csv", mime="text/csv", width="stretch",
        )
    with col_dl2:
        st.download_button(
            "⬇️ Baixar dados filtrados (XLSX)", data=converter_para_xlsx(df_filtrado),
            file_name="petverde_produtos_filtrado.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            width="stretch",
        )

    st.divider()
    st.subheader("📊 Métricas-resumo")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Produtos exibidos", f"{len(df_linhas_filtradas):,}".replace(",", "."))
    if len(df_linhas_filtradas):
        m2.metric("Nota média de sustentabilidade", f"{df_linhas_filtradas['nota_sustentabilidade'].mean():.1f}")
        pct_reciclavel = 100 * df_linhas_filtradas["embalagem_reciclavel"].mean()
        m3.metric("% embalagem reciclável", f"{pct_reciclavel:.0f}%")
        m4.metric("Pegada de carbono média (kgCO₂)", f"{df_linhas_filtradas['pegada_carbono_kgco2'].mean():.2f}")

    st.divider()
    st.subheader("📈 Gráficos")
    if colunas_categoricas and colunas_numericas and len(df_linhas_filtradas):
        col_x, col_y = st.columns(2)
        with col_x:
            indice_padrao = colunas_categoricas.index("categoria") if "categoria" in colunas_categoricas else 0
            eixo_categorico = st.selectbox(
                "Categoria (eixo X)", colunas_categoricas, index=indice_padrao, key="select_cat"
            )
        with col_y:
            metrica = st.selectbox("Métrica", colunas_numericas, key="select_metrica")

        resumo = (
            df_linhas_filtradas.groupby(eixo_categorico, as_index=False)[metrica].mean()
            .sort_values(metrica, ascending=False)
        )
        tab_barras, tab_linhas, tab_pizza = st.tabs(["Barras", "Linhas", "Pizza"])
        with tab_barras:
            st.plotly_chart(
                px.bar(resumo, x=eixo_categorico, y=metrica, color=eixo_categorico,
                       title=f"{metrica} médio por {eixo_categorico}"),
                width="stretch",
            )
        with tab_linhas:
            st.plotly_chart(
                px.line(resumo, x=eixo_categorico, y=metrica, markers=True,
                        title=f"{metrica} médio por {eixo_categorico}"),
                width="stretch",
            )
        with tab_pizza:
            st.plotly_chart(
                px.pie(resumo, names=eixo_categorico, values=metrica,
                       title=f"Participação por {eixo_categorico}"),
                width="stretch",
            )

        st.markdown("**Análise avançada**")
        col_h, col_s = st.columns(2)
        with col_h:
            n_bins = st.slider("Número de faixas (histograma)", 5, 40, 15, key="slider_bins")
            st.plotly_chart(
                px.histogram(df_linhas_filtradas, x=metrica, nbins=n_bins, title=f"Distribuição de {metrica}"),
                width="stretch",
            )
        with col_s:
            if len(colunas_numericas) >= 2:
                outra_metrica = next((c for c in colunas_numericas if c != metrica), metrica)
                st.plotly_chart(
                    px.scatter(df_linhas_filtradas, x=metrica, y=outra_metrica, color=eixo_categorico,
                               title=f"{outra_metrica} vs. {metrica}"),
                    width="stretch",
                )
    else:
        st.warning("Ajuste os filtros para ter ao menos um produto e uma coluna numérica/categórica.")

# ---------------------------------------------------------------------------
# Aba: Notícias & Nuvem de Palavras (conteúdo extraído via Beautiful Soup)
# ---------------------------------------------------------------------------
with aba_noticias:
    st.subheader("☁️ Nuvem de palavras")
    st.caption(
        "Texto extraído com Beautiful Soup de artigos da Wikipedia "
        "(`Code/DataAcquisition/scrape_wikipedia.py`)."
    )
    textos_disponiveis = {
        "Consumo sustentável (ODS 12)": "wiki_consumo_sustentavel.txt",
        "Abandono de animais (ODS 15)": "wiki_abandono_animais.txt",
    }
    escolha_texto = st.selectbox("Fonte de texto", list(textos_disponiveis.keys()), key="select_texto_wiki")
    texto = carregar_texto(textos_disponiveis[escolha_texto])

    if texto:
        with st.spinner("Gerando nuvem de palavras..."):
            imagem_nuvem = gerar_nuvem_palavras_png(texto)
        st.image(imagem_nuvem, width="stretch")

        st.markdown("**Estatísticas básicas do texto**")
        palavras = re.findall(r"[A-Za-zÀ-ÿ]{3,}", texto.lower())
        e1, e2, e3 = st.columns(3)
        e1.metric("Caracteres", f"{len(texto):,}".replace(",", "."))
        e2.metric("Palavras", f"{len(palavras):,}".replace(",", "."))
        e3.metric("Palavras únicas", f"{len(set(palavras)):,}".replace(",", "."))

        st.markdown("**Palavras mais frequentes**")
        st.dataframe(calcular_frequencia_palavras(texto), width="stretch", height=250)

        with st.expander("Ver texto completo extraído"):
            st.write(texto)
    else:
        st.warning(
            "Nenhum texto encontrado. Execute `python Code/DataAcquisition/scrape_wikipedia.py` "
            "para coletar o conteúdo."
        )

    st.divider()
    st.subheader("📰 Notícias coletadas (Google Notícias)")
    st.caption("Coletadas com Beautiful Soup a partir de um feed público de notícias.")
    df_noticias = carregar_noticias()
    if df_noticias.empty:
        st.warning(
            "Nenhuma notícia encontrada. Execute `python Code/DataAcquisition/scrape_noticias.py` "
            "para coletar o conteúdo."
        )
    else:
        termos = sorted(df_noticias["termo_busca"].dropna().unique().tolist())
        termos_selecionados = st.multiselect(
            "Filtrar por termo de busca", termos, default=termos, key="multiselect_termo_noticia",
        )
        df_noticias_filtrado = df_noticias[df_noticias["termo_busca"].isin(termos_selecionados)]
        st.dataframe(
            df_noticias_filtrado,
            width="stretch", height=350,
            column_config={"link": st.column_config.LinkColumn("Link")},
        )
        st.metric("Notícias exibidas", len(df_noticias_filtrado))

st.divider()
st.caption(
    "TP2 · Projeto de Bloco · PetVerde — Consumo Consciente no Mercado Pet · "
    "Uso de IA: assistido por Claude (Anthropic) na estruturação e implementação do código, "
    "conforme política de Sinal Verde do curso."
)
