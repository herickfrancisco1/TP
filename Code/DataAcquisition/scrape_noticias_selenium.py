"""
PetVerde - Web Scraping de páginas DINÂMICAS com Selenium (TP3)

Por que Selenium aqui?
----------------------
Os links do feed RSS do Google Notícias (coletados no TP2 com Beautiful Soup)
não apontam direto para a notícia: eles abrem uma página intermediária
(news.google.com/rss/articles/...) que só redireciona para o site do veículo
depois que o JavaScript da página é executado. Uma requisição simples com
`requests` + Beautiful Soup recebe apenas essa página intermediária, sem o
endereço final e sem o texto da notícia.

O Selenium controla um navegador Chrome de verdade (em modo invisível,
"headless"), executa o JavaScript, segue o redirecionamento e, já na página
do veículo, lê:
- a URL final da notícia;
- o título da página;
- a descrição/resumo que o próprio veículo publica nas metatags
  (<meta name="description"> / <meta property="og:description">).

Esse resumo é o texto que faltava para as tarefas com LLM da próxima etapa
(classificação de sentimento, resumos e perguntas e respostas). Por respeito
aos termos de uso dos veículos, NÃO copiamos o corpo completo das matérias.

Entrada:  Data/Raw/noticias_petverde.csv            (gerado por scrape_noticias.py)
Saída:    Data/Raw/noticias_detalhadas_selenium.csv

Requisitos: Google Chrome instalado. O Selenium 4 baixa o driver sozinho
(Selenium Manager).

Executar separadamente (fora do Streamlit):
    python Code/DataAcquisition/scrape_noticias_selenium.py            # todas
    python Code/DataAcquisition/scrape_noticias_selenium.py --limite 10
    python Code/DataAcquisition/scrape_noticias_selenium.py --mostrar-navegador
"""

import argparse
import csv
import pathlib
import time

from selenium import webdriver
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

RAIZ = pathlib.Path(__file__).resolve().parents[2]
ENTRADA = RAIZ / "Data" / "Raw" / "noticias_petverde.csv"
SAIDA = RAIZ / "Data" / "Raw" / "noticias_detalhadas_selenium.csv"

TEMPO_MAX_REDIRECIONAMENTO = 15  # segundos
PAUSA_ENTRE_PAGINAS = 1.0        # segundos (educação com os servidores)

CAMPOS_SAIDA = [
    "termo_busca", "titulo", "fonte", "data_publicacao", "link",
    "url_final", "titulo_pagina", "descricao", "status_coleta",
]


def criar_navegador(mostrar: bool = False) -> webdriver.Chrome:
    opcoes = webdriver.ChromeOptions()
    if not mostrar:
        opcoes.add_argument("--headless=new")
    opcoes.add_argument("--window-size=1280,900")
    opcoes.add_argument("--lang=pt-BR")
    opcoes.add_argument("--disable-gpu")
    opcoes.add_argument("--no-sandbox")
    # Não baixa imagens: as páginas carregam mais rápido e só precisamos do HTML.
    opcoes.add_experimental_option("prefs", {"profile.managed_default_content_settings.images": 2})
    navegador = webdriver.Chrome(options=opcoes)
    navegador.set_page_load_timeout(30)
    return navegador


def aceitar_consentimento_google(navegador: webdriver.Chrome) -> None:
    """Se o Google exibir a tela de cookies (consent.google.com), clica em aceitar."""
    if "consent.google" not in navegador.current_url:
        return
    for texto in ("Aceitar tudo", "Accept all", "Concordo", "I agree"):
        botoes = navegador.find_elements(By.XPATH, f"//button[.//*[contains(text(), '{texto}')] or contains(., '{texto}')]")
        if botoes:
            botoes[0].click()
            time.sleep(2)
            return


def ler_meta(navegador: webdriver.Chrome) -> str:
    """Lê a descrição publicada pelo veículo nas metatags da página."""
    seletores = [
        'meta[property="og:description"]',
        'meta[name="description"]',
        'meta[name="twitter:description"]',
    ]
    for seletor in seletores:
        for elemento in navegador.find_elements(By.CSS_SELECTOR, seletor):
            conteudo = (elemento.get_attribute("content") or "").strip()
            if conteudo:
                return " ".join(conteudo.split())
    return ""


def detalhar_noticia(navegador: webdriver.Chrome, link: str) -> dict:
    try:
        navegador.get(link)
        aceitar_consentimento_google(navegador)
        # Espera o JavaScript redirecionar para fora do domínio do Google Notícias.
        WebDriverWait(navegador, TEMPO_MAX_REDIRECIONAMENTO).until(
            lambda nav: "news.google.com" not in nav.current_url and "consent.google" not in nav.current_url
        )
        # Espera o documento do veículo terminar de carregar.
        WebDriverWait(navegador, TEMPO_MAX_REDIRECIONAMENTO).until(
            lambda nav: nav.execute_script("return document.readyState") in ("interactive", "complete")
        )
        descricao = ler_meta(navegador)
        return {
            "url_final": navegador.current_url,
            "titulo_pagina": navegador.title.strip(),
            "descricao": descricao,
            "status_coleta": "ok" if descricao else "sem_descricao",
        }
    except TimeoutException:
        return {"url_final": navegador.current_url, "titulo_pagina": "", "descricao": "",
                "status_coleta": "tempo_esgotado"}
    except WebDriverException as erro:
        return {"url_final": "", "titulo_pagina": "", "descricao": "",
                "status_coleta": f"erro: {erro.__class__.__name__}"}


def main() -> None:
    parser = argparse.ArgumentParser(description="Enriquece as notícias com Selenium.")
    parser.add_argument("--limite", type=int, default=None, help="Máximo de notícias a visitar")
    parser.add_argument("--mostrar-navegador", action="store_true", help="Abre o Chrome visível")
    args = parser.parse_args()

    if not ENTRADA.exists():
        raise SystemExit(f"Arquivo {ENTRADA} não encontrado. Rode antes: python Code/DataAcquisition/scrape_noticias.py")

    with open(ENTRADA, encoding="utf-8-sig") as arquivo:
        noticias = list(csv.DictReader(arquivo))
    if args.limite:
        noticias = noticias[: args.limite]

    navegador = criar_navegador(mostrar=args.mostrar_navegador)
    resultados = []
    try:
        for i, noticia in enumerate(noticias, start=1):
            detalhes = detalhar_noticia(navegador, noticia["link"])
            resultados.append({**noticia, **detalhes})
            print(f"[{i}/{len(noticias)}] {detalhes['status_coleta']:<15} {noticia['titulo'][:70]}")
            time.sleep(PAUSA_ENTRE_PAGINAS)
    finally:
        navegador.quit()

    SAIDA.parent.mkdir(parents=True, exist_ok=True)
    with open(SAIDA, "w", newline="", encoding="utf-8-sig") as arquivo:
        escritor = csv.DictWriter(arquivo, fieldnames=CAMPOS_SAIDA, extrasaction="ignore")
        escritor.writeheader()
        escritor.writerows(resultados)

    com_descricao = sum(r["status_coleta"] == "ok" for r in resultados)
    print(f"\n{len(resultados)} notícias visitadas, {com_descricao} com descrição. Salvo em {SAIDA}")


if __name__ == "__main__":
    main()
