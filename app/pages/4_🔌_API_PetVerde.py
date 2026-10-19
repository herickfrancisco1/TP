"""Página de integração: consome a API FastAPI do PetVerde (consultas GET e envio POST)."""

from __future__ import annotations

import json

import pandas as pd
import plotly.express as px
import streamlit as st

from comum import API_URL, aviso_api_offline, chamar_api

CATEGORIAS = ["Ração", "Petisco", "Higiene", "Acessório", "Brinquedo"]
EMBALAGENS = ["Plástico não reciclável", "Plástico reciclável", "Papel/Kraft", "Refil", "Vidro"]


def mostrar_requisicao(metodo: str, rota: str, parametros: dict | None = None, corpo: dict | None = None):
    """Mostra a chamada equivalente em curl, para documentar/ensinar o uso da API."""
    url = f"{API_URL}{rota}"
    if parametros:
        url += "?" + "&".join(f"{k}={v}" for k, v in parametros.items())
    comando = f'curl -X {metodo} "{url}"'
    if corpo:
        comando += f" -H \"Content-Type: application/json\" -d '{json.dumps(corpo, ensure_ascii=False)}'"
    st.code(comando, language="bash")


st.title("🔌 API PetVerde (FastAPI)")
st.caption(f"Esta página conversa com a API REST do projeto em `{API_URL}`. "
           f"Documentação interativa: [{API_URL}/docs]({API_URL}/docs)")

col_status, col_botao = st.columns([4, 1])
with col_botao:
    st.button("🔄 Testar conexão", width="stretch")
ok, saude, _ = chamar_api("GET", "/saude")
with col_status:
    if ok:
        arquivos = ", ".join(f"{nome} {'✅' if existe else '❌'}" for nome, existe in saude["arquivos"].items())
        st.success(f"API online · arquivos de dados: {arquivos}")
if not ok:
    aviso_api_offline()
    st.stop()

aba_get, aba_id, aba_post, aba_stats, aba_noticias = st.tabs([
    "GET /produtos", "GET /produtos/{id}", "POST /produtos", "GET /estatisticas", "GET /noticias",
])

# ---------------------------------------------------------------------------
with aba_get:
    st.markdown("Consulta produtos com filtros e paginação.")
    c1, c2, c3, c4 = st.columns(4)
    categoria = c1.selectbox("categoria", ["(todas)"] + CATEGORIAS)
    reciclavel = c2.selectbox("reciclavel", ["(todos)", "true", "false"])
    nota_min = c3.number_input("nota_min", 0.0, 10.0, 0.0, 0.5)
    limite = c4.number_input("limite", 1, 200, 10)
    busca = st.text_input("busca (trecho do nome)", "")

    parametros = {"nota_min": nota_min, "limite": int(limite)}
    if categoria != "(todas)":
        parametros["categoria"] = categoria
    if reciclavel != "(todos)":
        parametros["reciclavel"] = reciclavel
    if len(busca.strip()) >= 2:
        parametros["busca"] = busca.strip()

    mostrar_requisicao("GET", "/produtos", parametros)
    ok, corpo, codigo = chamar_api("GET", "/produtos", params=parametros)
    if ok:
        st.caption(f"HTTP {codigo} · {corpo['total_encontrado']} encontrados, {corpo['retornados']} retornados")
        st.dataframe(pd.DataFrame(corpo["produtos"]), width="stretch", hide_index=True)
    else:
        st.error(f"HTTP {codigo}: {corpo}")

# ---------------------------------------------------------------------------
with aba_id:
    id_produto = st.number_input("id_produto", min_value=1, value=1, step=1)
    mostrar_requisicao("GET", f"/produtos/{int(id_produto)}")
    ok, corpo, codigo = chamar_api("GET", f"/produtos/{int(id_produto)}")
    if ok:
        st.json(corpo)
    else:
        st.warning(f"HTTP {codigo}: {corpo.get('detail') if isinstance(corpo, dict) else corpo}")

