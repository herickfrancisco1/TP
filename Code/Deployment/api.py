"""
PetVerde - API REST com FastAPI (TP3)

Expõe os dados do PetVerde (produtos, indicadores, notícias e o corpus de
textos preparado para LLMs) por meio de rotas HTTP. A aplicação Streamlit
consome esta API na página "🔌 API PetVerde".

Como executar (a partir da raiz do repositório):
    uvicorn Code.Deployment.api:app --reload

Documentação interativa gerada automaticamente pelo FastAPI:
    http://127.0.0.1:8000/docs   (Swagger UI)
    http://127.0.0.1:8000/redoc  (ReDoc)

Detalhes de cada rota em Code/Deployment/README.md.
"""

import pathlib
import sys
from typing import Literal, Optional

from fastapi import FastAPI, HTTPException, Query, status
from pydantic import BaseModel, Field

# Permite importar dados_petverde tanto com
# "uvicorn Code.Deployment.api:app" quanto com "uvicorn api:app" dentro da pasta.
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import dados_petverde as dados  # noqa: E402

DESCRICAO = """
API de dados do **PetVerde** — consumo consciente no mercado pet (ODS 12 e ODS 15).

* **Produtos**: consultar (GET) e cadastrar (POST) produtos com indicadores de sustentabilidade.
* **Indicadores**: estatísticas agregadas de sustentabilidade por categoria.
* **Notícias**: manchetes coletadas por scraping (Beautiful Soup + Selenium).
* **Corpus LLM**: textos já fatiados e prontos para resumos, sentimento e perguntas e respostas.
"""

TAGS = [
    {"name": "Status", "description": "Verificação de funcionamento da API."},
    {"name": "Produtos", "description": "Consulta e cadastro de produtos pet."},
    {"name": "Indicadores", "description": "Estatísticas de sustentabilidade."},
    {"name": "Notícias", "description": "Notícias coletadas via web scraping."},
    {"name": "Corpus LLM", "description": "Textos preparados para a etapa de IA (LLMs)."},
]

app = FastAPI(
    title="PetVerde API",
    description=DESCRICAO,
    version="3.0.0",
    openapi_tags=TAGS,
)

Categoria = Literal["Ração", "Petisco", "Higiene", "Acessório", "Brinquedo"]
TipoEmbalagem = Literal["Plástico não reciclável", "Plástico reciclável", "Papel/Kraft", "Refil", "Vidro"]
Ods = Literal["ODS 12", "ODS 15", "ODS 12 e 15"]
FonteCorpus = Literal["wikipedia", "noticias", "produtos"]


# ---------------------------------------------------------------------------
# Modelos (validação automática dos dados de entrada e saída)
# ---------------------------------------------------------------------------
class ProdutoEntrada(BaseModel):
    nome_produto: str = Field(..., min_length=3, max_length=120, examples=["Ração Natural Refil 3kg"])
    categoria: Categoria = Field(..., examples=["Ração"])
    marca: str = Field(..., min_length=2, max_length=60, examples=["EcoBicho"])
    tipo_embalagem: TipoEmbalagem = Field(..., examples=["Refil"])
    certificacao: str = Field("Nenhuma", max_length=60, examples=["Selo Cruelty-Free"])
    preco_reais: float = Field(..., gt=0, le=10_000, examples=[89.9])
    pegada_carbono_kgco2: float = Field(..., ge=0, le=100, examples=[2.4])
    ods_relacionado: Ods = Field("ODS 12", examples=["ODS 12"])
    nota_sustentabilidade: Optional[float] = Field(
        None, ge=0, le=10,
        description="Opcional. Se omitida, a API calcula a nota a partir da embalagem, "
                    "certificação e pegada de carbono.",
    )


class Produto(BaseModel):
    id_produto: int
    nome_produto: str
    categoria: str
    marca: str
    tipo_embalagem: str
    embalagem_reciclavel: bool
    certificacao: str
    nota_sustentabilidade: float
    preco_reais: float
    pegada_carbono_kgco2: float
    ods_relacionado: str
    origem: str = Field(..., description="'amostra' (dataset base) ou 'api' (enviado via POST)")


class ListaProdutos(BaseModel):
    total_encontrado: int
    retornados: int
    produtos: list[Produto]


# ---------------------------------------------------------------------------
# Rotas
# ---------------------------------------------------------------------------
@app.get("/", tags=["Status"], summary="Informações da API")
def raiz():
    """Mostra o nome da API, a versão e os links da documentação."""
    return {
        "api": "PetVerde API",
        "versao": app.version,
        "documentacao": {"swagger": "/docs", "redoc": "/redoc"},
        "rotas": ["/saude", "/produtos", "/produtos/{id_produto}", "/estatisticas", "/noticias",
                  "/corpus", "/corpus/busca"],
    }


