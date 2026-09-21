# Data Summary Report — PetVerde (v1.0 — TP2)

**Autor:** Herick Francisco
**Versão anterior:** v0.1 (rascunho inicial, TP1)

Este relatório documenta, para cada fonte de dados utilizada pelo PetVerde nesta etapa, a
origem, os campos disponíveis, o método de obtenção, as limitações conhecidas e o uso
planejado dentro do dashboard.

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

- **Limitações conhecidas:** dados **sintéticos** (mock), não representam produtos ou marcas
  reais; usados exclusivamente para demonstrar a interface e os indicadores de
  sustentabilidade enquanto a integração com fontes reais (Open Pet Food Facts, ver seção 4)
  não é concluída.
- **Uso planejado:** popular a tabela interativa, os filtros, os gráficos e as métricas-resumo
  (nº de produtos, nota média de sustentabilidade, % de embalagem reciclável) do dashboard.
  O usuário pode complementar este dataset via upload de CSV próprio (ver seção 5).

## 2. Artigos da Wikipedia (conteúdo real, via scraping)

- **Arquivos:** `Data/Raw/wiki_consumo_sustentavel.txt`, `Data/Raw/wiki_abandono_animais.txt`
- **Script de coleta:** `Code/DataAcquisition/scrape_wikipedia.py`
- **Fontes:**
  - https://pt.wikipedia.org/wiki/Consumo_sustentável
  - https://pt.wikipedia.org/wiki/Abandono_de_animais
- **Tipo de acesso:** Web scraping público (HTTP GET + Beautiful Soup, sem necessidade de
  autenticação); extrai o texto dos parágrafos do corpo do artigo (`#mw-content-text p`).
- **Campos:** texto corrido (não estruturado), em português.
- **Limitações conhecidas:** o conteúdo pode ser editado por terceiros a qualquer momento
  (natureza colaborativa da Wikipedia); o script precisa ser executado novamente para obter a
  versão mais recente do artigo. Extração restrita a parágrafos de texto (não inclui tabelas,
  infoboxes ou referências).
- **Uso planejado:** geração de nuvem de palavras e estatísticas básicas de texto (contagem de
  caracteres, palavras, palavras únicas e mais frequentes) na aba "Notícias & Nuvem de
  Palavras" do dashboard.

## 3. Notícias sobre consumo consciente pet e sustentabilidade (conteúdo real, via scraping)

- **Arquivo:** `Data/Raw/noticias_petverde.csv` (bruto) → `Data/Processed/noticias_tratadas.csv` (tratado)
- **Script de coleta:** `Code/DataAcquisition/scrape_noticias.py`
- **Fonte:** feed RSS público do Google Notícias (`news.google.com/rss/search`), para os
  termos de busca: *"consumo consciente pet"*, *"sustentabilidade petshop"* e *"abandono de
  animais adoção"*.
- **Tipo de acesso:** Web scraping público (HTTP GET + Beautiful Soup com parser XML), sem
  necessidade de chave de API ou login.
- **Registros:** 45 notícias (15 por termo de busca, na coleta mais recente).
- **Campos:**

  | Campo | Descrição |
  |---|---|
  | `termo_busca` | Termo de busca que originou a notícia |
  | `titulo` | Manchete da notícia |
  | `fonte` | Veículo de origem |
  | `data_publicacao` | Data/hora de publicação |
  | `link` | URL da notícia |

- **Limitações conhecidas:** o feed retorna apenas manchete, fonte, data e link — não o corpo
  completo da notícia (seria necessário acessar cada link individualmente, o que não foi feito
  nesta etapa para respeitar os termos de uso de cada veículo). A cobertura depende da
  indexação do Google Notícias e pode variar entre execuções do script.
- **Uso planejado:** tabela filtrável de notícias na aba "Notícias & Nuvem de Palavras",
  permitindo ao usuário explorar cobertura recente sobre o tema do projeto.

## 4. Fontes planejadas para o TP3 (ainda não integradas)

| Fonte | Tipo de acesso | Objetivo de uso |
|---|---|---|
| Open Pet Food Facts (`world.openpetfoodfacts.org`) | API REST pública | Substituir o dataset mock de produtos por dados reais de embalagem/ingredientes |
| IBGE — SIDRA / PNS | API REST pública | Dimensionar o público-alvo por região |
| Portais de dados abertos municipais / dados.gov.br | CSV / API | Indicador social de abandono/adoção por região |
| LLM via API (Claude / OpenAI) | API REST | Recomendações de consumo consciente personalizadas via engenharia de prompts |

## 5. Dados complementares enviados pelo usuário (upload)

- O dashboard permite o upload de um arquivo **CSV** pelo usuário, com o objetivo de
  complementar a base de produtos (`sample_products.csv`) com itens adicionais.
- **Formato esperado:** mesmas colunas do dataset base (ver seção 1). Colunas ausentes são
  preenchidas com valores vazios; colunas extras são preservadas na sessão, mas não afetam os
  indicadores calculados a partir das colunas padrão.
- **Persistência:** os dados enviados ficam disponíveis apenas durante a sessão do navegador
  (`st.session_state`) — não são gravados em `Data/Raw/` automaticamente, preservando a
  reprodutibilidade do dataset versionado no repositório.
