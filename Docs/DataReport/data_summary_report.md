# Data Summary Report — PetVerde (v2.0 — TP3)

**Autor:** Herick Francisco
**Versões anteriores:** v0.1 (TP1, rascunho) · v1.0 (TP2)

Este relatório documenta, para cada fonte de dados utilizada pelo PetVerde, a origem, os
campos disponíveis, o método de obtenção, as limitações conhecidas e o uso planejado — incluindo
o uso previsto com LLMs na próxima etapa.

**O que mudou no TP3:** duas novas fontes (notícias enriquecidas via **Selenium** e produtos
reais via **API do Open Pet Food Facts**), dados recebidos pela **API FastAPI** do projeto e um
**corpus de textos preparado para LLMs**.

## Visão geral das fontes

| # | Fonte | Real ou sintética | Método | Arquivo(s) | Novidade |
|---|---|---|---|---|---|
| 1 | Produtos pet (amostra) | Sintética | Script Python (seed fixa) | `sample_products.csv` → `produtos_tratados.csv` | TP1/TP2 |
| 2 | Artigos da Wikipedia | Real | Beautiful Soup | `wiki_*.txt` | TP2 |
| 3 | Notícias (Google Notícias) | Real | Beautiful Soup (RSS) | `noticias_petverde.csv` → `noticias_tratadas.csv` | TP2 |
| 4 | Notícias detalhadas | Real | **Selenium** (página dinâmica) | `noticias_detalhadas_selenium.csv` → `noticias_detalhadas.csv` | **TP3** |
| 5 | Produtos reais | Real | **API REST** do Open Pet Food Facts | `openpetfoodfacts_produtos.csv` → `produtos_reais_opff.csv` | **TP3** |
| 6 | Produtos enviados via API | Informada pelo usuário | **POST /produtos** (FastAPI) | `produtos_enviados_api.csv` | **TP3** |
| 7 | Corpus para LLMs | Derivada (1–4) | Script de preparação | `corpus_llm.jsonl`, `noticias_para_sentimento.csv` | **TP3** |
| 8 | Upload de CSV | Informada pelo usuário | Streamlit (sessão) | — (memória da sessão) | TP2 |

Fluxo: `Code/DataAcquisition/` grava em `Data/Raw/` → `Code/DataPreparation/prepare_data.py`
grava em `Data/Processed/` → `Code/Modeling/preparar_corpus_llm.py` gera o corpus → app
Streamlit e API leem de `Data/Processed/`.

## 1. Produtos pet (dados de amostra / mock)

- **Arquivo:** `Data/Raw/sample_products.csv` (bruto) → `Data/Processed/produtos_tratados.csv` (tratado)
- **Script de geração:** `Code/DataAcquisition/gerar_dados_amostra.py`
- **Tipo de acesso:** arquivo local gerado sinteticamente (seed fixa, reprodutível)
- **Registros:** 120 produtos
- **Campos:**

  | Campo | Descrição |
  |---|---|
  | `id_produto` | Identificador sequencial do produto |
  | `nome_produto` | Nome descritivo (categoria + marca + número) |
  | `categoria` | Ração, Petisco, Higiene, Acessório ou Brinquedo |
  | `marca` | Uma de 10 marcas fictícias |
  | `tipo_embalagem` | Plástico não reciclável, Plástico reciclável, Papel/Kraft, Refil ou Vidro |
  | `embalagem_reciclavel` | Booleano derivado do tipo de embalagem |
  | `certificacao` | Selo/certificação ambiental ou social associada ao produto (ou "Nenhuma") |
  | `nota_sustentabilidade` | Indicador sintético de 0 a 10 (maior para embalagens recicláveis e produtos certificados) |
  | `preco_reais` | Preço de venda simulado |
  | `pegada_carbono_kgco2` | Pegada de carbono estimada (simulada) |
  | `ods_relacionado` | ODS 12, ODS 15 ou ambos |

- **Limitações conhecidas:** dados **sintéticos**, não representam produtos ou marcas reais.
  No TP3 eles passam a conviver com produtos reais do Open Pet Food Facts (seção 5), mas
  continuam sendo a base dos indicadores, porque a fonte real não traz preço, pegada de
  carbono nem nota de sustentabilidade.
- **Uso:** páginas Produtos & Filtros e Indicadores; rotas `GET /produtos`,
  `GET /produtos/{id}` e `GET /estatisticas`; fichas textuais no corpus para LLMs (seção 7),
  marcadas como `dados_sinteticos: true`.

## 2. Artigos da Wikipedia (conteúdo real, via scraping)

