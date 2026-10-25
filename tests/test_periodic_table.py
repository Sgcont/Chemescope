import pytest

from core.periodic_table import buscar_elementos, carregar_elementos


def test_tem_118_elementos_com_z_sequencial():
    elementos = carregar_elementos()
    assert [e.z for e in elementos] == list(range(1, 119))


@pytest.mark.parametrize("consulta", ["Oxigênio", "oxigenio", "O", "o", "8", " 8 "])
def test_busca_oxigenio(consulta):
    assert [e.simbolo for e in buscar_elementos(consulta)] == ["O"]


@pytest.mark.parametrize("consulta", ["Sódio", "Na", "11"])
def test_busca_sodio(consulta):
    assert buscar_elementos(consulta)[0].nome == "Sódio"


@pytest.mark.parametrize("consulta", ["", "   ", None, "Xyz", "0", "119", "-1", "Vibranium"])
def test_busca_invalida_retorna_vazio(consulta):
    assert buscar_elementos(consulta) == []


def test_sugestao_por_prefixo():
    assert "Sódio" in [e.nome for e in buscar_elementos("sod")]


def test_posicoes_sem_colisao():
    posicoes = [(e.linha, e.coluna) for e in carregar_elementos()]
    assert len(posicoes) == len(set(posicoes))


def test_posicoes_conhecidas():
    por_simbolo = {e.simbolo: e for e in carregar_elementos()}
    assert (por_simbolo["He"].linha, por_simbolo["He"].coluna) == (1, 18)
    assert (por_simbolo["Al"].linha, por_simbolo["Al"].coluna) == (3, 13)
    assert (por_simbolo["Hf"].linha, por_simbolo["Hf"].coluna) == (6, 4)
    assert por_simbolo["La"].linha == 9 and por_simbolo["Lr"].linha == 10


def test_categorias():
    por_simbolo = {e.simbolo: e.categoria for e in carregar_elementos()}
    assert por_simbolo["Na"] == "Metal alcalino"
    assert por_simbolo["Cl"] == "Halogênio"
    assert por_simbolo["Ar"] == "Gás nobre"
    assert por_simbolo["Fe"] == "Metal de transição"
    assert por_simbolo["Si"] == "Semimetal"
