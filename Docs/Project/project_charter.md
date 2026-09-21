# Project Charter — PetVerde: Consumo Consciente para o Mercado Pet

**Autor:** Herick Francisco
**Etapa:** TP2 · Projeto de Bloco (PB)
**Repositório:** https://github.com/herickfrancisco1/TP
**Versão:** 2.0 (atualizado no TP2 — substitui o rascunho v1.0 do TP1)

## 1. Problema de Negócio

O mercado pet brasileiro cresce rapidamente, mas esse crescimento carrega custos
socioambientais pouco visíveis ao consumidor final:

- **Ambiental:** grande parte das rações, petiscos e acessórios é vendida em embalagens
  plásticas não recicláveis, e a pegada de carbono da cadeia de produção de ração é elevada.
- **Social:** o Brasil tem uma das maiores populações de animais abandonados do mundo, e a
  decisão de compra (adotar vs. comprar; produto sustentável vs. convencional) raramente é
  informada por dados.
- **Governança:** poucos petshops e fabricantes divulgam de forma transparente suas práticas
  ESG, dificultando a comparação por parte do consumidor.

**Pergunta de negócio:** como ajudar tutores de pets e pequenos petshops a tomar decisões de
compra e de gestão mais sustentáveis, usando dados públicos sobre produtos, abandono/adoção de
animais e boas práticas ESG do setor?

## 2. Objetivo do Projeto

Entregar um dashboard interativo (**PetVerde**) que reúne e organiza dados do setor pet,
traduz esses dados em indicadores simples de sustentabilidade (ambiental e social) e, a
partir do TP2, passa a extrair conteúdo público da web (notícias e artigos) para enriquecer
a análise oferecida ao usuário.

## 3. Escopo

### Dentro do escopo (TP2)

- Reestruturação completa do projeto segundo o padrão **TDSP** (Team Data Science Process),
  com diretórios `app/`, `Code/`, `Data/`, `Docs/`;
- Interface Streamlit dinâmica e interativa (abas, filtros por radio/checkbox/multiselect/
  slider, tabela pesquisável e ordenável);
- Extração de conteúdo da web com **Beautiful Soup** (notícias e artigos da Wikipedia sobre
  consumo consciente e abandono de animais), com dados salvos em `Data/Raw/` (CSV e TXT);
- Geração de **nuvem de palavras** e estatísticas básicas de texto a partir do conteúdo
  coletado;
- **Cache** (`st.cache_data`) e **estado de sessão** (`st.session_state`) para performance e
  persistência de dados entre interações do usuário;
- Serviço de **upload de CSV** para o usuário complementar a base de produtos, com **download**
  dos dados filtrados (CSV/XLSX);
- Finalização do Project Charter e do Data Summary Report.

### Fora do escopo nesta etapa

- Integração completa com APIs em produção (Open Pet Food Facts, IBGE/SIDRA) — planejada para
  o TP3;
- Modelo de recomendação personalizado via engenharia de prompts com LLM — planejado para o
  TP3;
- Deploy em produção (Streamlit Community Cloud) e testes de aceitação com usuários finais —
  planejados para TP3/TP4.

## 4. Alinhamento com os ODS (Agenda 2030)

- **ODS 12 — Consumo e Produção Responsáveis (primário):** Meta 12.5 (reduzir a geração de
  resíduos por prevenção, redução, reciclagem e reuso) e Meta 12.8 (garantir acesso à
  informação relevante para o desenvolvimento sustentável).
- **ODS 15 — Vida Terrestre (secundário):** visibilidade a dados de abandono/adoção de
  animais, contribuindo para o bem-estar animal e a conscientização sobre guarda responsável.

## 5. Público-Alvo

| Público | Interesse |
|---|---|
| Tutores de pets conscientes | Comparar produtos por critérios de sustentabilidade, não só por preço |
| Pequenos e médios petshops | Escolher fornecedores e comunicar práticas ESG aos clientes |
| ONGs e protetores independentes | Usar dados de abandono/adoção para embasar campanhas e captação de recursos |
| Estudantes/pesquisadores | Cruzamento entre ESG, dados abertos e o setor pet |

## 6. Metas e Indicadores de Sucesso (KPIs)

