"""Página de preparação para IA: corpus para LLMs, busca de contexto e prompts prontos."""

import json

import pandas as pd
import plotly.express as px
import streamlit as st

from comum import carregar_corpus, chamar_api  # importar primeiro: ajusta o sys.path

import dados_petverde  # noqa: E402  (Code/Deployment)
import prompts  # noqa: E402  (Code/Modeling)

st.title("🤖 Preparação para LLMs")
st.caption("Os dados coletados já estão organizados para a próxima etapa (TP4), em que um LLM "
           "fará resumos, classificação de sentimento, perguntas e respostas e relatórios.")

corpus = carregar_corpus()
if corpus.empty:
    st.warning("Corpus não encontrado. Rode `python Code/Modeling/preparar_corpus_llm.py`.")
    st.stop()

# ---------------------------------------------------------------------------
st.subheader("📚 Corpus de textos (Data/Processed/corpus_llm.jsonl)")
resumo = corpus.groupby("fonte").agg(trechos=("id", "count"), tokens_estimados=("n_tokens_estimado", "sum"),
                                     tarefa_sugerida=("tarefa_sugerida", "first")).reset_index()
c1, c2, c3 = st.columns(3)
c1.metric("Trechos", len(corpus))
c2.metric("Tokens estimados (total)", f"{int(corpus['n_tokens_estimado'].sum()):,}".replace(",", "."))
c3.metric("Maior trecho (tokens)", int(corpus["n_tokens_estimado"].max()))

g1, g2 = st.columns([1, 1])
with g1:
    st.dataframe(resumo, width="stretch", hide_index=True)
    st.caption("Tokens estimados com a regra prática de ~4 caracteres por token. Todos os trechos cabem "
               "com folga na janela de contexto dos LLMs atuais, o que permite enviar vários de uma vez.")
with g2:
    st.plotly_chart(px.histogram(corpus, x="n_tokens_estimado", color="fonte", nbins=30,
                                 title="Tamanho dos trechos (tokens estimados)",
                                 labels={"n_tokens_estimado": "tokens"}), width="stretch")

with st.expander("Ver trechos do corpus"):
    fonte_sel = st.multiselect("Fonte", sorted(corpus["fonte"].unique()), default=sorted(corpus["fonte"].unique()))
    st.dataframe(corpus[corpus["fonte"].isin(fonte_sel)][["id", "fonte", "titulo", "texto", "n_tokens_estimado"]],
                 width="stretch", hide_index=True, height=300)

# ---------------------------------------------------------------------------
st.divider()
st.subheader("🧭 Como cada dado será usado com LLMs")
st.markdown(
    """
| Tarefa (TP4) | Dados de entrada | Valor para o negócio |
|---|---|---|
| **Resumo automático** | Artigos da Wikipedia (consumo sustentável, abandono de animais) | Explicar o tema em poucas linhas para tutores e petshops |
| **Classificação de sentimento** | Notícias (título + descrição coletada via Selenium) | Acompanhar se a cobertura sobre bem-estar animal e sustentabilidade pet é positiva ou negativa |
| **Perguntas e respostas (RAG)** | Corpus inteiro, com busca dos trechos mais relevantes | Responder dúvidas do usuário citando a fonte |
| **Geração de relatório** | Indicadores da API (`GET /estatisticas`) e fichas dos produtos | Relatório automático de sustentabilidade para o gestor do petshop |
    """
)

# ---------------------------------------------------------------------------
st.divider()
st.subheader("🧪 Laboratório de prompts")
st.caption("Monta o prompt exatamente como será enviado ao LLM na próxima etapa. "
           "Nesta entrega nenhum modelo é chamado: o objetivo é validar dados e instruções.")

tarefa = st.radio("Tarefa", list(prompts.TEMPLATES), horizontal=True,
                  format_func=lambda t: prompts.TEMPLATES[t]["nome"])
st.caption(prompts.TEMPLATES[tarefa]["descricao"])

prompt = ""
if tarefa == "resumo":
    wiki = corpus[corpus["fonte"] == "wikipedia"]
    trecho_id = st.selectbox("Trecho", wiki["id"], format_func=lambda i: f"{i} — {wiki.set_index('id').loc[i, 'titulo']}")
    n_topicos = st.slider("Número de tópicos", 3, 7, 5)
    prompt = prompts.montar_prompt("resumo", n_topicos=n_topicos,
                                   texto=wiki.set_index("id").loc[trecho_id, "texto"])

elif tarefa == "sentimento":
    noticias = corpus[corpus["fonte"] == "noticias"]
    noticia_id = st.selectbox("Notícia", noticias["id"],
                              format_func=lambda i: noticias.set_index("id").loc[i, "titulo"][:100])
    prompt = prompts.montar_prompt("sentimento", texto=noticias.set_index("id").loc[noticia_id, "texto"])
    st.caption("Uma amostra dessas notícias pode ser rotulada à mão em "
               "`Data/Processed/noticias_para_sentimento.csv` para medir a acurácia do LLM no TP4.")

elif tarefa == "perguntas_respostas":
    pergunta = st.text_input("Pergunta", "Qual é o problema do abandono de animais no Brasil?")
    k = st.slider("Trechos de contexto (k)", 1, 6, 3)
    ok, corpo, _ = chamar_api("GET", "/corpus/busca", params={"q": pergunta, "k": k})
    if ok:
        trechos = corpo["trechos"]
        st.caption("Trechos recuperados pela API (`GET /corpus/busca`).")
    else:
        trechos = dados_petverde.buscar_trechos(pergunta, k)
        st.caption("API desligada — trechos recuperados localmente com a mesma função da API.")
    if trechos:
        st.dataframe(pd.DataFrame(trechos)[["id", "fonte", "pontuacao", "texto"]], width="stretch", hide_index=True)
        prompt = prompts.montar_prompt("perguntas_respostas", pergunta=pergunta,
                                       contexto=prompts.formatar_contexto(trechos))
    else:
        st.info("Nenhum trecho relevante encontrado para essa pergunta.")

elif tarefa == "relatorio":
    ok, indicadores, _ = chamar_api("GET", "/estatisticas")
    if not ok:
        indicadores = dados_petverde.estatisticas_produtos()
    prompt = prompts.montar_prompt("relatorio",
                                   indicadores_json=json.dumps(indicadores, ensure_ascii=False, indent=2))

if prompt:
    st.markdown("**Instrução de sistema**")
    st.code(prompts.INSTRUCAO_SISTEMA, language=None, wrap_lines=True)
    st.markdown(f"**Prompt do usuário** (~{max(1, len(prompt) // 4)} tokens)")
    st.code(prompt, language=None, wrap_lines=True)
