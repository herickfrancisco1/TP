# Project Charter — PetVerde: Consumo Consciente para o Mercado Pet

**Autor:** Herick Francisco
**Etapa:** TP3 · Projeto de Bloco (PB)
**Repositório:** https://github.com/herickfrancisco1/TP
**Versão:** 3.0 (atualizado no TP3 — substitui a v2.0 do TP2)

### Histórico de versões

| Versão | Etapa | Principais mudanças |
|---|---|---|
| 1.0 | TP1 | Proposta inicial, problema de negócio, ODS e app demo |
| 2.0 | TP2 | Estrutura TDSP, scraping com Beautiful Soup, cache, upload/download |
| 3.0 | TP3 | App com múltiplas páginas, API FastAPI, scraping dinâmico com Selenium, produtos reais via API do Open Pet Food Facts, preparação dos dados para LLMs |

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

### 1.1 Reavaliação do problema no TP3 (à luz de FastAPI e Selenium)

A pergunta de negócio **foi mantida**, mas as novas ferramentas mudam *como* o PetVerde a
responde:

- **FastAPI** transforma o PetVerde de um painel isolado em um **serviço de dados**: um petshop
  ou ONG pode cadastrar produtos (POST) e consultar indicadores (GET) a partir de outros
  sistemas, sem abrir o dashboard. Isso aproxima o projeto de um uso real por pequenos
  petshops, que poderiam integrar a nota de sustentabilidade ao seu e-commerce.
- **Selenium** resolve uma limitação registrada no TP2: o feed do Google Notícias só
  entregava manchetes, porque os links passam por uma página que redireciona via JavaScript.
  Com o navegador automatizado, o projeto passa a obter a URL real e a descrição de cada
  notícia — texto necessário para as tarefas com LLM.
- **API do Open Pet Food Facts** começa a substituir os dados sintéticos por **produtos reais**.
  O painel mede quantos desses produtos informam o tipo de embalagem: a ausência dessa
  informação é, ela própria, um indicador da falta de transparência ao consumidor (meta 12.8
  do ODS 12).

**Metas ajustadas:** (i) o foco do TP3 deixa de ser "mais telas" e passa a ser **integração**
(API) e **qualidade do texto** coletado; (ii) o deploy em nuvem foi movido para o TP4, para
ser feito uma única vez já com os recursos de IA; (iii) foi incluída uma meta explícita de
preparação de dados para LLMs (KPI 7).

## 2. Objetivo do Projeto

Entregar um dashboard interativo e uma API (**PetVerde**) que reúnem e organizam dados do
setor pet, traduzem esses dados em indicadores simples de sustentabilidade (ambiental e
social) e, a partir do TP4, usam LLMs para resumir conteúdo, classificar notícias, responder
perguntas e gerar relatórios para tutores e petshops.

## 3. Escopo

### Dentro do escopo (TP3)

- **Aplicação Streamlit com múltiplas páginas** e menu de navegação agrupado por seções
  (`st.navigation`): Início · Produtos & Filtros · Indicadores de Sustentabilidade ·
  Notícias & NLP · API PetVerde · Preparação para LLMs;
- **API REST com FastAPI** (`Code/Deployment/api.py`) com 9 rotas, incluindo consulta (GET) e
  envio (POST) de produtos, validação com Pydantic, documentação automática (`/docs`) e testes
  automatizados (`pytest`);
- **Integração app ↔ API**: a página "API PetVerde" consome as rotas e a página de IA usa a
  busca de trechos da API;
- **Web scraping de páginas dinâmicas com Selenium** (`scrape_noticias_selenium.py`) para
  obter URL final e descrição das notícias;
- **Coleta de produtos reais** pela API pública do Open Pet Food Facts (com `requests`, sem
  Selenium, por ser uma API JSON);
- **Preparação para LLMs**: corpus fatiado com metadados (`corpus_llm.jsonl`), templates de
  prompt e plano de uso (`Docs/Model/plano_llm.md`);
- Atualização do Project Charter, do Data Summary Report e do README.

### Fora do escopo nesta etapa

- Chamadas reais a um LLM (previstas para o TP4 — no TP3 os prompts são montados e
  validados, mas não enviados);
