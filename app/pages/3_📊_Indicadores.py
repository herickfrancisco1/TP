"""Página de indicadores: KPIs e gráficos de sustentabilidade (amostra e dados reais)."""

import plotly.express as px
import streamlit as st

from comum import carregar_csv, formatar_numero

st.title("📊 Indicadores de Sustentabilidade")
st.caption("Estatísticas geradas a partir dos dados coletados · ODS 12 (meta 12.5 — reduzir resíduos)")

aba_amostra, aba_reais = st.tabs(["🧪 Base de amostra (120 produtos)", "🌍 Produtos reais — Open Pet Food Facts"])

# ---------------------------------------------------------------------------
# Base de amostra
# ---------------------------------------------------------------------------
with aba_amostra:
    df = carregar_csv("produtos_tratados.csv")
    if df.empty:
        st.warning("Base de produtos não encontrada. Rode `python Code/DataPreparation/prepare_data.py`.")
    else:
        df["Embalagem"] = df["embalagem_reciclavel"].map({True: "Reciclável", False: "Não reciclável"})
        categorias = st.multiselect("Categorias", sorted(df["categoria"].unique()),
                                    default=sorted(df["categoria"].unique()), key="ind_cat")
        dfc = df[df["categoria"].isin(categorias)]

        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Produtos", len(dfc))
        k2.metric("Nota média de sustentabilidade", formatar_numero(dfc["nota_sustentabilidade"].mean(), 2))
        k3.metric("Embalagem reciclável", f"{formatar_numero(dfc['embalagem_reciclavel'].mean() * 100, 1)}%")
        k4.metric("Pegada de carbono média", f"{formatar_numero(dfc['pegada_carbono_kgco2'].mean(), 2)} kg CO₂")

        if dfc.empty:
            st.info("Selecione ao menos uma categoria.")
        else:
            g1, g2 = st.columns(2)
            with g1:
                por_categoria = (dfc.groupby("categoria", as_index=False)["nota_sustentabilidade"].mean()
                                 .sort_values("nota_sustentabilidade"))
                st.plotly_chart(
                    px.bar(por_categoria, x="nota_sustentabilidade", y="categoria", orientation="h",
                           title="Nota média por categoria", text_auto=".2f",
                           labels={"nota_sustentabilidade": "Nota média (0–10)", "categoria": ""},
                           color_discrete_sequence=["#2E7D32"]),
                    width="stretch",
                )
            with g2:
                por_embalagem = dfc["tipo_embalagem"].value_counts().reset_index()
                por_embalagem.columns = ["tipo_embalagem", "produtos"]
                st.plotly_chart(
                    px.pie(por_embalagem, names="tipo_embalagem", values="produtos", hole=0.45,
                           title="Distribuição por tipo de embalagem"),
                    width="stretch",
                )

            st.plotly_chart(
                px.scatter(dfc, x="preco_reais", y="nota_sustentabilidade", color="Embalagem",
                           hover_name="nome_produto", size="pegada_carbono_kgco2",
                           title="Preço × nota de sustentabilidade (tamanho = pegada de carbono)",
                           labels={"preco_reais": "Preço (R$)", "nota_sustentabilidade": "Nota (0–10)"},
                           color_discrete_map={"Reciclável": "#2E7D32", "Não reciclável": "#C62828"}),
                width="stretch",
            )
            correlacao = dfc["preco_reais"].corr(dfc["nota_sustentabilidade"])
            st.caption(f"Correlação entre preço e nota: **{formatar_numero(correlacao, 2)}** — "
                       "valores próximos de zero indicam que produto sustentável não é, "
                       "necessariamente, mais caro nesta amostra.")

            st.markdown("**Top 5 produtos mais sustentáveis por categoria**")
            top = (dfc.sort_values("nota_sustentabilidade", ascending=False)
                   .groupby("categoria").head(5)
                   [["categoria", "nome_produto", "tipo_embalagem", "certificacao",
                     "nota_sustentabilidade", "preco_reais"]])
            st.dataframe(top, width="stretch", hide_index=True, height=300)

# ---------------------------------------------------------------------------
# Dados reais do Open Pet Food Facts
# ---------------------------------------------------------------------------
with aba_reais:
    reais = carregar_csv("produtos_reais_opff.csv")
    if reais.empty:
        st.info("Ainda não há produtos reais coletados. Rode, a partir da raiz do projeto:")
        st.code("python Code/DataAcquisition/coletar_openpetfoodfacts.py\n"
                "python Code/DataPreparation/prepare_data.py", language="bash")
    else:
        r1, r2, r3, r4 = st.columns(4)
        r1.metric("Produtos reais", len(reais))
        r2.metric("Vendidos no Brasil", int(reais["vendido_no_brasil"].astype(str).str.lower().eq("true").sum()))
        marcas_validas = reais["marcas"].dropna().astype(str).str.strip()
        marcas_validas = marcas_validas[marcas_validas != ""]
        r3.metric("Marcas", marcas_validas.nunique())
        com_info = reais[reais["embalagem_reciclavel"] != "Sem informação"]
        r4.metric("Com informação de embalagem", f"{formatar_numero(len(com_info) / len(reais) * 100, 0)}%")

        g1, g2 = st.columns(2)
        with g1:
            contagem = reais.groupby(["especie", "embalagem_reciclavel"]).size().reset_index(name="produtos")
            st.plotly_chart(
                px.bar(contagem, x="especie", y="produtos", color="embalagem_reciclavel", barmode="group",
                       title="Embalagem reciclável por espécie",
                       labels={"especie": "", "embalagem_reciclavel": "Reciclável?"},
                       color_discrete_map={"Sim": "#2E7D32", "Não": "#C62828", "Sem informação": "#9E9E9E"}),
                width="stretch",
            )
        with g2:
            marcas = (marcas_validas.str.split(",").str[0].str.strip()
                      .value_counts().head(10).reset_index())
            marcas.columns = ["marca", "produtos"]
            st.plotly_chart(
                px.bar(marcas.sort_values("produtos"), x="produtos", y="marca", orientation="h",
                       title="Marcas com mais produtos cadastrados", labels={"marca": ""},
                       color_discrete_sequence=["#1565C0"]),
                width="stretch",
            )

        st.caption("A ausência de informação de embalagem em parte dos produtos também é um achado: "
                   "reforça a meta 12.8 do ODS 12 (acesso à informação para consumo sustentável).")
        st.dataframe(reais, width="stretch", height=320,
                     column_config={"url": st.column_config.LinkColumn("Página no OPFF")})
