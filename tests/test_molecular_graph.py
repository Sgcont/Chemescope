import pytest

pytest.importorskip("rdkit")
from core.molecular_graph import GrafoMolecular, comparar


def test_agua():
    g = GrafoMolecular.de_smiles("O")
    assert (g.n_vertices, g.n_arestas) == (3, 2)
    assert g.esta_conectado() and g.ciclos() == []


def test_benzeno_tem_um_ciclo_de_seis_atomos():
    g = GrafoMolecular.de_smiles("c1ccccc1", hidrogenios=False)
    ciclos = g.ciclos()
    assert len(ciclos) == 1 and len(set(ciclos[0])) == 6


def test_ciclohexano_vs_hexano():
    ciclo = GrafoMolecular.de_smiles("C1CCCCC1", hidrogenios=False)
    cadeia = GrafoMolecular.de_smiles("CCCCCC", hidrogenios=False)
    r = comparar(ciclo, cadeia)
    assert not r["Ligações"]["igual"] and not r["Ciclos independentes"]["igual"]
    assert r["Átomos"]["igual"]


def test_grafo_desconexo():
    g = GrafoMolecular()
    for i, s in enumerate("CCO"):
        g.adicionar_vertice(i, s)
    g.adicionar_aresta(0, 1)
    assert len(g.componentes()) == 2 and not g.esta_conectado()


def test_aresta_com_vertice_inexistente():
    g = GrafoMolecular()
    g.adicionar_vertice(0, "H")
    with pytest.raises(ValueError):
        g.adicionar_aresta(0, 1)


def test_smiles_invalido():
    assert GrafoMolecular.de_smiles("xyz!") is None
