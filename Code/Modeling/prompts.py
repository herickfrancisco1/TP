"""
PetVerde - Modelos de prompt para as tarefas com LLM (preparação do TP4)

Cada tarefa planejada tem um template com instruções fixas e espaços para
os dados do PetVerde. Assim, na próxima etapa basta enviar o texto gerado
por `montar_prompt(...)` para o LLM escolhido (Claude, GPT, Llama etc.),
sem reescrever a lógica da aplicação.

As saídas pedidas em JSON facilitam validar e exibir as respostas no
Streamlit e na API.
"""

INSTRUCAO_SISTEMA = (
    "Você é o assistente do PetVerde, um painel de consumo consciente no mercado pet "
    "alinhado aos ODS 12 (Consumo e Produção Responsáveis) e 15 (Vida Terrestre). "
    "Responda em português do Brasil, de forma objetiva, e use somente as informações "
    "fornecidas. Se a informação não estiver no contexto, diga que não sabe."
)

TEMPLATES = {
    "resumo": {
        "nome": "Resumo automático",
        "descricao": "Resume textos longos (ex.: artigos da Wikipedia) em tópicos.",
        "template": (
            "Resuma o texto abaixo em até {n_topicos} tópicos curtos, destacando o que é "
            "relevante para tutores de pets e petshops que querem consumir de forma mais "
            "sustentável.\n\nTEXTO:\n\"\"\"\n{texto}\n\"\"\""
        ),
    },
    "sentimento": {
        "nome": "Classificação de sentimento",
        "descricao": "Classifica manchetes/notícias como positiva, negativa ou neutra.",
        "template": (
            "Classifique o sentimento da notícia abaixo em relação ao bem-estar animal e à "
            "sustentabilidade no mercado pet. Responda APENAS com um JSON no formato "
            '{{"sentimento": "positivo" | "negativo" | "neutro", "justificativa": "<até 20 palavras>"}}.'
            "\n\nNOTÍCIA:\n\"\"\"\n{texto}\n\"\"\""
        ),
    },
    "perguntas_respostas": {
        "nome": "Perguntas e respostas (RAG)",
        "descricao": "Responde perguntas usando apenas os trechos recuperados do corpus.",
        "template": (
            "Use somente os trechos de contexto abaixo para responder à pergunta. Cite o id "
            "do(s) trecho(s) usados entre colchetes.\n\nCONTEXTO:\n{contexto}\n\n"
            "PERGUNTA: {pergunta}"
        ),
    },
    "relatorio": {
        "nome": "Geração de relatório",
        "descricao": "Transforma os indicadores numéricos em um relatório descritivo.",
        "template": (
            "Com base nos indicadores de sustentabilidade abaixo (dados em JSON), escreva um "
            "relatório curto (3 parágrafos) para o gestor de um petshop: 1) visão geral, "
            "2) categorias que mais precisam de atenção, 3) três recomendações práticas "
            "ligadas ao ODS 12.\n\nINDICADORES:\n{indicadores_json}"
        ),
    },
}


def formatar_contexto(trechos: list[dict]) -> str:
    """Formata trechos recuperados do corpus como contexto numerado para o prompt."""
    return "\n\n".join(f"[{t['id']}] ({t['fonte']}) {t['texto']}" for t in trechos)


def montar_prompt(tarefa: str, **campos) -> str:
    """Preenche o template da tarefa com os dados informados."""
    if tarefa not in TEMPLATES:
        raise ValueError(f"Tarefa desconhecida: {tarefa}. Opções: {list(TEMPLATES)}")
    return TEMPLATES[tarefa]["template"].format(**campos)
