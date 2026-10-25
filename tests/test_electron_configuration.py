import pytest

from core.electron_configuration import (
    CAPACIDADE, ConfiguracaoNaoSuportada, configuracao_eletronica, diagrama_orbitais,
    eletrons_de_valencia, eletrons_por_camada, formatar)


def texto(z, carga=0):
    return formatar(configuracao_eletronica(z, carga).subniveis, expoente=False)


@pytest.mark.parametrize("z, esperado", [
    (1, "1s1"),
    (2, "1s2"),
    (6, "1s2 2s2 2p2"),
    (8, "1s2 2s2 2p4"),
    (11, "1s2 2s2 2p6 3s1"),
    (26, "1s2 2s2 2p6 3s2 3p6 3d6 4s2"),
])
def test_configuracoes_comuns(z, esperado):
    assert texto(z) == esperado


def test_formato_com_expoentes():
    assert formatar(configuracao_eletronica(8).subniveis) == "1s² 2s² 2p⁴"


def test_capacidade_dos_subniveis():
    assert CAPACIDADE == {"s": 2, "p": 6, "d": 10, "f": 14}


@pytest.mark.parametrize("z, esperado", [
    (24, "1s2 2s2 2p6 3s2 3p6 3d5 4s1"),                        # Cr
    (29, "1s2 2s2 2p6 3s2 3p6 3d10 4s1"),                       # Cu
    (46, "1s2 2s2 2p6 3s2 3p6 3d10 4s2 4p6 4d10"),              # Pd
    (79, "1s2 2s2 2p6 3s2 3p6 3d10 4s2 4p6 4d10 4f14 5s2 5p6 5d10 6s1"),  # Au
])
def test_excecoes_conhecidas(z, esperado):
    cfg = configuracao_eletronica(z)
    assert cfg.excecao
    assert formatar(cfg.subniveis, expoente=False) == esperado


def test_todas_as_configuracoes_somam_z_e_respeitam_capacidade():
    for z in range(1, 103):
        subs = configuracao_eletronica(z).subniveis
        assert sum(subs.values()) == z
        assert all(e <= CAPACIDADE[sn[1]] for sn, e in subs.items())


def test_ions_simples():
    assert configuracao_eletronica(11, +1).eletrons == 10
    assert texto(11, +1) == "1s2 2s2 2p6"          # Na+ como o neônio
    assert texto(17, -1) == "1s2 2s2 2p6 3s2 3p6"  # Cl- como o argônio
    assert texto(8, -2) == "1s2 2s2 2p6"           # O2-
    assert texto(26, +2) == "1s2 2s2 2p6 3s2 3p6 3d6"  # Fe2+: o 4s sai antes do 3d


def test_cation_sem_eletrons_e_carga_impossivel():
    assert configuracao_eletronica(1, +1).eletrons == 0
    with pytest.raises(ValueError):
        configuracao_eletronica(1, +2)


def test_valencia_e_camadas():
    subs = configuracao_eletronica(8).subniveis
    assert eletrons_por_camada(subs) == {1: 2, 2: 6}
    assert eletrons_de_valencia(subs) == 6
    assert eletrons_de_valencia(configuracao_eletronica(2).subniveis) == 2


def test_diagrama_regra_de_hund_no_oxigenio():
    # 2p4: três orbitais com um elétron "para cima" e o primeiro emparelhado
    assert diagrama_orbitais(configuracao_eletronica(8).subniveis)["2p"] == [(1, 1), (1, 0), (1, 0)]


def test_diagrama_recusa_excesso_de_eletrons():
    with pytest.raises(ValueError):
        diagrama_orbitais({"2p": 7})


@pytest.mark.parametrize("z", [0, -3, 119, 3.5, "8", True])
def test_numero_atomico_invalido(z):
    with pytest.raises(ValueError):
        configuracao_eletronica(z)


@pytest.mark.parametrize("z", [103, 110, 118])
def test_elementos_sem_suporte_informam_limitacao(z):
    with pytest.raises(ConfiguracaoNaoSuportada):
        configuracao_eletronica(z)