- **Arquivos:** `Data/Raw/wiki_consumo_sustentavel.txt`, `Data/Raw/wiki_abandono_animais.txt`
- **Script de coleta:** `Code/DataAcquisition/scrape_wikipedia.py`
- **Fontes:** https://pt.wikipedia.org/wiki/Consumo_sustentável e
  https://pt.wikipedia.org/wiki/Abandono_de_animais
- **Tipo de acesso:** HTTP GET + Beautiful Soup (sem autenticação); extrai os parágrafos do
  corpo do artigo (`#mw-content-text p`).
- **Campos:** texto corrido, em português (~5,3 mil e ~1 mil caracteres).
- **Limitações conhecidas:** conteúdo editável por terceiros; o artigo "Abandono de animais" é
  curto; extração restrita a parágrafos (sem tabelas/infoboxes).
- **Uso:** nuvem de palavras e estatísticas de texto (página Notícias & NLP); **resumo
  automático** e contexto para **perguntas e respostas** com LLM (9 trechos no corpus).

## 3. Notícias do Google Notícias (conteúdo real, via scraping)

- **Arquivo:** `Data/Raw/noticias_petverde.csv` (bruto) → `Data/Processed/noticias_tratadas.csv` (tratado)
- **Script de coleta:** `Code/DataAcquisition/scrape_noticias.py`
- **Fonte:** feed RSS público do Google Notícias (`news.google.com/rss/search`), termos
  *"consumo consciente pet"*, *"sustentabilidade petshop"* e *"abandono de animais adoção"*.
- **Tipo de acesso:** HTTP GET + Beautiful Soup (parser XML), sem chave de API.
- **Registros:** 45 notícias (15 por termo), de 39 veículos diferentes.
- **Campos:** `termo_busca`, `titulo`, `fonte`, `data_publicacao`, `link`.
- **Limitações conhecidas:** o feed traz só manchete, fonte, data e link; o `link` aponta para
  uma página intermediária do Google (ver seção 4). Ambiguidade do termo "pet": algumas
  notícias tratam de **garrafas PET** (plástico), e não de animais — ruído a ser filtrado no TP4.
- **Uso:** tabela filtrável, nuvem de palavras, rota `GET /noticias`, base da coleta com
  Selenium e da **classificação de sentimento**.

## 4. Notícias detalhadas — scraping de página dinâmica com Selenium (TP3)

- **Arquivos:** `Data/Raw/noticias_detalhadas_selenium.csv` (bruto) →
  `Data/Processed/noticias_detalhadas.csv` (tratado; junção com a seção 3)
- **Script de coleta:** `Code/DataAcquisition/scrape_noticias_selenium.py`
- **Por que Selenium:** os links do feed (`news.google.com/rss/articles/...`) abrem uma página
  que só redireciona para o veículo após executar **JavaScript**. Com `requests` + Beautiful
  Soup obtém-se apenas a página intermediária. O Selenium controla um Chrome *headless*,
  aceita a tela de consentimento do Google quando ela aparece, espera o redirecionamento
  (`WebDriverWait`) e lê a página final.
- **Campos adicionados:**

  | Campo | Descrição |
  |---|---|
  | `url_final` | Endereço real da notícia no site do veículo |
  | `titulo_pagina` | Título da página final |
  | `descricao` | Resumo publicado pelo veículo nas metatags (`og:description`, `description`, `twitter:description`) |
  | `status_coleta` | `ok`, `sem_descricao`, `tempo_esgotado`, `erro: ...` ou `nao_visitada` |

- **Tratamento:** *left join* pelo `link` com `noticias_tratadas.csv` — todas as notícias
  permanecem, mesmo as que o Selenium não conseguiu detalhar.
- **Limitações conhecidas:** depende do Google Chrome instalado; alguns veículos bloqueiam
  robôs, exigem login (paywall) ou não publicam descrição; a coleta é lenta (~2–5 s por
  notícia). Por respeito aos termos de uso, **não** se copia o corpo das matérias.
- **Uso:** coluna de descrição na página Notícias & NLP e na rota `GET /noticias`; texto mais
  rico para **sentimento** e **perguntas e respostas** com LLM.

## 5. Produtos reais — API do Open Pet Food Facts (TP3)

- **Arquivos:** `Data/Raw/openpetfoodfacts_produtos.csv` → `Data/Processed/produtos_reais_opff.csv`
- **Script de coleta:** `Code/DataAcquisition/coletar_openpetfoodfacts.py`
- **Fonte:** https://world.openpetfoodfacts.org — base aberta e colaborativa (licença ODbL).
- **Tipo de acesso:** API REST pública (`/api/v2/search`), JSON, sem chave. Não exige Selenium.
  Categorias `en:dog-food` e `en:cat-food`; prioriza produtos vendidos no Brasil
  (`countries_tags=en:brazil`) e completa com outros países quando há menos de 30.
  Até 150 produtos por espécie, pausa de 6 s entre requisições.
