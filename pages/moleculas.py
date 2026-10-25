import pandas as pd
import streamlit as st

from core.molecules import RDKIT_DISPONIVEL, buscar_molecula, listar_base, modelo_3d
from visualizations.moleculas import figura_3d, svg_2d

st.title("Moléculas")
st.write("Pesquise por nome (ex.: Água), fórmula molecular (ex.: CO2) ou SMILES (ex.: CCO).")
if not RDKIT_DISPONIVEL:
    st.warning("RDKit não está instalado: apenas fórmula, contagem de átomos e massa molar funcionam.")


@st.cache_data(show_spinner=False)
def modelo_cacheado(smiles):
    return modelo_3d(smiles)


consulta = st.text_input("Molécula", value="Água", key="busca_molecula")
st.caption("Na base local: " + ", ".join(listar_base()) + ". Se a entrada servir ao mesmo tempo como "
           "fórmula da base e SMILES (ex.: CO), vale a fórmula da base.")
if not consulta.strip():
    st.info("Digite uma molécula para começar.")
    st.stop()
m = buscar_molecula(consulta)
if m is None:
    st.warning("Molécula não encontrada. Nomes de elementos (como Oxigênio) não são moléculas: "
               "para O2, use a fórmula ou 'Oxigênio molecular'.")
    st.stop()

st.subheader(m.nome)
c1, c2, c3 = st.columns(3)
c1.metric("Fórmula", m.formula)
c2.metric("Massa molar (g/mol)", m.massa_molar)
c3.metric("Átomos no total", sum(m.contagem.values()))
st.caption(f"Origem da identificação: {m.origem}. Massa molar calculada com as massas de data/elementos.csv.")
st.markdown("**Átomos de cada elemento** (calculado)")
st.dataframe(pd.DataFrame({"Elemento": list(m.contagem), "Quantidade": list(m.contagem.values())}),
             hide_index=True)

if m.smiles:
    aba2d, aba3d, abaprop = st.tabs(["Estrutura 2D", "Modelo 3D", "Propriedades"])
    with aba2d:
        svg = svg_2d(m.smiles) if RDKIT_DISPONIVEL else None
        st.image(svg) if svg else st.info("Estrutura 2D indisponível sem RDKit.")
    with aba3d:
        with st.spinner("Gerando geometria 3D..."):
            modelo = modelo_cacheado(m.smiles) if RDKIT_DISPONIVEL else None
        if modelo:
            st.plotly_chart(figura_3d(modelo), width="stretch")
            st.caption("Coordenadas aproximadas (RDKit, campo de força MMFF), não experimentais. "
                       "Arraste para rotacionar.")
        else:
            st.info("Não foi possível gerar a geometria 3D desta molécula.")
    with abaprop:
        if m.geometria:
            st.write(f"**Geometria molecular:** {m.geometria} (informação didática simplificada, "
                     "modelo VSEPR).")
            st.write(f"**Polaridade:** {m.polaridade} (informação didática simplificada).")
        else:
            st.info("Geometria e polaridade não estão disponíveis para esta molécula: exigem dados "
                    "externos ou cálculo específico, e o ChemScope não inventa valores.")
else:
    st.info("Só a fórmula foi informada: contagem e massa molar são calculadas, mas a estrutura "
            "depende de um SMILES ou de uma molécula da base.")
st.warning("A configuração eletrônica de um átomo isolado não descreve a molécula: nas ligações, os "
           "elétrons ocupam orbitais moleculares.")
