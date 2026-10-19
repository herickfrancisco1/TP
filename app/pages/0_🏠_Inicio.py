"""Página inicial: problema de negócio, ODS e mapa das funcionalidades do app."""

import streamlit as st

from comum import api_disponivel, carregar_corpus, carregar_csv, carregar_noticias

st.title("🐾 PetVerde — Consumo Consciente no Mercado Pet")
st.caption("Dashboard de dados a serviço de um petshop sustentável · ODS 12 (primário) e ODS 15 "
           "(secundário) · Agenda 2030")

st.header("Problema de negócio")
st.markdown(
    """
O mercado pet brasileiro cresce rapidamente, mas carrega custos socioambientais pouco
visíveis ao consumidor final: embalagens plásticas não recicláveis, alta pegada de carbono
na cadeia produtiva de ração e uma das maiores populações de animais abandonados do mundo.

**Pergunta de negócio:** como ajudar tutores de pets e pequenos petshops a tomar decisões de
compra e de gestão mais sustentáveis, usando dados públicos sobre produtos, abandono/adoção
de animais e boas práticas ESG do setor?
    """
)

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

st.header("Dados disponíveis")
produtos = carregar_csv("produtos_tratados.csv")
reais = carregar_csv("produtos_reais_opff.csv")
noticias = carregar_noticias()
corpus = carregar_corpus()

m1, m2, m3, m4 = st.columns(4)
m1.metric("Produtos (amostra)", len(produtos))
m2.metric("Produtos reais (Open Pet Food Facts)", len(reais) if not reais.empty else "—")
m3.metric("Notícias coletadas", len(noticias))
m4.metric("Trechos no corpus para LLM", len(corpus))

st.header("O que há em cada página")
st.markdown(
    """
| Página | O que faz |
|---|---|
| 🛒 **Produtos & Filtros** | Tabela de produtos com filtros, upload de CSV, download (CSV/XLSX) e gráficos |
| 📊 **Indicadores de Sustentabilidade** | KPIs e gráficos da base de amostra e dos produtos reais do Open Pet Food Facts |
| 📰 **Notícias & NLP** | Nuvem de palavras, estatísticas de texto e notícias (com descrição coletada via Selenium) |
| 🔌 **API PetVerde (FastAPI)** | Consulta (GET) e cadastro (POST) de dados através da API REST do projeto |
| 🤖 **Preparação para LLMs** | Corpus de textos fatiado, busca de contexto e prompts prontos para a próxima etapa |
    """
)

st.divider()
if api_disponivel():
    st.success("🔌 API PetVerde conectada.")
else:
    st.warning("🔌 API PetVerde desligada — a página **API PetVerde** explica como iniciá-la. "
               "As demais páginas funcionam sem ela.")
st.info("👈 Use o **menu lateral** para navegar entre as páginas.")
