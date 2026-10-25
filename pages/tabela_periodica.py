import streamlit as st

from core.periodic_table import buscar_elementos, carregar_elementos
from ui import mostrar_elemento
from visualizations.tabela import ESTILO, figura_tabela

st.title("Tabela Periódica")
st.write("Clique em um elemento (ou use a busca) para ver os detalhes. A legenda filtra as famílias, "
         "e cada família usa um formato de marcador diferente além da cor.")

categorias = st.multiselect("Famílias exibidas", list(ESTILO), default=list(ESTILO))
busca = st.text_input("Buscar por símbolo, nome ou número atômico", key="busca_tabela")

z_selecionado = None
achados = buscar_elementos(busca) if busca.strip() else []
if busca.strip() and not achados:
    st.warning("Nenhum elemento encontrado.")
elif achados:
    z_selecionado = achados[0].z

if not categorias:
    st.info("Selecione ao menos uma família para exibir a tabela.")
else:
    evento = st.plotly_chart(figura_tabela(categorias, z_selecionado), width="stretch",
                             on_select="rerun", selection_mode="points", key="tabela")
    pontos = evento.selection.points if evento and evento.selection else []
    if pontos and not achados:
        dados = pontos[0].get("customdata")
        z_selecionado = dados[0] if isinstance(dados, (list, tuple)) else dados

if z_selecionado:
    mostrar_elemento(carregar_elementos()[int(z_selecionado) - 1])
else:
    st.info("Nenhum elemento selecionado.")
with st.expander("Lista textual (acessível) das famílias"):
    for cat in ESTILO:
        st.write(f"**{cat}:** " + ", ".join(e.simbolo for e in carregar_elementos() if e.categoria == cat))
st.caption("Elementos de Z 109 a 118: a classificação em famílias é prevista, não confirmada experimentalmente.")
