"""
PetVerde - Preparação dos dados para uso com LLMs (TP3 -> TP4)

Junta todos os textos coletados até agora num único corpus padronizado,
fatiado em trechos ("chunks") de tamanho controlado e com metadados, pronto
para ser enviado a um LLM nas tarefas planejadas para a próxima etapa:

- Resumo automático (artigos da Wikipedia);
- Classificação de sentimento (notícias);
- Perguntas e respostas com recuperação de contexto - RAG (todo o corpus);
- Geração de relatórios/insights (fichas textuais dos produtos).

Saídas em Data/Processed/:
- corpus_llm.jsonl              -> um trecho por linha (JSON Lines)
- noticias_para_sentimento.csv  -> notícias com coluna "sentimento_rotulo" vazia,
                                   para rotulagem manual de uma amostra de referência
                                   (permite medir a acurácia do LLM no TP4)

Executar separadamente (fora do Streamlit):
    python Code/Modeling/preparar_corpus_llm.py
"""

import json
import pathlib
import re

import pandas as pd

RAIZ = pathlib.Path(__file__).resolve().parents[2]
BRUTO = RAIZ / "Data" / "Raw"
PROCESSADO = RAIZ / "Data" / "Processed"

TAMANHO_MAX_TRECHO = 900  # caracteres (~225 tokens) - cabe folgado em qualquer janela de contexto

ARTIGOS_WIKIPEDIA = {
    "wiki_consumo_sustentavel.txt": ("Consumo sustentável", "ODS 12"),
    "wiki_abandono_animais.txt": ("Abandono de animais", "ODS 15"),
}


def estimar_tokens(texto: str) -> int:
    """Estimativa simples: ~4 caracteres por token (aproximação comum para LLMs)."""
    return max(1, round(len(texto) / 4))


def limpar_texto(texto: str) -> str:
    texto = re.sub(r"\[\s*\d+\s*\]", "", texto)        # remove marcas de referência [1], [2]...
    texto = re.sub(r"\s+([,.;:!?])", r"\1", texto)  # remove espaço antes de pontuação
    texto = re.sub(r"[ \t]+", " ", texto)
    return texto.strip()


def fatiar_em_trechos(texto: str, tamanho_max: int = TAMANHO_MAX_TRECHO) -> list[str]:
    """Agrupa parágrafos até o tamanho máximo; parágrafos longos são quebrados por frase."""
    paragrafos = [limpar_texto(p) for p in texto.split("\n") if p.strip()]
    unidades = []
    for paragrafo in paragrafos:
        if len(paragrafo) <= tamanho_max:
            unidades.append(paragrafo)
        else:
            unidades.extend(re.split(r"(?<=[.!?])\s+", paragrafo))

    trechos, atual = [], ""
    for unidade in unidades:
        if atual and len(atual) + len(unidade) + 1 > tamanho_max:
            trechos.append(atual)
            atual = unidade
        else:
            atual = f"{atual} {unidade}".strip()
    if atual:
        trechos.append(atual)
    return trechos


def trechos_wikipedia() -> list[dict]:
    registros = []
    for nome_arquivo, (titulo, ods) in ARTIGOS_WIKIPEDIA.items():
        caminho = BRUTO / nome_arquivo
        if not caminho.exists():
            continue
        for i, trecho in enumerate(fatiar_em_trechos(caminho.read_text(encoding="utf-8")), start=1):
            registros.append({
                "id": f"wiki-{caminho.stem}-{i:03d}",
                "fonte": "wikipedia",
                "tarefa_sugerida": "resumo; perguntas_respostas",
                "titulo": titulo,
                "texto": trecho,
                "metadados": {"arquivo": nome_arquivo, "ods": ods, "parte": i},
            })
    return registros


def carregar_noticias() -> pd.DataFrame:
    for nome in ("noticias_detalhadas.csv", "noticias_tratadas.csv"):
        caminho = PROCESSADO / nome
        if caminho.exists():
            return pd.read_csv(caminho, encoding="utf-8-sig")
    return pd.DataFrame()


