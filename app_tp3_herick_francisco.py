"""
TP3 - Streamlit: Painel de Turismo do Rio de Janeiro
Autor: Herick Francisco
Fonte dos dados: Data.Rio - grupo "Turismo"
https://www.data.rio/search?groupIds=729990e9fbc04c6ebf81715ab438cae8
"""

import io
import time

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

DATARIO_TURISMO_URL = "https://www.data.rio/search?groupIds=729990e9fbc04c6ebf81715ab438cae8"

DATASETS_REFERENCIA = [
    ("Chegada mensal de turistas pelo Rio de Janeiro, por via Aérea, "
     "segundo continentes e países de residência permanente (2006-2019)"),
    "Taxa de ocupação média anual e mensal dos hotéis no Município do Rio de Janeiro (1997-2017)",
    "Número total de visitantes por mês no Parque Nacional da Tijuca, segundo setores de controle (2007-2020)",
    "Número total de visitantes por dia na trilha do Monumento Natural - MoNa Pão de Açúcar (2017-2023)",
]

st.set_page_config(
    page_title="Painel de Turismo - Rio de Janeiro",
    page_icon="🌆",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Item 9: Session State - valores padrão que persistem durante a navegação
# ---------------------------------------------------------------------------
_DEFAULTS = {
    "cor_fundo": "#0E1117",
    "cor_fonte": "#FAFAFA",
    "df_atual": None,
    "nome_arquivo": None,
    "colunas_marcadas": None,
}
for chave, valor in _DEFAULTS.items():
    if chave not in st.session_state:
        st.session_state[chave] = valor


# ---------------------------------------------------------------------------
# Item 8: Cache - evita reprocessar o XLS a cada interação do usuário
# ---------------------------------------------------------------------------
def _localizar_linha_cabecalho(bruto: pd.DataFrame, limite: int = 15) -> int:
    """Planilhas do Data.Rio costumam ter títulos/notas antes do cabeçalho real."""
    melhor_linha, melhor_pontuacao = 0, -1
    for i in range(min(limite, len(bruto))):
        linha = bruto.iloc[i]
        pontuacao = linha.notna().sum() + linha.apply(lambda v: isinstance(v, str)).sum()
        if linha.notna().sum() >= 2 and pontuacao > melhor_pontuacao:
            melhor_linha, melhor_pontuacao = i, pontuacao
    return melhor_linha


@st.cache_data(show_spinner=False)
def carregar_planilha(conteudo: bytes, nome_arquivo: str) -> pd.DataFrame:
    engine = "openpyxl" if nome_arquivo.lower().endswith("xlsx") else "xlrd"
    bruto = pd.read_excel(io.BytesIO(conteudo), header=None, engine=engine)
    linha_cabecalho = _localizar_linha_cabecalho(bruto)
    df = pd.read_excel(io.BytesIO(conteudo), header=linha_cabecalho, engine=engine)
    df = df.dropna(axis=1, how="all").dropna(axis=0, how="all")
    df.columns = [str(c).strip() for c in df.columns]
    return df.reset_index(drop=True)


@st.cache_data(show_spinner=False)
def gerar_dataset_exemplo() -> pd.DataFrame:
    """Dataset ilustrativo (dados sintéticos), com a mesma estrutura das
    tabelas de turismo do Data.Rio: ano, mês, origem do turista e volume."""
    rng = np.random.default_rng(42)
    anos = list(range(2016, 2025))
    meses = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho",
             "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
    origens = {
        "América do Sul": ["Argentina", "Chile", "Uruguai", "Paraguai"],
        "América do Norte": ["Estados Unidos", "Canadá", "México"],
        "Europa": ["Portugal", "Alemanha", "França", "Espanha", "Itália"],
        "Ásia": ["China", "Japão", "Coreia do Sul"],
    }
    alta_temporada = {"Dezembro", "Janeiro", "Fevereiro", "Março", "Julho"}
    linhas = []
    for ano in anos:
        for mes in meses:
            fator_sazonal = 1.6 if mes in alta_temporada else 1.0
            for continente, paises in origens.items():
                for pais in paises:
                    base = rng.integers(800, 6000)
                    tendencia = 1 + 0.03 * (ano - anos[0])
                    turistas = int(base * fator_sazonal * tendencia)
                    gasto_medio = round(rng.uniform(120, 480), 2)
                    linhas.append((ano, mes, continente, pais, turistas, gasto_medio))
    df = pd.DataFrame(
        linhas,
        columns=["Ano", "Mês", "Continente", "País", "Número de Turistas", "Gasto Médio Diário (R$)"],
    )
    return df


def converter_para_xlsx(df: pd.DataFrame) -> bytes:
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="dados_filtrados")
    return buffer.getvalue()


