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

## Como executar

Requisitos: **Python 3.10 ou mais recente** e **Git**. Para a coleta com Selenium (opcional),
também é preciso ter o **Google Chrome** instalado.

Os comandos abaixo são para o **PowerShell (Windows)**. No Linux/Mac, veja a observação em cada
passo.

### 1. Baixar o projeto e criar o ambiente virtual

```powershell
git clone https://github.com/herickfrancisco1/TP.git
cd TP
python -m venv venv
venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

- Linux/Mac: ative o ambiente com `source venv/bin/activate`.
- Se o PowerShell bloquear o `Activate.ps1` ("execução de scripts foi desabilitada"), rode uma
  vez `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` e ative de novo.
- Com o ambiente ativado, o terminal mostra `(venv)` no início da linha. **Ative o ambiente em
  todo terminal novo** antes de rodar os comandos dos próximos passos.

### 2. Rodar os testes da API

```powershell
python -m pytest -v
```

O resultado esperado é `10 passed`. Os testes usam uma cópia temporária da pasta `Data/`, então
não alteram os arquivos do repositório.

### 3. Subir a API (terminal 1)

Na pasta raiz do projeto, com o ambiente ativado:

```powershell
python -m uvicorn Code.Deployment.api:app --reload
```

Deixe esse terminal aberto. A API fica em <http://127.0.0.1:8000>. A documentação interativa,
onde dá para testar cada rota com o botão **Try it out**, fica em
<http://127.0.0.1:8000/docs>.

### 4. Abrir o dashboard (terminal 2)

Abra **outro** terminal, entre na pasta do projeto, ative o ambiente (`venv\Scripts\Activate.ps1`)
e rode:

```powershell
python -m streamlit run app/app.py
```

O navegador abre em <http://localhost:8501>. Use o **menu lateral** para trocar de página. A
página **🔌 API PetVerde** só funciona com a API do passo 3 ligada; as outras páginas funcionam
mesmo sem ela.

Para encerrar a API ou o dashboard, pressione `Ctrl + C` no terminal correspondente.

### 5. (Opcional) Recoletar e preparar os dados

O repositório já traz os dados prontos em `Data/`. Para coletar tudo de novo (precisa de
internet), rode na ordem, com o ambiente ativado:

```powershell
python Code/DataAcquisition/gerar_dados_amostra.py
python Code/DataAcquisition/scrape_wikipedia.py
python Code/DataAcquisition/scrape_noticias.py
python Code/DataAcquisition/scrape_noticias_selenium.py     # páginas dinâmicas (usa o Chrome)
python Code/DataAcquisition/coletar_openpetfoodfacts.py    # produtos reais (API, leva ~1 min)
python Code/DataPreparation/prepare_data.py
python Code/Modeling/preparar_corpus_llm.py
```

- `scrape_noticias_selenium.py --limite 10` visita só 10 notícias, o que é útil para um teste
  rápido. Com `--mostrar-navegador`, a janela do Chrome fica visível.
- Depois de recoletar, reinicie o Streamlit (ou use **Clear cache** no menu ⋮ do canto superior
  direito) para ver os dados novos.

### Problemas comuns

| Sintoma | Solução |
|---|---|
| `streamlit`, `uvicorn` ou `pytest` "não é reconhecido como comando" | O ambiente não está ativado. Rode `venv\Scripts\Activate.ps1` ou use a forma `python -m ...` dos comandos acima |
| `ModuleNotFoundError` ao rodar algum script | Rode os comandos a partir da **pasta raiz** do projeto (onde está o `README.md`) e confira se o ambiente está ativado |
| Página **API PetVerde** mostra "A API não está respondendo" | Suba a API (passo 3) em outro terminal e clique em **Testar conexão** |
| `[Errno 10048]` ou "address already in use" ao subir a API | A porta 8000 já está em uso. Feche o outro terminal da API ou rode com `--port 8001` e defina `$env:PETVERDE_API_URL="http://127.0.0.1:8001"` antes de abrir o Streamlit |
| Selenium falha ao abrir o navegador | Instale o Google Chrome. O Selenium 4 baixa o driver sozinho na primeira execução (precisa de internet) |
| Abas "Produtos reais" ou "Com descrição (Selenium)" vazias | Esses dados vêm da coleta opcional (passo 5). Rode os scripts e depois `prepare_data.py` |

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
