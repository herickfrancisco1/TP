"""
Testes automatizados das rotas da API PetVerde.

Executar a partir da raiz do repositório:
    pytest -v
"""

from fastapi.testclient import TestClient

from Code.Deployment.api import app

cliente = TestClient(app)


def test_raiz_e_saude():
    assert cliente.get("/").status_code == 200
    resposta = cliente.get("/saude")
    assert resposta.status_code == 200
    assert resposta.json()["status"] == "ok"
    assert resposta.json()["arquivos"]["produtos"] is True


def test_listar_produtos_com_filtros():
    resposta = cliente.get("/produtos", params={"categoria": "Ração", "reciclavel": True, "limite": 5})
    assert resposta.status_code == 200
    corpo = resposta.json()
    assert corpo["retornados"] <= 5
    assert all(p["categoria"] == "Ração" and p["embalagem_reciclavel"] for p in corpo["produtos"])
    notas = [p["nota_sustentabilidade"] for p in corpo["produtos"]]
    assert notas == sorted(notas, reverse=True)


def test_paginacao():
    pagina1 = cliente.get("/produtos", params={"limite": 10, "ordenar_por": "id_produto", "decrescente": False}).json()
    pagina2 = cliente.get("/produtos", params={"limite": 10, "deslocamento": 10, "ordenar_por": "id_produto", "decrescente": False}).json()
    assert pagina1["produtos"][0]["id_produto"] == 1
    assert pagina2["produtos"][0]["id_produto"] == 11


def test_categoria_invalida_retorna_422():
    assert cliente.get("/produtos", params={"categoria": "Carro"}).status_code == 422


def test_obter_produto_e_404():
    assert cliente.get("/produtos/1").json()["id_produto"] == 1
    assert cliente.get("/produtos/999999").status_code == 404


def test_criar_produto_calcula_nota_e_aparece_na_consulta():
    novo = {
        "nome_produto": "Ração Teste Refil 3kg",
        "categoria": "Ração",
        "marca": "EcoBicho",
        "tipo_embalagem": "Refil",
        "certificacao": "Selo Cruelty-Free",
        "preco_reais": 89.9,
        "pegada_carbono_kgco2": 1.7,
    }
    resposta = cliente.post("/produtos", json=novo)
    assert resposta.status_code == 201
    criado = resposta.json()
    assert criado["embalagem_reciclavel"] is True
    assert criado["origem"] == "api"
    assert 0 <= criado["nota_sustentabilidade"] <= 10

    consulta = cliente.get(f"/produtos/{criado['id_produto']}")
    assert consulta.status_code == 200
    assert consulta.json()["nome_produto"] == novo["nome_produto"]
    assert cliente.get("/estatisticas").json()["enviados_via_api"] >= 1


def test_criar_produto_invalido_retorna_422():
    invalido = {"nome_produto": "X", "categoria": "Ração", "marca": "A", "tipo_embalagem": "Isopor",
                "preco_reais": -1, "pegada_carbono_kgco2": 1}
    assert cliente.post("/produtos", json=invalido).status_code == 422


def test_estatisticas():
    corpo = cliente.get("/estatisticas").json()
    assert corpo["total_produtos"] >= 120
    assert 0 <= corpo["pct_embalagem_reciclavel"] <= 100
    assert {c["categoria"] for c in corpo["por_categoria"]} >= {"Ração", "Petisco"}


def test_noticias():
    corpo = cliente.get("/noticias", params={"termo": "consumo consciente pet", "limite": 5}).json()
    assert 0 < corpo["retornadas"] <= 5
    assert all(n["termo_busca"] == "consumo consciente pet" for n in corpo["noticias"])


def test_corpus_e_busca():
    corpo = cliente.get("/corpus", params={"fonte": "wikipedia", "limite": 3}).json()
    assert corpo["total"] > 0
    assert all(t["fonte"] == "wikipedia" for t in corpo["trechos"])
    busca = cliente.get("/corpus/busca", params={"q": "abandono de animais", "k": 2}).json()
    assert len(busca["trechos"]) >= 1