def trechos_noticias(df: pd.DataFrame) -> list[dict]:
    registros = []
    for i, linha in enumerate(df.itertuples(index=False), start=1):
        titulo = str(linha.titulo)
        # Remove o " - Nome do Veículo" que o Google Notícias acrescenta ao fim do título.
        if isinstance(linha.fonte, str) and titulo.endswith(f" - {linha.fonte}"):
            titulo = titulo[: -len(f" - {linha.fonte}")]
        descricao = getattr(linha, "descricao", "")
        descricao = descricao if isinstance(descricao, str) else ""
        texto = f"{titulo}. {descricao}".strip() if descricao else titulo
        registros.append({
            "id": f"noticia-{i:03d}",
            "fonte": "noticias",
            "tarefa_sugerida": "sentimento; perguntas_respostas",
            "titulo": titulo,
            "texto": limpar_texto(texto),
            "metadados": {
                "veiculo": linha.fonte,
                "termo_busca": linha.termo_busca,
                "data_publicacao": str(linha.data_publicacao),
                "link": getattr(linha, "url_final", None) or linha.link,
                "tem_descricao_selenium": bool(descricao),
            },
        })
    return registros


def trechos_produtos() -> list[dict]:
    """Converte cada produto (dado tabular) numa 'ficha' em linguagem natural."""
    caminho = PROCESSADO / "produtos_tratados.csv"
    if not caminho.exists():
        return []
    df = pd.read_csv(caminho, encoding="utf-8-sig")
    registros = []
    for linha in df.itertuples(index=False):
        reciclavel = "reciclável" if linha.embalagem_reciclavel else "não reciclável"
        certificacao = (
            "sem certificação" if linha.certificacao == "Nenhuma" else f"com certificação {linha.certificacao}"
        )
        texto = (
            f"O produto {linha.nome_produto} (categoria {linha.categoria}, marca {linha.marca}) "
            f"usa embalagem do tipo {linha.tipo_embalagem} ({reciclavel}), {certificacao}, "
            f"custa R$ {linha.preco_reais:.2f}, tem pegada de carbono estimada de "
            f"{linha.pegada_carbono_kgco2:.2f} kg CO2 e nota de sustentabilidade "
            f"{linha.nota_sustentabilidade:.1f}/10. Relacionado a: {linha.ods_relacionado}."
        )
        registros.append({
            "id": f"produto-{linha.id_produto:04d}",
            "fonte": "produtos",
            "tarefa_sugerida": "geracao_relatorio; perguntas_respostas",
            "titulo": linha.nome_produto,
            "texto": texto,
            "metadados": {"id_produto": int(linha.id_produto), "categoria": linha.categoria,
                          "dados_sinteticos": True},
        })
    return registros


def main() -> None:
    PROCESSADO.mkdir(parents=True, exist_ok=True)
    noticias = carregar_noticias()

    corpus = trechos_wikipedia() + trechos_noticias(noticias) + trechos_produtos()
    for registro in corpus:
        registro["n_caracteres"] = len(registro["texto"])
        registro["n_tokens_estimado"] = estimar_tokens(registro["texto"])

    with open(PROCESSADO / "corpus_llm.jsonl", "w", encoding="utf-8") as arquivo:
        for registro in corpus:
            arquivo.write(json.dumps(registro, ensure_ascii=False) + "\n")

    resumo = pd.DataFrame(corpus).groupby("fonte").agg(
        trechos=("id", "count"), tokens_estimados=("n_tokens_estimado", "sum")
    )
    print("corpus_llm.jsonl gerado:")
    print(resumo.to_string())

    if not noticias.empty:
        base_rotulo = pd.DataFrame([
            {"id": r["id"], "texto": r["texto"], "veiculo": r["metadados"]["veiculo"],
             "termo_busca": r["metadados"]["termo_busca"], "sentimento_rotulo": ""}
            for r in corpus if r["fonte"] == "noticias"
        ])
        base_rotulo.to_csv(PROCESSADO / "noticias_para_sentimento.csv", index=False, encoding="utf-8-sig")
        print(f"noticias_para_sentimento.csv: {len(base_rotulo)} linhas para rotulagem")


if __name__ == "__main__":
    main()