# ---------------------------------------------------------------------------
with aba_post:
    st.markdown("Cadastra um novo produto. Se a nota não for informada, a API calcula: "
                "**5,0** + **2,5** (embalagem reciclável) + **1,5** (certificação) − até **2,5** "
                "conforme a pegada de carbono.")
    with st.form("form_novo_produto", clear_on_submit=False):
        f1, f2 = st.columns(2)
        nome = f1.text_input("Nome do produto *", placeholder="Ração Natural Refil 3kg")
        marca = f2.text_input("Marca *", placeholder="EcoBicho")
        f3, f4, f5 = st.columns(3)
        categoria_nova = f3.selectbox("Categoria *", CATEGORIAS)
        embalagem = f4.selectbox("Tipo de embalagem *", EMBALAGENS, index=3)
        certificacao = f5.text_input("Certificação", value="Nenhuma")
        f6, f7, f8 = st.columns(3)
        preco = f6.number_input("Preço (R$) *", min_value=0.01, value=89.90, step=1.0)
        carbono = f7.number_input("Pegada de carbono (kg CO₂) *", min_value=0.0, value=2.0, step=0.1)
        ods = f8.selectbox("ODS relacionado", ["ODS 12", "ODS 15", "ODS 12 e 15"])
        informar_nota = st.checkbox("Informar a nota manualmente")
        nota = st.slider("Nota de sustentabilidade", 0.0, 10.0, 7.0, 0.1, disabled=not informar_nota)
        enviado = st.form_submit_button("📤 Enviar produto (POST)", type="primary")

    if enviado:
        corpo_envio = {
            "nome_produto": nome, "categoria": categoria_nova, "marca": marca,
            "tipo_embalagem": embalagem, "certificacao": certificacao or "Nenhuma",
            "preco_reais": preco, "pegada_carbono_kgco2": carbono, "ods_relacionado": ods,
        }
        if informar_nota:
            corpo_envio["nota_sustentabilidade"] = nota
        mostrar_requisicao("POST", "/produtos", corpo=corpo_envio)
        ok, corpo, codigo = chamar_api("POST", "/produtos", json=corpo_envio)
        if ok:
            st.success(f"HTTP {codigo} · Produto cadastrado com id {corpo['id_produto']} "
                       f"e nota {corpo['nota_sustentabilidade']}.")
            st.json(corpo)
            st.caption("Ele já aparece em GET /produtos, nos indicadores e na página Produtos & Filtros "
                       "(opção “Incluir produtos cadastrados via API”).")
        else:
            st.error(f"HTTP {codigo} · A API recusou os dados:")
            st.json(corpo)

# ---------------------------------------------------------------------------
with aba_stats:
    mostrar_requisicao("GET", "/estatisticas")
    ok, corpo, codigo = chamar_api("GET", "/estatisticas")
    if ok:
        s1, s2, s3, s4 = st.columns(4)
        s1.metric("Produtos", corpo["total_produtos"])
        s2.metric("Enviados via API", corpo["enviados_via_api"])
        s3.metric("Nota média", corpo["nota_media"])
        s4.metric("% embalagem reciclável", corpo["pct_embalagem_reciclavel"])
        por_categoria = pd.DataFrame(corpo["por_categoria"])
        st.plotly_chart(
            px.bar(por_categoria, x="categoria", y="pct_reciclavel", text_auto=".1f",
                   title="% de embalagens recicláveis por categoria (dados vindos da API)",
                   labels={"pct_reciclavel": "% reciclável", "categoria": ""},
                   color_discrete_sequence=["#2E7D32"]),
            width="stretch",
        )
        st.dataframe(por_categoria, width="stretch", hide_index=True)
    else:
        st.error(f"HTTP {codigo}: {corpo}")

# ---------------------------------------------------------------------------
with aba_noticias:
    termo = st.selectbox("termo", ["(todos)", "consumo consciente pet", "sustentabilidade petshop",
                                   "abandono de animais adocao"])
    parametros = {"limite": 20}
    if termo != "(todos)":
        parametros["termo"] = termo
    mostrar_requisicao("GET", "/noticias", parametros)
    ok, corpo, codigo = chamar_api("GET", "/noticias", params=parametros)
    if ok:
        st.dataframe(pd.DataFrame(corpo["noticias"]), width="stretch", hide_index=True,
                     column_config={"link": st.column_config.LinkColumn("link"),
                                    "url_final": st.column_config.LinkColumn("url_final")})
    else:
        st.error(f"HTTP {codigo}: {corpo}")

st.divider()
st.caption("As rotas do corpus para LLM (`GET /corpus` e `GET /corpus/busca`) são usadas na página "
           "🤖 Preparação para LLMs. Documentação completa das rotas: `Code/Deployment/README.md`.")
