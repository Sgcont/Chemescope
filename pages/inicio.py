import streamlit as st

from core.molecules import buscar_molecula
from core.periodic_table import buscar_elementos
from ui import mostrar_elemento

EXEMPLOS = ["Oxigênio", "Na", "26", "H2O", "Dióxido de carbono", "CCO"]

st.title("⚛️ ChemScope")
st.write("Plataforma interativa e de código aberto para explorar átomos, configurações eletrônicas, "
         "a tabela periódica, moléculas e a química vista como grafos.")


def usar_exemplo(texto):
    st.session_state["consulta"] = texto


consulta = st.text_input("Pesquise um elemento (nome, símbolo ou número) ou uma molécula "
                         "(nome, fórmula ou SMILES)", key="consulta", placeholder="Ex.: Oxigênio, Na, 11, H2O")
colunas = st.columns(len(EXEMPLOS))
for col, ex in zip(colunas, EXEMPLOS):
    col.button(ex, on_click=usar_exemplo, args=(ex,), width="stretch")

if consulta.strip():
    with st.spinner("Buscando..."):
        elementos = buscar_elementos(consulta)
        molecula = buscar_molecula(consulta)
    if not elementos and molecula is None:
        st.warning("Nada encontrado. Confira a grafia ou tente outro formato (nome, símbolo, número, "
                   "fórmula ou SMILES).")
    if elementos:
        st.markdown("### Elemento")
        escolhido = elementos[0] if len(elementos) == 1 else st.selectbox(
            "Vários elementos combinam. Escolha um:", elementos, format_func=lambda e: f"{e.nome} ({e.simbolo})")
        mostrar_elemento(escolhido, completo=False)
    if molecula:
        st.markdown("### Molécula")
        st.write(f"**{molecula.nome}**: fórmula {molecula.formula}, massa molar {molecula.massa_molar} g/mol.")
        st.caption("Veja estrutura, 3D e grafo nas seções Moléculas e Grafos.")
else:
    st.info("Digite algo acima ou escolha um exemplo para começar.")

st.markdown("### Seções")
a, b, c, d = st.columns(4)
a.page_link("pages/atomos.py", label="Átomos")
b.page_link("pages/tabela_periodica.py", label="Tabela Periódica")
c.page_link("pages/moleculas.py", label="Moléculas")
d.page_link("pages/grafos.py", label="Grafos")