# ---------------------------------------------------------------------------
# Item 7: Color Picker - personalização de cores (persistido no Session State)
# ---------------------------------------------------------------------------
with st.sidebar:
    st.title("🌆 Painel de Turismo - RJ")
    st.caption("TP3 · Streamlit · Dados do Data.Rio")

    st.subheader("🎨 Aparência")
    st.session_state["cor_fundo"] = st.color_picker(
        "Cor de fundo do painel", st.session_state["cor_fundo"], key="picker_fundo"
    )
    st.session_state["cor_fonte"] = st.color_picker(
        "Cor da fonte", st.session_state["cor_fonte"], key="picker_fonte"
    )

    st.divider()
    st.subheader("📂 Dados")
    arquivo_subido = st.file_uploader(
        "Envie um XLS/XLSX de turismo do Data.Rio", type=["xls", "xlsx"], key="uploader_xls"
    )
    usar_exemplo = st.checkbox(
        "Usar dataset de exemplo (ilustrativo)", value=(arquivo_subido is None), key="chk_exemplo"
    )
    st.caption(f"Fonte oficial: [Data.Rio - Turismo]({DATARIO_TURISMO_URL})")

    if st.button("🔄 Resetar filtros e preferências", width="stretch"):
        for chave in list(st.session_state.keys()):
            if chave not in ("uploader_xls",):
                del st.session_state[chave]
        st.rerun()

