# Modeling — preparação para LLMs (TP3)

| Arquivo | O que faz |
|---|---|
| `preparar_corpus_llm.py` | Junta Wikipedia, notícias e fichas de produtos em `Data/Processed/corpus_llm.jsonl` (trechos de até ~900 caracteres, com metadados e estimativa de tokens) e gera `noticias_para_sentimento.csv` para rotulagem manual |
| `prompts.py` | Instrução de sistema e templates de prompt das 4 tarefas (resumo, sentimento, perguntas e respostas, relatório) + `montar_prompt()` |

```bash
python Code/Modeling/preparar_corpus_llm.py
```

Plano completo em [Docs/Model/plano_llm.md](../../Docs/Model/plano_llm.md). A busca de trechos
relevantes (base do RAG) fica em `Code/Deployment/dados_petverde.py` e é exposta na rota
`GET /corpus/busca` da API.
