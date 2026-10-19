"""
PetVerde - Ponto de entrada da aplicação Streamlit (TP3).

Define o menu de navegação com várias páginas (st.navigation), agrupadas em
seções. Cada página fica em um arquivo próprio dentro de app/pages/.

Executar a partir da raiz do repositório:
    streamlit run app/app.py
"""

import streamlit as st

AGENDA_2030_URL = "https://brasil.un.org/pt-br/sdgs"
OPEN_PET_FOOD_FACTS_URL = "https://world.openpetfoodfacts.org/"
REPOSITORIO_URL = "https://github.com/herickfrancisco1/TP"

st.set_page_config(
    page_title="PetVerde - Consumo Consciente no Mercado Pet",
    page_icon="🐾",
    layout="wide",
    initial_sidebar_state="expanded",
)

paginas = {
    "Visão geral": [
        st.Page("pages/0_🏠_Inicio.py", title="Início", icon="🏠", default=True),
    ],
    "Análises": [
        st.Page("pages/1_🛒_Produtos_e_Filtros.py", title="Produtos & Filtros", icon="🛒",
                url_path="produtos"),
        st.Page("pages/3_📊_Indicadores.py", title="Indicadores de Sustentabilidade", icon="📊",
                url_path="indicadores"),
        st.Page("pages/2_📰_Noticias_e_NLP.py", title="Notícias & NLP", icon="📰",
                url_path="noticias"),
    ],
    "Integrações": [
        st.Page("pages/4_🔌_API_PetVerde.py", title="API PetVerde (FastAPI)", icon="🔌",
                url_path="api"),
    ],
    "Inteligência Artificial": [
        st.Page("pages/5_🤖_Preparacao_IA.py", title="Preparação para LLMs", icon="🤖",
                url_path="ia"),
    ],
}

navegacao = st.navigation(paginas)

with st.sidebar:
    st.caption("🐾 **PetVerde** · TP3 · Projeto de Bloco")
    st.caption(f"[Agenda 2030 - ODS]({AGENDA_2030_URL}) · "
               f"[Open Pet Food Facts]({OPEN_PET_FOOD_FACTS_URL}) · "
               f"[Repositório]({REPOSITORIO_URL})")

navegacao.run()