cor_fundo = st.session_state["cor_fundo"]
cor_fonte = st.session_state["cor_fonte"]
st.markdown(
    f"""
    <style>
    .stApp {{ background-color: {cor_fundo}; }}
    .stApp, .stApp p, .stApp span, .stApp li, .stApp label,
    .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5,
    .stApp .stMarkdown, .stApp .stCaption {{ color: {cor_fonte}; }}
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("🌆 Painel Interativo de Turismo - Rio de Janeiro")
st.caption("Explore, filtre e visualize dados de turismo do portal Data.Rio.")

aba_sobre, aba_dados, aba_graficos, aba_avancado = st.tabs(
    ["ℹ️ Sobre o Projeto", "📋 Dados & Filtros", "📊 Gráficos", "🔬 Análise Avançada"]
)

# ---------------------------------------------------------------------------
# Item 1: Datasets, objetivo e motivação
# ---------------------------------------------------------------------------
with aba_sobre:
    st.header("Objetivo e motivação")
    st.markdown(
        f"""
O turismo é um dos setores econômicos mais relevantes para a cidade do Rio de Janeiro,
gerando emprego, renda e projeção internacional. A Prefeitura, por meio do
**[Data.Rio - grupo Turismo]({DATARIO_TURISMO_URL})**, disponibiliza dezenas de planilhas
históricas sobre chegada de turistas, ocupação hoteleira, visitação a pontos turísticos
(Cristo Redentor, Pão de Açúcar, Parque Nacional da Tijuca) e perfil do visitante.

**Objetivo deste painel:** oferecer uma interface simples, sem necessidade de programação,
para que qualquer pessoa (gestor público, pesquisador, estudante ou empresa do setor) possa
enviar uma dessas planilhas e obter, em segundos, filtros, tabelas interativas, gráficos e
métricas que ajudem a identificar sazonalidade, tendências de crescimento/queda e diferenças
entre origens de turistas ou pontos de visitação.

**Datasets de referência utilizados como motivação** (todos do Data.Rio, categoria Turismo):
"""
    )
    for nome in DATASETS_REFERENCIA:
        st.markdown(f"- {nome}")

    st.markdown(
        """
**Funcionalidades implementadas neste painel:**
1. Upload de arquivo XLS/XLSX de turismo;
2. Filtros por radio button, checkbox e dropdown/multiselect;
3. Tabela interativa (ordenável e pesquisável) com os dados filtrados;
4. Download dos dados filtrados em XLSX;
5. Barra de progresso e spinner durante o carregamento;
6. Personalização de cores (color picker) do painel;
7. Cache dos dados carregados e persistência de preferências via Session State;
8. Gráficos simples (barras, linhas, pizza) e avançados (histograma, dispersão);
9. Métricas-resumo (contagem, soma, média) dos dados carregados.
        """
    )
    st.info(
        "Nenhum arquivo em mãos? Marque **'Usar dataset de exemplo'** na barra lateral "
        "para explorar o painel com dados ilustrativos, ou baixe uma planilha real "
        f"em [data.rio]({DATARIO_TURISMO_URL})."
    )

# ---------------------------------------------------------------------------
# Item 2 e 6: Upload + Spinner/Progress bar
# ---------------------------------------------------------------------------
df_bruto = None
if arquivo_subido is not None:
    etapas = st.progress(0, text="Iniciando processamento do arquivo...")
    with st.spinner("Lendo e limpando a planilha..."):
        etapas.progress(25, text="Lendo bytes do arquivo...")
        time.sleep(0.2)
        conteudo = arquivo_subido.getvalue()
        etapas.progress(55, text="Detectando cabeçalho e convertendo em tabela...")
        df_bruto = carregar_planilha(conteudo, arquivo_subido.name)
        etapas.progress(85, text="Finalizando limpeza dos dados...")
        time.sleep(0.2)
        etapas.progress(100, text="Concluído!")
    time.sleep(0.3)
    etapas.empty()
    st.session_state["nome_arquivo"] = arquivo_subido.name
elif usar_exemplo:
    with st.spinner("Gerando dataset de exemplo..."):
        df_bruto = gerar_dataset_exemplo()
        time.sleep(0.3)
    st.session_state["nome_arquivo"] = "dataset_exemplo.xlsx"

if df_bruto is not None:
    st.session_state["df_atual"] = df_bruto

df = st.session_state["df_atual"]

if df is None:
    st.warning("Envie um arquivo XLS/XLSX na barra lateral ou marque 'Usar dataset de exemplo' para começar.")
    st.stop()

colunas_numericas = df.select_dtypes(include=np.number).columns.tolist()
colunas_categoricas = [c for c in df.columns if c not in colunas_numericas]

# ---------------------------------------------------------------------------
# Item 3: Filtros - radio, checkbox e dropdown/multiselect
# ---------------------------------------------------------------------------
with aba_dados:
    st.subheader(f"Dataset carregado: `{st.session_state['nome_arquivo']}`")
    st.caption(f"{df.shape[0]} linhas × {df.shape[1]} colunas")
    st.dataframe(df, width="stretch", height=220)

    st.divider()
    st.subheader("🔍 Filtros e seleção")

    col_a, col_b, col_c = st.columns(3)

    with col_a:
        st.markdown("**Colunas a exibir (checkbox)**")
        if st.session_state.get("colunas_marcadas") is None:
            st.session_state["colunas_marcadas"] = {c: True for c in df.columns}
        colunas_selecionadas = []
        for coluna in df.columns:
            marcado = st.checkbox(
                coluna,
                value=st.session_state["colunas_marcadas"].get(coluna, True),
                key=f"chk_col_{coluna}",
            )
            st.session_state["colunas_marcadas"][coluna] = marcado
            if marcado:
                colunas_selecionadas.append(coluna)
        if not colunas_selecionadas:
            colunas_selecionadas = list(df.columns)

    with col_b:
        st.markdown("**Coluna categórica para filtrar (dropdown)**")
        if colunas_categoricas:
            coluna_filtro = st.selectbox(
                "Filtrar por coluna", colunas_categoricas, key="select_coluna_filtro"
            )
            valores_disponiveis = sorted(df[coluna_filtro].dropna().unique().tolist(), key=str)
            valores_selecionados = st.multiselect(
                f"Valores de '{coluna_filtro}'",
                valores_disponiveis,
                default=valores_disponiveis,
                key="multiselect_valores",
            )
        else:
            coluna_filtro, valores_selecionados = None, None
            st.caption("Nenhuma coluna categórica encontrada neste dataset.")

    with col_c:
        st.markdown("**Ordenação da tabela (radio)**")
        ordem = st.radio("Direção", ["Crescente", "Decrescente"], horizontal=True, key="radio_ordem")
        coluna_para_ordenar = st.selectbox(
            "Ordenar por", df.columns.tolist(), key="select_ordenar_por"
        )

    df_filtrado = df.copy()
    if coluna_filtro and valores_selecionados is not None:
        df_filtrado = df_filtrado[df_filtrado[coluna_filtro].isin(valores_selecionados)]
    df_filtrado = df_filtrado[colunas_selecionadas]
    if coluna_para_ordenar in df_filtrado.columns:
        df_filtrado = df_filtrado.sort_values(
            coluna_para_ordenar, ascending=(ordem == "Crescente")
        )

    if colunas_numericas:
        st.markdown("**Faixa numérica (slider)**")
        metrica_faixa = st.selectbox(
            "Métrica para filtrar por faixa de valores", colunas_numericas, key="select_metrica_faixa"
        )
        minimo, maximo = float(df[metrica_faixa].min()), float(df[metrica_faixa].max())
        if minimo < maximo and metrica_faixa in df_filtrado.columns:
            faixa = st.slider(
                f"Intervalo de '{metrica_faixa}'", minimo, maximo, (minimo, maximo), key="slider_faixa"
            )
            df_filtrado = df_filtrado[df_filtrado[metrica_faixa].between(*faixa)]

    # -----------------------------------------------------------------
    # Item 4: Tabela interativa
    # -----------------------------------------------------------------
    st.divider()
    st.subheader("📋 Tabela filtrada")
    st.caption("Clique no cabeçalho de uma coluna para ordenar ou use o ícone de busca da tabela para filtrar.")
    st.dataframe(df_filtrado, width="stretch", height=320)

    # -----------------------------------------------------------------
    # Item 5: Download dos dados filtrados
    # -----------------------------------------------------------------
    st.download_button(
        "⬇️ Baixar dados filtrados (XLSX)",
        data=converter_para_xlsx(df_filtrado),
        file_name="turismo_rio_filtrado.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        width="stretch",
    )

# ---------------------------------------------------------------------------
# Item 12: Métricas básicas
# ---------------------------------------------------------------------------
def exibir_metricas(dados: pd.DataFrame, metrica_principal: str | None):
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Registros", f"{len(dados):,}".replace(",", "."))
    if metrica_principal:
        m2.metric(f"Soma de {metrica_principal}", f"{dados[metrica_principal].sum():,.0f}".replace(",", "."))
        m3.metric(f"Média de {metrica_principal}", f"{dados[metrica_principal].mean():,.1f}".replace(",", "."))
        m4.metric(f"Máximo de {metrica_principal}", f"{dados[metrica_principal].max():,.0f}".replace(",", "."))
    else:
        m2.metric("Colunas numéricas", "0")


def _parece_coluna_de_ano(nome_coluna: str) -> bool:
    nome = nome_coluna.strip().lower()
    return "ano" in nome or nome == "year"


# ---------------------------------------------------------------------------
# Item 10: Gráficos simples (barras, linhas, pizza)
# ---------------------------------------------------------------------------
with aba_graficos:
    st.subheader("📊 Métricas do recorte filtrado")
    metricas_candidatas = [c for c in colunas_numericas if not _parece_coluna_de_ano(c)] or colunas_numericas
    metrica_resumo = None
    if metricas_candidatas:
        metrica_resumo = st.selectbox(
            "Métrica para o resumo abaixo", metricas_candidatas, key="select_metrica_resumo"
        )
    exibir_metricas(df_filtrado, metrica_resumo)

    st.divider()
    if not colunas_numericas or not colunas_categoricas:
        st.warning("São necessárias ao menos uma coluna numérica e uma categórica para gerar estes gráficos.")
    else:
        col_x, col_y = st.columns(2)
        with col_x:
            eixo_categorico = st.selectbox("Categoria (eixo X)", colunas_categoricas, key="select_cat_simples")
        with col_y:
            metrica_simples = st.selectbox("Métrica (valor)", metricas_candidatas, key="select_metrica_simples")

        resumo = (
            df_filtrado.groupby(eixo_categorico, as_index=False)[metrica_simples]
            .sum()
            .sort_values(metrica_simples, ascending=False)
        )

        tab_barras, tab_linhas, tab_pizza = st.tabs(["Barras", "Linhas", "Pizza"])
        with tab_barras:
            fig_barras = px.bar(resumo, x=eixo_categorico, y=metrica_simples,
                                 color=eixo_categorico, title=f"{metrica_simples} por {eixo_categorico}")
            st.plotly_chart(fig_barras, width="stretch")
        with tab_linhas:
            fig_linhas = px.line(resumo, x=eixo_categorico, y=metrica_simples, markers=True,
                                  title=f"Tendência de {metrica_simples} por {eixo_categorico}")
            st.plotly_chart(fig_linhas, width="stretch")
        with tab_pizza:
            fig_pizza = px.pie(resumo, names=eixo_categorico, values=metrica_simples,
                                title=f"Participação de {eixo_categorico} em {metrica_simples}")
            st.plotly_chart(fig_pizza, width="stretch")

# ---------------------------------------------------------------------------
# Item 11: Gráficos avançados (histograma e dispersão)
# ---------------------------------------------------------------------------
with aba_avancado:
    st.subheader("🔬 Visualizações avançadas")
    if not colunas_numericas:
        st.warning("São necessárias colunas numéricas para gerar histograma e dispersão.")
    else:
        col_h, col_s = st.columns(2)
        with col_h:
            st.markdown("**Histograma**")
            metrica_hist = st.selectbox("Métrica", metricas_candidatas, key="select_metrica_hist")
            n_bins = st.slider("Número de faixas (bins)", 5, 60, 20, key="slider_bins")
            fig_hist = px.histogram(df_filtrado, x=metrica_hist, nbins=n_bins,
                                     title=f"Distribuição de {metrica_hist}")
            st.plotly_chart(fig_hist, width="stretch")

        with col_s:
            st.markdown("**Dispersão (scatter)**")
            if len(colunas_numericas) >= 2:
                eixo_x = st.selectbox("Eixo X", colunas_numericas, index=0, key="select_scatter_x")
                eixo_y = st.selectbox("Eixo Y", colunas_numericas, index=min(1, len(colunas_numericas) - 1), key="select_scatter_y")
                cor_scatter = st.selectbox(
                    "Colorir por", ["(nenhuma)"] + colunas_categoricas, key="select_scatter_cor"
                )
                fig_scatter = px.scatter(
                    df_filtrado, x=eixo_x, y=eixo_y,
                    color=None if cor_scatter == "(nenhuma)" else cor_scatter,
                    title=f"{eixo_y} vs. {eixo_x}",
                )
            else:
                st.caption("Apenas uma coluna numérica disponível: dispersão feita contra o índice das linhas.")
                fig_scatter = px.scatter(
                    df_filtrado.reset_index(), x="index", y=colunas_numericas[0],
                    title=f"{colunas_numericas[0]} por linha",
                )
            st.plotly_chart(fig_scatter, width="stretch")

st.divider()
st.caption(
    "TP3 · Desenvolvimento de Aplicações com Streamlit · Dados: Data.Rio (Prefeitura do Rio de Janeiro) · "
    "Uso de IA: assistido por Claude (Anthropic) na estruturação e implementação do código, conforme "
    "política de Sinal Verde do curso."
)
