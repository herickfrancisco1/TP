# Deployment — API PetVerde (FastAPI)

| Arquivo | O que faz |
|---|---|
| `api.py` | Aplicação FastAPI: rotas, modelos de validação (Pydantic) e documentação |
| `dados_petverde.py` | Camada de dados: leitura/escrita dos CSV e do corpus, filtros, indicadores e busca de trechos |

## Como executar

Na raiz do repositório, com o ambiente virtual ativado:

```bash
python -m uvicorn Code.Deployment.api:app --reload
```

- API: <http://127.0.0.1:8000>
- Documentação interativa (Swagger, permite testar as rotas pelo navegador): <http://127.0.0.1:8000/docs>
- Documentação alternativa (ReDoc): <http://127.0.0.1:8000/redoc>

Com a API ligada, rode o Streamlit em **outro terminal** (`python -m streamlit run app/app.py`) e abra a
página **🔌 API PetVerde**, que consome as rotas abaixo. Para apontar o app para outro endereço,
defina `PETVERDE_API_URL` (padrão `http://127.0.0.1:8000`).

Testes automatizados (não alteram os dados do repositório — usam uma cópia temporária):

```bash
python -m pytest -v
```

## Rotas

| Método | Rota | Função |
|---|---|---|
| GET | `/` | Nome, versão e lista de rotas |
| GET | `/saude` | Health check: API no ar e quais arquivos de dados existem |
| GET | `/produtos` | **Consulta** produtos com filtros e paginação |
| GET | `/produtos/{id_produto}` | Detalha um produto (404 se não existir) |
| POST | `/produtos` | **Envia** (cadastra) um novo produto |
| GET | `/estatisticas` | Indicadores de sustentabilidade, geral e por categoria |
| GET | `/noticias` | Notícias coletadas (com descrição do Selenium, quando houver) |
| GET | `/corpus` | Trechos de texto preparados para LLMs |
| GET | `/corpus/busca` | Trechos mais relevantes para uma pergunta (base do RAG) |

### GET `/produtos`

Parâmetros de consulta (todos opcionais):

| Parâmetro | Tipo | Exemplo | Descrição |
|---|---|---|---|
| `categoria` | texto | `Ração` | Ração, Petisco, Higiene, Acessório ou Brinquedo |
| `reciclavel` | booleano | `true` | Só embalagens recicláveis (`true`) ou não (`false`) |
| `nota_min` / `nota_max` | número 0–10 | `8` | Faixa da nota de sustentabilidade |
| `busca` | texto | `EcoBicho` | Trecho do nome do produto |
| `ordenar_por` | texto | `preco_reais` | `nota_sustentabilidade` (padrão), `preco_reais`, `pegada_carbono_kgco2`, `id_produto` |
| `decrescente` | booleano | `false` | Direção da ordenação (padrão `true`) |
| `limite` | inteiro 1–200 | `20` | Itens por página |
| `deslocamento` | inteiro | `20` | Pula N itens (paginação) |

```bash
curl "http://127.0.0.1:8000/produtos?categoria=Ração&reciclavel=true&nota_min=8&limite=3"
```

```json
{
  "total_encontrado": 5,
  "retornados": 3,
  "produtos": [
    {"id_produto": 42, "nome_produto": "Ração BioRação #42", "categoria": "Ração",
     "marca": "BioRação", "tipo_embalagem": "Plástico reciclável", "embalagem_reciclavel": true,
     "certificacao": "Nenhuma", "nota_sustentabilidade": 9.9, "preco_reais": 22.37,
     "pegada_carbono_kgco2": 7.88, "ods_relacionado": "ODS 12", "origem": "amostra"}
  ]
}
```

Valores inválidos (ex.: `categoria=Carro`, `nota_min=20`) retornam **422** com a explicação do erro.

### GET `/produtos/{id_produto}`

```bash
curl http://127.0.0.1:8000/produtos/3
```

Retorna o produto ou **404** `{"detail": "Produto 999 não encontrado."}`.

### POST `/produtos`

Corpo em JSON:

| Campo | Obrigatório | Regra |
|---|---|---|
| `nome_produto` | sim | 3 a 120 caracteres |
| `categoria` | sim | Ração, Petisco, Higiene, Acessório ou Brinquedo |
| `marca` | sim | 2 a 60 caracteres |
| `tipo_embalagem` | sim | Plástico não reciclável, Plástico reciclável, Papel/Kraft, Refil ou Vidro |
| `certificacao` | não | padrão `"Nenhuma"` |
| `preco_reais` | sim | maior que 0 |
| `pegada_carbono_kgco2` | sim | 0 a 100 |
| `ods_relacionado` | não | `ODS 12` (padrão), `ODS 15` ou `ODS 12 e 15` |
| `nota_sustentabilidade` | não | 0 a 10; se omitida, é **calculada** pela API |

Regra da nota calculada: parte de 5,0; +2,5 se a embalagem é reciclável; +1,5 se há
certificação; −(pegada de carbono ÷ 8,5) × 2,5 (limitado a 2,5); resultado entre 0 e 10.

```bash
curl -X POST http://127.0.0.1:8000/produtos -H "Content-Type: application/json" \
  -d '{"nome_produto": "Ração Natural Refil 3kg", "categoria": "Ração", "marca": "EcoBicho",
       "tipo_embalagem": "Refil", "certificacao": "Selo Cruelty-Free",
       "preco_reais": 89.9, "pegada_carbono_kgco2": 1.7}'
```

Resposta **201 Created** com o produto completo (id gerado, `embalagem_reciclavel` e nota
calculados, `origem: "api"`). O produto é gravado em
`Data/Processed/produtos_enviados_api.csv` e passa a aparecer em `GET /produtos`,
`GET /estatisticas` e na página Produtos & Filtros do Streamlit.

> No Windows (PowerShell), o mais simples é testar o POST pela página `/docs` ("Try it out")
> ou pelo formulário da página 🔌 API PetVerde do Streamlit.

### GET `/estatisticas`

Sem parâmetros. Retorna `total_produtos`, `enviados_via_api`, `nota_media`,
`pct_embalagem_reciclavel`, `pegada_carbono_media_kgco2`, `preco_medio_reais` e a lista
`por_categoria` (produtos, nota média, % reciclável, preço e carbono médios).

### GET `/noticias`

| Parâmetro | Exemplo | Descrição |
|---|---|---|
| `termo` | `consumo consciente pet` | Termo de busca usado na coleta |
| `busca` | `adoção` | Palavra no título |
| `limite` | `20` | 1 a 200 |

### GET `/corpus` e GET `/corpus/busca`

- `/corpus?fonte=wikipedia&limite=5` — lista trechos (`fonte`: `wikipedia`, `noticias` ou `produtos`).
- `/corpus/busca?q=abandono de animais&k=3` — devolve os `k` trechos mais relevantes com a
  `pontuacao` de cada um. Na próxima etapa esses trechos serão o **contexto** enviado ao LLM
  (perguntas e respostas com RAG).