- **Campos:**

  | Campo | Descrição |
  |---|---|
  | `codigo_barras` | Código EAN do produto |
  | `nome_produto` | Nome (em português quando disponível) |
  | `marcas` | Marca(s) |
  | `especie` | Cão ou Gato |
  | `embalagem` | Materiais de embalagem informados pela comunidade |
  | `embalagem_reciclavel` | Sim / Não / Sem informação — classificado por palavras-chave (papel, vidro, metal, "recycl" = Sim; plástico = Não) |
  | `selos` | Rótulos/certificações (ex.: orgânico) |
  | `vendido_no_brasil` | Se o produto consta como vendido no Brasil |
  | `ecoscore` | Nota ambiental da plataforma, quando existir |
  | `url` | Página do produto no Open Pet Food Facts |

- **Limitações conhecidas:** cobertura pequena para o Brasil; muitos produtos sem informação de
  embalagem; a classificação de reciclabilidade é heurística. Não há preço nem pegada de
  carbono, por isso a nota de sustentabilidade continua calculada só na base de amostra.
- **Uso:** aba "Produtos reais" da página Indicadores (espécie × reciclabilidade, marcas,
  % com informação de embalagem — indicador de transparência ligado à meta 12.8).

## 6. Produtos enviados pela API do projeto (TP3)

- **Arquivo:** `Data/Processed/produtos_enviados_api.csv` (criado no primeiro POST)
- **Origem:** rota `POST /produtos` da API FastAPI (`Code/Deployment/api.py`), usada pelo
  formulário da página "API PetVerde" ou por qualquer sistema externo.
- **Campos:** os mesmos da seção 1. Os dados são **validados** pela API (categorias e
  embalagens permitidas, preço > 0, nota 0–10); `id_produto` e `embalagem_reciclavel` são
  gerados pela API; `nota_sustentabilidade` é calculada quando não informada.
- **Uso:** aparecem com `origem = "api"` em `GET /produtos` e `GET /estatisticas` e na página
  Produtos & Filtros (opção "Incluir produtos cadastrados via API").
- **Observação:** o arquivo está no `.gitignore` para que testes manuais não sujem o
  repositório; o dataset versionado continua sendo o da seção 1.

## 7. Corpus de textos para LLMs (TP3)

- **Arquivos:** `Data/Processed/corpus_llm.jsonl` e `Data/Processed/noticias_para_sentimento.csv`
- **Script:** `Code/Modeling/preparar_corpus_llm.py`
- **Conteúdo atual:** 174 trechos — 9 da Wikipedia, 45 de notícias e 120 fichas de produtos —
  com ~10,8 mil tokens estimados no total. Cada trecho tem `id`, `fonte`, `tarefa_sugerida`,
  `titulo`, `texto`, `metadados`, `n_caracteres` e `n_tokens_estimado`.
- **Tratamento:** remoção de marcas de referência (`[1]`), espaços e do nome do veículo no fim
  das manchetes; parágrafos agrupados em trechos de até ~900 caracteres; dados tabulares
  convertidos em frases.
- **Uso:** rotas `GET /corpus` e `GET /corpus/busca` e página "Preparação para LLMs";
  `noticias_para_sentimento.csv` tem a coluna `sentimento_rotulo` vazia para rotulagem manual
  de uma amostra de referência (avaliação do LLM no TP4). Plano completo em
  [Docs/Model/plano_llm.md](../Model/plano_llm.md).

## 8. Dados complementares enviados pelo usuário (upload)

- O dashboard permite o upload de um **CSV** para complementar a base de produtos.
- **Formato esperado:** mesmas colunas do dataset base (seção 1). Colunas ausentes ficam vazias;
  colunas extras são preservadas na sessão.
- **Persistência:** apenas durante a sessão do navegador (`st.session_state`). Para gravar
  produtos de forma permanente, o caminho no TP3 é a rota `POST /produtos` (seção 6).

## 9. Fontes planejadas para as próximas etapas

| Fonte | Tipo de acesso | Objetivo de uso |
|---|---|---|
| LLM via API (Claude / OpenAI / modelo aberto) | API REST | Resumos, sentimento, perguntas e respostas e relatórios (TP4) |
| Embeddings (mesmo provedor ou modelo local) | API / biblioteca | Busca vetorial no corpus, substituindo a busca por palavras |
| IBGE — SIDRA / PNS | API REST pública | Dimensionar o público-alvo por região |
| Portais de dados abertos municipais / dados.gov.br | CSV / API | Indicador social de abandono/adoção por região |
