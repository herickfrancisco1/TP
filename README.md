# 🐾 PetVerde — Consumo Consciente para o Mercado Pet

Dashboard de dados a serviço de um petshop sustentável, alinhado à Agenda 2030 (ODS 12 e 15).

**TP2 · Projeto de Bloco (PB)**
**Repositório:** https://github.com/herickfrancisco1/TP

## Objetivo e motivação

O mercado pet brasileiro cresce rapidamente, mas esse crescimento carrega custos
socioambientais pouco visíveis ao consumidor final: embalagens plásticas não recicláveis, alta
pegada de carbono na cadeia produtiva de ração e uma das maiores populações de animais
abandonados do mundo.

O **PetVerde** reúne dados sobre produtos pet, traduz esses dados em indicadores simples de
sustentabilidade (ambiental e social) e extrai conteúdo público da web (notícias e artigos)
para ajudar tutores de pets e pequenos petshops a tomar decisões de compra e gestão mais
conscientes.

- **ODS 12 — Consumo e Produção Responsáveis** (primário)
- **ODS 15 — Vida Terrestre** (secundário)

## O que há de novo no TP2

1. **Reestruturação TDSP** completa do projeto (`app/`, `Code/`, `Data/`, `Docs/`);
2. **Interface dinâmica** em Streamlit: abas, filtros por radio/checkbox/multiselect/slider,
   tabela interativa e pesquisável;
3. **Extração de conteúdo da web com Beautiful Soup**, salva em `Data/Raw/` (CSV e TXT):
   - notícias reais sobre consumo consciente pet e sustentabilidade (Google Notícias);
   - artigos da Wikipedia sobre consumo sustentável e abandono de animais;
4. **Nuvem de palavras** e estatísticas básicas de texto geradas a partir do conteúdo coletado;
5. **Cache** (`st.cache_data`) e **estado de sessão** (`st.session_state`) para performance e
   persistência de dados entre interações;
6. **Upload de CSV** para o usuário complementar a base de produtos, com **download** dos
   dados filtrados em CSV ou XLSX;
7. **Project Charter** e **Data Summary Report** finalizados (`Docs/Project/`,
   `Docs/DataReport/`).

## Estrutura do projeto (TDSP)

```
tp haard/
├── app/
│   └── app.py                  # Aplicação Streamlit (Deployment)
├── Code/
│   ├── DataAcquisition/        # Scripts de coleta (mock + scraping com Beautiful Soup)
│   ├── DataPreparation/        # Limpeza e tratamento dos dados
│   ├── Modeling/                # Indicadores e prompts de LLM — próxima etapa (TP3)
│   └── Deployment/              # Scripts de implantação — próxima etapa (TP3/TP4)
├── Data/
│   ├── Raw/                     # Dados brutos (amostra de produtos, scraping)
│   └── Processed/               # Dados tratados, prontos para o app
├── Docs/
│   ├── Project/                 # Project Charter
│   ├── DataReport/              # Data Summary Report
│   └── Model/                   # Relatórios de modelagem — próximas etapas
├── legacy_turismo_tp3/          # Entrega de outra disciplina, mantida por histórico
├── requirements.txt
└── README.md
```

## Como executar localmente

```bash
python -m venv venv
venv\Scripts\Activate.ps1   # Windows (PowerShell)
pip install -r requirements.txt
```

(Re)coletar os dados (opcional — o repositório já inclui uma coleta em `Data/Raw/`):

```bash
python Code/DataAcquisition/gerar_dados_amostra.py
python Code/DataAcquisition/scrape_wikipedia.py
python Code/DataAcquisition/scrape_noticias.py
python Code/DataPreparation/prepare_data.py
```

Rodar o dashboard:

```bash
streamlit run app/app.py
```

## Fontes de dados

Ver detalhamento completo (campos, limitações e uso planejado) em
[Docs/DataReport/data_summary_report.md](Docs/DataReport/data_summary_report.md).

- Dataset de amostra (mock) de produtos pet, gerado localmente;
- Artigos da Wikipedia (Consumo sustentável; Abandono de animais), coletados via Beautiful Soup;
- Notícias públicas (Google Notícias) sobre consumo consciente pet e sustentabilidade,
  coletadas via Beautiful Soup;
- Planejadas para o TP3: Open Pet Food Facts (API), IBGE/SIDRA (API), LLM via API.

## Documentação do projeto

- [Project Charter](Docs/Project/project_charter.md)
- [Data Summary Report](Docs/DataReport/data_summary_report.md)

## Autor

Herick Francisco

## Uso de IA

Este projeto foi desenvolvido com apoio de IA (Claude, da Anthropic) para estruturação e
implementação do código, conforme a política de Sinal Verde do curso.