- Busca vetorial com embeddings (no TP3 a busca é por sobreposição de palavras);
- Deploy em produção (Streamlit Community Cloud + hospedagem da API) e testes de aceitação
  com usuários — TP4;
- Dados oficiais de abandono/adoção por município (IBGE/dados abertos) — mantidos como
  fonte futura (ver riscos).

## 4. Alinhamento com os ODS (Agenda 2030)

- **ODS 12 — Consumo e Produção Responsáveis (primário):** Meta 12.5 (reduzir a geração de
  resíduos por prevenção, redução, reciclagem e reuso) e Meta 12.8 (garantir acesso à
  informação relevante para o desenvolvimento sustentável). No TP3, a API amplia o acesso à
  informação (12.8) e os dados reais do Open Pet Food Facts medem a transparência sobre
  embalagens (12.5).
- **ODS 15 — Vida Terrestre (secundário):** visibilidade a dados de abandono/adoção de
  animais, contribuindo para o bem-estar animal e a conscientização sobre guarda responsável.

## 5. Público-Alvo

| Público | Interesse |
|---|---|
| Tutores de pets conscientes | Comparar produtos por critérios de sustentabilidade, não só por preço |
| Pequenos e médios petshops | Escolher fornecedores, comunicar práticas ESG e **integrar a nota de sustentabilidade aos seus sistemas via API** |
| ONGs e protetores independentes | Usar dados de abandono/adoção e notícias para embasar campanhas e captação de recursos |
| Estudantes/pesquisadores | Cruzamento entre ESG, dados abertos e o setor pet |

## 6. Metas e Indicadores de Sucesso (KPIs)

| # | Objetivo | Indicador (KPI) | Meta TP2 | Meta TP3 | Situação no TP3 |
|---|---|---|---|---|---|
| 1 | Estruturar o projeto de dados | Estrutura TDSP | Completa e populada | Mantida, com `Code/Modeling` e `Code/Deployment` populados | ✅ Atingida |
| 2 | Coletar fontes de dados | Nº de fontes com coleta implementada | ≥ 3 | ≥ 5 (produtos mock, Wikipedia, notícias, notícias via Selenium, Open Pet Food Facts) | ✅ 5 scripts de coleta |
| 3 | Entregar aplicação navegável | Nº de páginas com menu de navegação | 2 | ≥ 5 páginas, cada uma com uma função distinta | ✅ 6 páginas |
| 4 | Disponibilizar dados por API | Nº de rotas documentadas e testadas | — | ≥ 2 rotas (≥ 1 GET e 1 POST) | ✅ 9 rotas (8 GET, 1 POST) e 10 testes |
| 5 | Alinhar com a Agenda 2030 | ODS refletidos na interface e na API | ODS 12 e 15 | Mantidos; indicadores ligados às metas 12.5 e 12.8 | ✅ Atingida |
| 6 | Enriquecer o conteúdo textual | % das notícias com descrição além da manchete | — | ≥ 60% (via Selenium) | ⏳ Medido a cada execução da coleta (`status_coleta`) |
| 7 | Preparar dados para LLMs | Corpus padronizado e prompts prontos | — | 100% dos textos no corpus com metadados; 4 templates de prompt | ✅ 174 trechos (~10,8 mil tokens) e 4 templates |

## 7. Metodologia: CRISP-DM x TDSP

| Fase TDSP | Fase CRISP-DM equivalente | O que significa aqui | Artefatos | Status no TP3 |
|---|---|---|---|---|
| 1. Business Understanding | Business Understanding | Problema, metas, ODS e público-alvo | Project Charter v3.0, Data Summary Report v2.0 | ✅ Revisado |
| 2. Data Acquisition and Understanding | Data Understanding / Data Preparation | Coleta (Beautiful Soup, Selenium, API) e preparação | `Code/DataAcquisition/`, `Code/DataPreparation/`, `Data/` | ✅ Ampliado |
| 3. Modeling | Modeling | Indicadores de sustentabilidade; preparação para LLMs | `Code/Modeling/` (corpus, prompts), `Docs/Model/plano_llm.md` | 🔶 Dados e prompts prontos; LLM no TP4 |
| 4. Deployment | Evaluation / Deployment | App multipáginas + API REST | `app/`, `Code/Deployment/api.py`, `tests/` | 🔶 Local e testado; deploy em nuvem no TP4 |

