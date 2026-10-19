# 🐾 PetVerde — Consumo Consciente para o Mercado Pet

Dashboard e API de dados a serviço de um petshop sustentável, alinhados à Agenda 2030
(ODS 12 e 15).

**TP3 · Projeto de Bloco (PB)**
**Repositório:** https://github.com/herickfrancisco1/TP

## Objetivo e motivação

O mercado pet brasileiro cresce rapidamente, mas esse crescimento carrega custos
socioambientais pouco visíveis ao consumidor final: embalagens plásticas não recicláveis, alta
pegada de carbono na cadeia produtiva de ração e uma das maiores populações de animais
abandonados do mundo.

O **PetVerde** reúne dados sobre produtos pet, traduz esses dados em indicadores simples de
sustentabilidade (ambiental e social), coleta conteúdo público da web (notícias e artigos) e
disponibiliza tudo por uma API, para ajudar tutores de pets e pequenos petshops a tomar
decisões de compra e gestão mais conscientes.

- **ODS 12 — Consumo e Produção Responsáveis** (primário)
- **ODS 15 — Vida Terrestre** (secundário)

## O que há de novo no TP3

1. **Aplicação com múltiplas páginas** e menu de navegação por seções (`st.navigation`):

   | Seção | Página | Função |
   |---|---|---|
   | Visão geral | 🏠 Início | Problema de negócio, ODS, resumo dos dados e status da API |
   | Análises | 🛒 Produtos & Filtros | Tabela, filtros, upload de CSV, download CSV/XLSX, gráficos |
   | Análises | 📊 Indicadores de Sustentabilidade | KPIs e gráficos (amostra) + produtos reais do Open Pet Food Facts |
   | Análises | 📰 Notícias & NLP | Nuvem de palavras, estatísticas de texto, notícias com descrição (Selenium) |
   | Integrações | 🔌 API PetVerde | Consulta (GET) e cadastro (POST) de dados pela API FastAPI |
   | Inteligência Artificial | 🤖 Preparação para LLMs | Corpus de textos, busca de contexto e laboratório de prompts |

2. **API REST com FastAPI** (`Code/Deployment/api.py`): 9 rotas — consulta e cadastro de
   produtos, indicadores, notícias e corpus para LLM — com validação (Pydantic), documentação
   automática em `/docs` e **10 testes automatizados** (`tests/`). Documentação das rotas em
   [Code/Deployment/README.md](Code/Deployment/README.md).
3. **Scraping de página dinâmica com Selenium** (`scrape_noticias_selenium.py`): segue o
   redirecionamento em JavaScript dos links do Google Notícias e coleta a URL real e a
   descrição de cada notícia.
4. **Produtos reais via API do Open Pet Food Facts** (`coletar_openpetfoodfacts.py`), com
   `requests` — sem Selenium, porque a fonte já oferece JSON.
5. **Preparação para LLMs**: corpus fatiado com metadados (`Data/Processed/corpus_llm.jsonl`),
   templates de prompt (`Code/Modeling/prompts.py`) e plano de uso
   ([Docs/Model/plano_llm.md](Docs/Model/plano_llm.md)).
6. **Documentação atualizada**: Project Charter v3.0 e Data Summary Report v2.0.

## Estrutura do projeto (TDSP)

```
TP/
├── app/
│   ├── app.py                   # Ponto de entrada + menu de navegação (st.navigation)
│   ├── comum.py                 # Caminhos, cache e cliente da API compartilhados
│   └── pages/                   # Uma página por arquivo (0 a 5)
├── Code/
│   ├── DataAcquisition/         # Coleta: amostra, Wikipedia e notícias (BS4), Selenium, Open Pet Food Facts
│   ├── DataPreparation/         # Limpeza e junção dos dados (Raw -> Processed)
│   ├── Modeling/                # Corpus para LLMs e templates de prompt
│   └── Deployment/              # API FastAPI + camada de dados
├── Data/
│   ├── Raw/                     # Dados brutos coletados
│   └── Processed/               # Dados tratados, usados pelo app e pela API
├── Docs/
│   ├── Project/                 # Project Charter
│   ├── DataReport/              # Data Summary Report
│   └── Model/                   # Plano de uso de LLMs
├── tests/                       # Testes automatizados da API (pytest)
├── legacy_turismo_tp3/          # Entrega de outra disciplina, mantida por histórico
├── requirements.txt
└── README.md
```

## Como executar localmente

Requisitos: Python 3.10+ e, para o Selenium, o Google Chrome instalado.

```bash
python -m venv venv
venv\Scripts\Activate.ps1   # Windows (PowerShell)  |  source venv/bin/activate (Linux/Mac)
pip install -r requirements.txt
```

**1. (Opcional) Recoletar os dados** — o repositório já inclui uma coleta em `Data/`:

```bash
python Code/DataAcquisition/gerar_dados_amostra.py
python Code/DataAcquisition/scrape_wikipedia.py
python Code/DataAcquisition/scrape_noticias.py
python Code/DataAcquisition/scrape_noticias_selenium.py      # páginas dinâmicas (Chrome)
python Code/DataAcquisition/coletar_openpetfoodfacts.py     # produtos reais (API)
python Code/DataPreparation/prepare_data.py
python Code/Modeling/preparar_corpus_llm.py
```

**2. Subir a API** (terminal 1):

```bash
uvicorn Code.Deployment.api:app --reload
```

Documentação interativa: <http://127.0.0.1:8000/docs>

**3. Rodar o dashboard** (terminal 2):

```bash
streamlit run app/app.py
```

**4. Rodar os testes da API:**

```bash
pytest -v
```

## Fontes de dados

Detalhamento completo (campos, limitações e uso com LLMs) em
[Docs/DataReport/data_summary_report.md](Docs/DataReport/data_summary_report.md).

- Produtos pet de amostra (sintéticos), gerados localmente;
- Artigos da Wikipedia (Consumo sustentável; Abandono de animais) — Beautiful Soup;
- Notícias do Google Notícias — Beautiful Soup (RSS) + **Selenium** (página dinâmica);
- Produtos reais do **Open Pet Food Facts** — API REST;
- Produtos cadastrados pelos usuários — **API PetVerde** (`POST /produtos`).

## Documentação do projeto

- [Project Charter (v3.0)](Docs/Project/project_charter.md)
- [Data Summary Report (v2.0)](Docs/DataReport/data_summary_report.md)
- [Documentação da API](Code/Deployment/README.md)
- [Plano de uso de LLMs](Docs/Model/plano_llm.md)

## Próxima etapa (TP4)

Integrar um LLM às rotas e à página de IA: resumos dos artigos, classificação de sentimento
das notícias, perguntas e respostas com recuperação de contexto (RAG) e relatórios
automáticos a partir dos indicadores; publicar app e API na nuvem.

## Autor

Herick Francisco

## Uso de IA

Este projeto foi desenvolvido com apoio de IA (Claude, da Anthropic) para estruturação e
implementação do código, conforme a política de Sinal Verde do curso.