@app.get("/saude", tags=["Status"], summary="Health check")
def saude():
    """Confirma que a API está no ar e quais arquivos de dados foram encontrados."""
    return {
        "status": "ok",
        "arquivos": {
            "produtos": dados.ARQ_PRODUTOS_BASE.exists(),
            "noticias": dados.ARQ_NOTICIAS.exists(),
            "noticias_detalhadas_selenium": dados.ARQ_NOTICIAS_DETALHADAS.exists(),
            "corpus_llm": dados.ARQ_CORPUS.exists(),
        },
    }


@app.get("/produtos", tags=["Produtos"], response_model=ListaProdutos, summary="Consultar produtos")
def listar_produtos(
    categoria: Optional[Categoria] = Query(None, description="Filtra por categoria"),
    reciclavel: Optional[bool] = Query(None, description="true = só embalagens recicláveis"),
    nota_min: Optional[float] = Query(None, ge=0, le=10, description="Nota mínima de sustentabilidade"),
    nota_max: Optional[float] = Query(None, ge=0, le=10, description="Nota máxima de sustentabilidade"),
    busca: Optional[str] = Query(None, min_length=2, description="Trecho do nome do produto"),
    ordenar_por: Literal["nota_sustentabilidade", "preco_reais", "pegada_carbono_kgco2", "id_produto"] = "nota_sustentabilidade",
    decrescente: bool = True,
    limite: int = Query(20, ge=1, le=200),
    deslocamento: int = Query(0, ge=0, description="Para paginação"),
):
    """Lista produtos (base de amostra + enviados via POST), com filtros e paginação."""
    df = dados.carregar_produtos()
    filtrados = dados.filtrar_produtos(
        df, categoria, reciclavel, nota_min, nota_max, busca,
        ordenar_por=ordenar_por, decrescente=decrescente, limite=len(df) or 1,
    )
    pagina = filtrados.iloc[deslocamento: deslocamento + limite]
    registros = dados.df_para_registros(pagina)
    return {"total_encontrado": len(filtrados), "retornados": len(registros), "produtos": registros}


@app.get("/produtos/{id_produto}", tags=["Produtos"], response_model=Produto, summary="Detalhar um produto")
def obter_produto(id_produto: int):
    """Retorna um único produto pelo seu `id_produto` (404 se não existir)."""
    produto = dados.buscar_produto(id_produto)
    if produto is None:
        raise HTTPException(status_code=404, detail=f"Produto {id_produto} não encontrado.")
    return produto


@app.post(
    "/produtos", tags=["Produtos"], response_model=Produto,
    status_code=status.HTTP_201_CREATED, summary="Cadastrar produto",
)
def criar_produto(produto: ProdutoEntrada):
    """Cadastra um novo produto. Ele é gravado em `Data/Processed/produtos_enviados_api.csv`
    e passa a aparecer nas consultas e nos indicadores. A nota de sustentabilidade é
    calculada automaticamente quando não for informada."""
    return dados.adicionar_produto(produto.model_dump())


@app.get("/estatisticas", tags=["Indicadores"], summary="Indicadores de sustentabilidade")
def estatisticas():
    """Nota média, % de embalagens recicláveis, pegada de carbono e preço médio,
    no geral e por categoria."""
    return dados.estatisticas_produtos()


@app.get("/noticias", tags=["Notícias"], summary="Consultar notícias")
def listar_noticias(
    termo: Optional[str] = Query(None, description="Termo usado na coleta, ex.: 'consumo consciente pet'"),
    busca: Optional[str] = Query(None, min_length=2, description="Palavra no título"),
    limite: int = Query(20, ge=1, le=200),
):
    """Notícias coletadas do Google Notícias (com descrição obtida via Selenium, quando disponível)."""
    df = dados.filtrar_noticias(termo, busca, limite)
    return {"retornadas": len(df), "noticias": dados.df_para_registros(df)}


@app.get("/corpus", tags=["Corpus LLM"], summary="Listar trechos do corpus")
def listar_corpus(
    fonte: Optional[FonteCorpus] = None,
    limite: int = Query(20, ge=1, le=500),
):
    """Trechos de texto (com metadados e estimativa de tokens) prontos para envio a um LLM."""
    corpus = dados.carregar_corpus()
    if fonte:
        corpus = [c for c in corpus if c["fonte"] == fonte]
    return {"total": len(corpus), "trechos": corpus[:limite]}


@app.get("/corpus/busca", tags=["Corpus LLM"], summary="Buscar trechos relevantes (base do RAG)")
def buscar_corpus(
    q: str = Query(..., min_length=3, description="Pergunta ou palavras-chave"),
    k: int = Query(3, ge=1, le=10, description="Quantidade de trechos"),
    fonte: Optional[FonteCorpus] = None,
):
    """Recupera os `k` trechos mais relevantes para uma pergunta. É o primeiro passo de um
    sistema de Perguntas e Respostas com LLM (RAG), a ser concluído na próxima etapa."""
    return {"pergunta": q, "trechos": dados.buscar_trechos(q, k, fonte)}
