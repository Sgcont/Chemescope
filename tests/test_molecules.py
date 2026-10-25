import pytest

from core.molecules import (RDKIT_DISPONIVEL, buscar_molecula, contar_atomos, formula_de_hill,
                            massa_molar, modelo_3d)


@pytest.mark.parametrize("formula, esperado", [
    ("H2O", {"H": 2, "O": 1}),
    ("CO2", {"C": 1, "O": 2}),
    ("CH4", {"C": 1, "H": 4}),
    ("Ca(OH)2", {"Ca": 1, "O": 2, "H": 2}),
    ("Al2(SO4)3", {"Al": 2, "S": 3, "O": 12}),
])
def test_contagem_de_atomos(formula, esperado):
    assert contar_atomos(formula) == esperado


def test_massa_molar():
    assert massa_molar(contar_atomos("H2O")) == pytest.approx(18.015, abs=0.001)
    assert massa_molar(contar_atomos("CO2")) == pytest.approx(44.009, abs=0.001)


@pytest.mark.parametrize("formula", ["", "   ", None, "h2o", "Xx2", "H2O)", "(H2O", "2H", "H-O", "123"])
def test_formulas_invalidas(formula):
    with pytest.raises(ValueError):
        contar_atomos(formula)


def test_busca_por_nome_e_formula():
    assert buscar_molecula("água").formula == "H2O"
    assert buscar_molecula("Agua").formula == "H2O"
    assert buscar_molecula("NH3").nome == "Amônia"
    assert buscar_molecula("CO").nome == "Monóxido de carbono"  # fórmula da base vence o SMILES


def test_nome_de_elemento_nao_e_molecula():
    assert buscar_molecula("Oxigênio") is None   # elemento, não molécula
    assert buscar_molecula("Oxigênio molecular").formula == "O2"


@pytest.mark.parametrize("consulta", ["", "   ", None, "banana", "@@@"])
def test_busca_invalida(consulta):
    assert buscar_molecula(consulta) is None


def test_formula_sem_estrutura():
    m = buscar_molecula("C3H8")
    assert m.smiles == "" and m.contagem == {"C": 3, "H": 8}


def test_hill():
    assert formula_de_hill({"H": 6, "C": 2, "O": 1}) == "C2H6O"


@pytest.mark.skipif(not RDKIT_DISPONIVEL, reason="RDKit não instalado")
def test_smiles_e_modelo_3d():
    m = buscar_molecula("CCO")
    assert m.origem == "SMILES informado" or m.origem == "base local"
    assert m.contagem == {"C": 2, "H": 6, "O": 1}
    modelo = modelo_3d("O")
    assert len(modelo["atomos"]) == 3 and len(modelo["ligacoes"]) == 2