| # | Objetivo | Indicador (KPI) | Meta TP1 | Meta TP2 |
|---|---|---|---|---|
| 1 | Estruturar o projeto de dados | Diretórios TDSP criados e documentados | 100% das fases mapeadas | Estrutura TDSP completa e populada com dados reais/mock |
| 2 | Mapear e coletar fontes de dados | Nº de fontes de dados identificadas/coletadas | ≥ 4 fontes identificadas | ≥ 3 fontes efetivamente coletadas (produtos mock, Wikipedia, notícias) |
| 3 | Entregar protótipo navegável | App Streamlit rodando localmente | App funcional com dados de amostra | App funcional com interatividade, scraping, cache e upload/download |
| 4 | Alinhar com a Agenda 2030 | ODS identificados e justificados | ≥ 1 ODS primário justificado | ODS 12 e 15 mantidos e refletidos na interface |
| 5 | Reduzir fricção na decisão de compra sustentável | Nº de produtos comparados por sessão | Definir baseline no TP2 | Baseline: nº médio de produtos filtrados/exportados por sessão de teste |
| 6 | Estimular consumo consciente via conteúdo | Nº de notícias/artigos exibidos e engajamento com a nuvem de palavras | — | ≥ 40 notícias coletadas e exibidas; nuvem de palavras gerada para 2 fontes de texto |

## 7. Metodologia: CRISP-DM x TDSP

| Fase TDSP | Fase CRISP-DM equivalente | O que significa aqui | Artefatos | Status no TP2 |
|---|---|---|---|---|
| 1. Business Understanding | Business Understanding | Definir problema, metas, ODS e público-alvo | Project Charter, Data Summary Report | ✅ Concluído |
| 2. Data Acquisition and Understanding | Data Understanding | Coletar e explorar os dados (mock + scraping) | Scripts de coleta (`Code/DataAcquisition/`), dados brutos (`Data/Raw/`) | ✅ Concluído |
| 3. Modeling | Data Preparation / Modeling | Limpar e preparar os dados; indicadores de sustentabilidade | Scripts de preparação (`Code/DataPreparation/`), dados tratados (`Data/Processed/`) | ✅ Concluído (indicadores); engenharia de prompts com LLM planejada para TP3 |
| 4. Deployment | Evaluation / Deployment | Publicar o dashboard interativo e documentar reprodutibilidade | App Streamlit (`app/app.py`), README | 🔶 App local completo; deploy em nuvem planejado para TP3 |

## 8. Stakeholders

| Stakeholder | Papel | Interesse |
|---|---|---|
| Herick Francisco | Project Lead / Individual Contributor | Executar e entregar o TP2 |
| Professor(a)/orientador(a) | Sponsor / Avaliador | Avaliar aderência ao CRISP-DM/TDSP e à Agenda 2030 |
| Tutores de pets | Cliente / usuário | Decisões de consumo mais sustentáveis |
| Pequenos petshops | Usuário secundário | Diferenciação via práticas ESG |
| ONGs de proteção animal | Fonte de dados / beneficiário | Visibilidade para a causa animal |

## 9. Cronograma (marcos macro)

| # | Marco | Entrega | Fase TDSP | Status |
|---|---|---|---|---|
| 1 | TP1 | Proposta, planejamento, Project Charter (v0.1), Data Summary Report (v0.1), app demo | Business Understanding | ✅ Concluído |
| 2 | TP2 | Reestruturação TDSP, scraping (Beautiful Soup), cache/session state, upload/download, Project Charter e Data Summary Report finalizados | Data Acquisition & Understanding | ✅ Concluído |
| 3 | TP3 (previsto) | Integração com APIs reais (Open Pet Food Facts, IBGE), engenharia de prompts com LLM, dashboard com dados reais, deploy | Modeling / Deployment | ⏳ Próxima etapa |
| 4 | TP4 (previsto) | Testes, ajustes finais, relatório de encerramento | Customer Acceptance | ⏳ Futuro |

## 10. Riscos e Premissas

- **Risco:** APIs públicas do setor pet podem ter cobertura limitada para o Brasil.
  **Mitigação:** complementar com web scraping (já iniciado no TP2) e dados oficiais (IBGE,
  portais de dados abertos).
- **Risco:** dados de adoção/abandono são fragmentados entre municípios/ONGs.
  **Mitigação:** priorizar fontes agregadoras e documentar como limitação.
- **Risco:** feeds de notícias públicos (RSS) podem mudar de estrutura HTML/XML ao longo do
  tempo, quebrando o script de scraping. **Mitigação:** scripts de coleta são executados
  separadamente do app e os dados coletados ficam versionados em `Data/Raw/`, garantindo que
  o dashboard continue funcionando mesmo se uma nova coleta falhar.
- **Premissa:** o uso de dados de amostra (mock) para produtos pet continua aceitável nesta
  etapa, desde que documentado como tal (ver Data Summary Report); os dados de notícias e os
  textos da Wikipedia, por outro lado, já são reais e coletados via scraping.
