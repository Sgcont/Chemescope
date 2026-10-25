import pandas as pd
import streamlit as st

from core.molecular_graph import GrafoMolecular, comparar
from core.molecules import RDKIT_DISPONIVEL, buscar_molecula

st.title("Grafos químicos (experimental)")
st.write("Cada átomo é um vértice e cada ligação é uma aresta. A topologia mostra apenas **estrutura**: "
         "propriedades como geometria, polaridade e reatividade exigem métodos adicionais.")
if not RDKIT_DISPONIVEL:
    st.error("Esta seção precisa do RDKit para ler a estrutura das moléculas.")
    st.stop()

hidrogenios = st.checkbox("Incluir hidrogênios como vértices", value=True)


def carregar_grafo(consulta):
    m = buscar_molecula(consulta)
    if m is None or not m.smiles:
        return None, m
    return GrafoMolecular.de_smiles(m.smiles, hidrogenios), m


consulta = st.text_input("Molécula (nome, fórmula da base ou SMILES)", value="Etanol", key="grafo_a")
g, m = carregar_grafo(consulta)
if not consulta.strip():
    st.info("Digite uma molécula.")
elif g is None:
    st.warning("Não foi possível montar o grafo: molécula não encontrada ou sem estrutura (só fórmula).")
else:
    st.subheader(m.nome)
    c1, c2, c3, c4 = st.columns(4)
    ciclos = g.ciclos()
    c1.metric("Átomos (vértices)", g.n_vertices)
    c2.metric("Ligações (arestas)", g.n_arestas)
    c3.metric("Conexo?", "Sim" if g.esta_conectado() else "Não")
    c4.metric("Ciclos independentes", len(ciclos))
    st.markdown("**Lista de adjacência**")
    st.dataframe(pd.DataFrame({"Vértice": list(g.lista_adjacencia()),
                               "Vizinhos": [", ".join(v) for v in g.lista_adjacencia().values()]}),
                 hide_index=True)
    if ciclos:
        for c in ciclos:
            st.write("Ciclo: " + " → ".join(f"{v}:{g.vertices[v]}" for v in c))
    with st.expander("Complexidade dos algoritmos"):
        st.markdown("- Construção, BFS e componentes: **O(V + E)**\n"
                    "- Detecção de ciclos fundamentais: **O(V + E)** (listar cada ciclo custa até O(V))\n"
                    "- Comparação por sequência de graus: **O(V log V)**")

    st.markdown("### Comparação estrutural")
    consulta_b = st.text_input("Segunda molécula", value="Metanol", key="grafo_b")
    g2, m2 = carregar_grafo(consulta_b)
    if consulta_b.strip() and g2 is None:
        st.warning("Segunda molécula não encontrada ou sem estrutura.")
    elif g2 is not None:
        r = comparar(g, g2)
        st.dataframe(pd.DataFrame({"Propriedade": list(r), m.nome: [str(v["A"]) for v in r.values()],
                                   m2.nome: [str(v["B"]) for v in r.values()],
                                   "Igual?": ["Sim" if v["igual"] else "Não" for v in r.values()]}),
                     hide_index=True)
        st.caption("Invariantes iguais são necessários, mas não suficientes para dizer que duas moléculas "
                   "têm a mesma estrutura (isomorfismo não é implementado). Isômeros, por exemplo, "
                   "podem ter os mesmos números e ainda assim ser diferentes.")
