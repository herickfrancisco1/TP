# Painel de Turismo do Rio de Janeiro (TP3 - Streamlit)

Aplicação em Streamlit para explorar, filtrar, visualizar e exportar dados de
turismo do portal [Data.Rio - grupo Turismo](https://www.data.rio/search?groupIds=729990e9fbc04c6ebf81715ab438cae8).

## Objetivo e motivação

O turismo é um dos setores econômicos mais relevantes para a cidade do Rio de
Janeiro. O Data.Rio disponibiliza dezenas de planilhas históricas sobre chegada
de turistas, ocupação hoteleira e visitação a pontos turísticos, mas em um
formato bruto, pouco acessível a quem não programa. Este painel permite que
qualquer pessoa envie uma dessas planilhas (XLS/XLSX) e obtenha, em segundos,
filtros, tabelas interativas, gráficos e métricas — sem escrever código.

Datasets de referência usados como motivação (Data.Rio, categoria Turismo):

- Chegada mensal de turistas pelo Rio de Janeiro, por via Aérea, segundo
  continentes e países de residência permanente (2006-2019)
- Taxa de ocupação média anual e mensal dos hotéis no Município do Rio de
  Janeiro (1997-2017)
- Número total de visitantes por mês no Parque Nacional da Tijuca, segundo
  setores de controle (2007-2020)
- Número total de visitantes por dia na trilha do MoNa Pão de Açúcar
  (2017-2023)

## Funcionalidades

1. Upload de arquivo XLS/XLSX de turismo
2. Filtros por radio, checkbox e dropdown/multiselect
3. Tabela interativa (ordenável e pesquisável)
4. Download dos dados filtrados em XLSX
5. Barra de progresso e spinner durante o carregamento
6. Color picker para personalizar cores do painel
7. Cache dos dados carregados (`st.cache_data`)
8. Persistência de filtros e preferências via `st.session_state`
9. Gráficos simples: barras, linhas e pizza
10. Gráficos avançados: histograma e dispersão
11. Métricas-resumo: contagem, soma, média e máximo

## Como executar localmente

```bash
pip install -r requirements.txt
streamlit run app_tp3_herick_francisco.py
```

Se não tiver um arquivo à mão, use o dataset de exemplo (ilustrativo) marcando
a opção correspondente na barra lateral, ou baixe uma planilha real em
[data.rio](https://www.data.rio/search?groupIds=729990e9fbc04c6ebf81715ab438cae8).

## Autor

Herick Francisco

## Uso de IA

Este projeto foi desenvolvido com apoio de IA (Claude, da Anthropic) para
estruturação e implementação do código, conforme a política de Sinal Verde
do curso.