## 8. Decisões técnicas do TP3

| Decisão | Motivo |
|---|---|
| `st.navigation` com seções, em vez da pasta `pages/` automática | Menu agrupado (Análises, Integrações, IA), com títulos e ícones controlados no código |
| Selenium **apenas** para as notícias | Único caso com conteúdo dependente de JavaScript (redirecionamento do Google Notícias); para o Open Pet Food Facts há API JSON, então `requests` basta (simplicidade) |
| Coletar só a descrição (metatags) das notícias, não o corpo | Respeito aos termos de uso dos veículos e direitos autorais; a descrição já basta para sentimento e contexto |
| Camada de dados separada da API (`dados_petverde.py`) | A mesma lógica é usada pela API, pelo Streamlit e pelos testes |
| Produtos enviados via POST em CSV separado | Não altera o dataset versionado e facilita auditar o que veio de fora |
| Corpus em JSON Lines com trechos ≤ 900 caracteres | Formato padrão para LLMs/RAG; trechos pequenos facilitam busca e citação de fontes |
| Busca de trechos por palavras (baseline) | Simples e sem dependências; será trocada por embeddings no TP4 sem mudar a rota |

## 9. Stakeholders

| Stakeholder | Papel | Interesse |
|---|---|---|
| Herick Francisco | Project Lead / Individual Contributor | Executar e entregar o TP3 |
| Professor(a)/orientador(a) | Sponsor / Avaliador | Avaliar aderência ao CRISP-DM/TDSP e à Agenda 2030 |
| Tutores de pets | Cliente / usuário | Decisões de consumo mais sustentáveis |
| Pequenos petshops | Usuário secundário / consumidor da API | Diferenciação via práticas ESG |
| ONGs de proteção animal | Fonte de dados / beneficiário | Visibilidade para a causa animal |

## 10. Cronograma (marcos macro)

| # | Marco | Entrega | Fase TDSP | Status |
|---|---|---|---|---|
| 1 | TP1 | Proposta, Project Charter (v1.0), Data Summary Report (v0.1), app demo | Business Understanding | ✅ Concluído |
| 2 | TP2 | Reestruturação TDSP, scraping (Beautiful Soup), cache/session state, upload/download | Data Acquisition & Understanding | ✅ Concluído |
| 3 | TP3 | App multipáginas, API FastAPI, Selenium, Open Pet Food Facts, preparação para LLMs | Modeling / Deployment | ✅ Concluído |
| 4 | TP4 (previsto) | Integração com LLM (resumo, sentimento, Q&A, relatórios), busca vetorial, deploy em nuvem, testes com usuários | Modeling / Customer Acceptance | ⏳ Próxima etapa |

## 11. Riscos e Premissas

- **Risco:** páginas dinâmicas mudam de estrutura e o Selenium pode falhar (tela de cookies,
  paywall, tempo de carregamento). **Mitigação:** coleta executada fora do app, com tempo
  máximo por página, registro do `status_coleta` de cada notícia e junção *left join* —
  notícias sem descrição continuam disponíveis com a manchete.
- **Risco:** a API do Open Pet Food Facts tem cobertura limitada para o Brasil e limite de
  requisições. **Mitigação:** a coleta prioriza produtos vendidos no Brasil e completa com
  outros países; pausa de 6 s entre páginas; o painel mostra a proporção de produtos sem
  informação de embalagem.
- **Risco:** o termo "pet" traz notícias sobre garrafas PET (plástico), fora do tema.
  **Mitigação:** registrado como limitação; no TP4, o LLM fará um filtro de relevância.
- **Risco:** dados de adoção/abandono são fragmentados entre municípios/ONGs.
  **Mitigação:** priorizar fontes agregadoras e documentar como limitação.
- **Risco:** API fora do ar impede o uso da página de integração. **Mitigação:** as demais
  páginas leem os arquivos de `Data/` diretamente; a página de IA tem alternativa local.
- **Premissa:** o uso de dados de amostra (mock) para os indicadores de produtos continua
  aceitável nesta etapa, desde que documentado; notícias, Wikipedia e Open Pet Food Facts são
  dados reais.
