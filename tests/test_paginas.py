"""Testes de fumaça da interface: cada página deve renderizar sem exceções."""
import pathlib

import pytest

pytest.importorskip("rdkit")
from streamlit.testing.v1 import AppTest

APP = str(pathlib.Path(__file__).resolve().parent.parent / "app.py")
PAGINAS = ["pages/inicio.py", "pages/atomos.py", "pages/tabela_periodica.py",
           "pages/moleculas.py", "pages/grafos.py"]


def abrir(pagina):
    at = AppTest.from_file(APP, default_timeout=60).run()
    return at.switch_page(pagina).run() if pagina != PAGINAS[0] else at


@pytest.mark.parametrize("pagina", PAGINAS)
def test_pagina_renderiza(pagina):
    at = abrir(pagina)
    assert not at.exception, [e.value for e in at.exception]


def test_busca_na_pagina_inicial():
    at = abrir(PAGINAS[0])
    at.text_input(key="consulta").set_value("Sódio").run()
    assert not at.exception
    assert any("Sódio" in s.value for s in at.subheader)


def test_busca_inexistente_mostra_aviso():
    at = abrir(PAGINAS[0])
    at.text_input(key="consulta").set_value("Vibranium").run()
    assert not at.exception and at.warning


def test_pagina_atomos_com_ion():
    at = abrir("pages/atomos.py")
    at.text_input(key="busca_atomo").set_value("Fe").run()
    at.number_input[0].set_value(2).run()
    assert not at.exception
    assert any("3d⁶" in m.value for m in at.markdown)
