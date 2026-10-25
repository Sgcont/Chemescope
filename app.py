"""Ponto de entrada do ChemScope. Execute com: streamlit run app.py"""

import streamlit as st

st.set_page_config(page_title="ChemScope", page_icon="⚛️", layout="wide")

from ui import carregar_estilo  # noqa: E402  (precisa vir depois do set_page_config)

carregar_estilo()
navegacao = st.navigation([
    st.Page("pages/inicio.py", title="Início", default=True),
    st.Page("pages/atomos.py", title="Átomos"),
    st.Page("pages/tabela_periodica.py", title="Tabela Periódica"),
    st.Page("pages/moleculas.py", title="Moléculas"),
    st.Page("pages/grafos.py", title="Grafos (experimental)"),
])
navegacao.run()
