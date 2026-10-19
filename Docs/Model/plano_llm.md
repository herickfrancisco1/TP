# Plano de uso de LLMs — PetVerde (preparação para o TP4)

**Autor:** Herick Francisco · **Etapa:** TP3 · **Versão:** 1.0

Este documento registra como os dados coletados até o TP3 serão usados com LLMs (Large
Language Models) na próxima etapa, e o que já foi preparado para que essa integração seja
direta.

## 1. Inventário dos dados para IA

| Fonte | Volume (TP3) | Natureza | Arquivo preparado |
|---|---|---|---|
| Wikipedia (Consumo sustentável; Abandono de animais) | 9 trechos · ~1,5 mil tokens | Texto corrido, real | `Data/Processed/corpus_llm.jsonl` (`fonte = wikipedia`) |
| Notícias do Google Notícias | 45 notícias · ~0,9 mil tokens (só títulos) | Texto curto, real | `corpus_llm.jsonl` (`fonte = noticias`) e `noticias_para_sentimento.csv` |
| Descrição das notícias (Selenium) | até 45 descrições | Texto curto, real | coluna `descricao` em `Data/Processed/noticias_detalhadas.csv` |
| Produtos (amostra) | 120 fichas · ~8,4 mil tokens | Tabular convertido em texto, sintético | `corpus_llm.jsonl` (`fonte = produtos`) |
| Indicadores agregados | 1 JSON | Numérico | rota `GET /estatisticas` da API |
| Produtos reais (Open Pet Food Facts) | até 300 itens | Tabular, real | `Data/Processed/produtos_reais_opff.csv` |

Cada linha de `corpus_llm.jsonl` tem: `id`, `fonte`, `tarefa_sugerida`, `titulo`, `texto`,
`metadados` (veículo, data, link, ODS…), `n_caracteres` e `n_tokens_estimado`. Os trechos têm no
máximo ~900 caracteres (~225 tokens), tamanho adequado tanto para envio direto quanto para
indexação vetorial.

## 2. Tarefas planejadas

### 2.1 Resumo automático
- **Entrada:** trechos da Wikipedia (e, futuramente, relatórios ESG de fabricantes).
- **Saída:** 3 a 7 tópicos curtos voltados para tutores e petshops.
- **Prompt:** template `resumo` em `Code/Modeling/prompts.py`.
- **Avaliação:** leitura humana de uma amostra (fidelidade ao texto, ausência de invenções).

### 2.2 Classificação de sentimento
- **Entrada:** título + descrição das notícias (a descrição vem do scraping com Selenium e dá
  mais contexto do que só a manchete).
- **Saída:** JSON `{"sentimento": "positivo|negativo|neutro", "justificativa": "..."}`.
- **Avaliação:** rotular à mão ~30 notícias em `noticias_para_sentimento.csv`
  (coluna `sentimento_rotulo`) e medir a acurácia do LLM contra esses rótulos.
- **Achado do TP3:** o termo "pet" também traz notícias sobre **garrafas PET** (plástico).
  O LLM pode ser usado antes, como filtro de relevância ("a notícia é sobre animais de
  estimação?"), melhorando a qualidade da base.

### 2.3 Perguntas e respostas (RAG)
- **Fluxo:** pergunta do usuário → `GET /corpus/busca` recupera os *k* trechos mais relevantes
  → template `perguntas_respostas` monta o prompt com o contexto numerado → LLM responde
  citando os ids dos trechos.
- **Já pronto no TP3:** a rota de busca (baseline por sobreposição de palavras) e o template.
- **Evolução no TP4:** trocar a busca por palavras por **embeddings** + índice vetorial, mantendo
  a mesma rota da API.

### 2.4 Geração de relatórios
- **Entrada:** JSON de `GET /estatisticas` (nota média, % de embalagens recicláveis, pegada de
  carbono, por categoria).
- **Saída:** relatório de 3 parágrafos para o gestor do petshop, com recomendações ligadas ao
  ODS 12.

## 3. Arquitetura prevista

```
Coleta (BS4 / Selenium / API OPFF) ─► Data/Raw ─► prepare_data.py ─► Data/Processed
                                                        │
                                   preparar_corpus_llm.py ─► corpus_llm.jsonl
                                                        │
               FastAPI (/corpus, /corpus/busca, /estatisticas)  ◄─── Streamlit (página 🤖)
                                                        │
                                    TP4: rota /ia/* que chama o LLM com prompts.py
```

A chave da API do LLM ficará em variável de ambiente (ex.: `ANTHROPIC_API_KEY` ou
`OPENAI_API_KEY`), nunca no repositório.

## 4. Riscos e cuidados

- **Alucinação:** instrução de sistema exige usar apenas o contexto fornecido e admitir quando
  não souber; respostas de Q&A citam os trechos.
- **Dados sintéticos:** as fichas de produtos de amostra são marcadas com
  `dados_sinteticos: true` nos metadados e não devem ser apresentadas como produtos reais.
- **Custos/limites:** com ~11 mil tokens no corpus inteiro, o custo de processamento é baixo;
  ainda assim, as respostas devem ser armazenadas em cache para não repetir chamadas.
- **Direitos autorais:** só são usados títulos e descrições públicas das notícias, não o corpo
  das matérias.
