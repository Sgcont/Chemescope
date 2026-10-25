import pandas as pd
import streamlit as st

from core.electron_configuration import (ConfiguracaoNaoSuportada, configuracao_eletronica,
                                         eletrons_de_valencia, eletrons_por_camada, formatar)
from core.periodic_table import buscar_elementos, carregar_elementos
from ui import mostrar_elemento
from visualizations.orbitais import figura_comparacao

st.title("Átomos")
aba_atomo, aba_comparar = st.tabs(["Átomo ou íon", "Comparar dois elementos"])

with aba_atomo:
    consulta = st.text_input("Elemento (nome em português, símbolo ou número atômico)", value="Oxigênio",
                             key="busca_atomo")
    carga = st.number_input("Carga do íon (0 = átomo neutro)", min_value=-5, max_value=8, value=0, step=1)
    achados = buscar_elementos(consulta)
    if not consulta.strip():
        st.info("Digite o nome, o símbolo ou o número atômico de um elemento.")
    elif not achados:
        st.warning(f"Nenhum elemento encontrado para '{consulta}'.")
    else:
        el = achados[0] if len(achados) == 1 else st.selectbox(
            "Vários elementos combinam:", achados, format_func=lambda e: f"{e.nome} ({e.simbolo})")
        mostrar_elemento(el, carga=int(carga))

with aba_comparar:
    todos = carregar_elementos()
    rotulo = lambda e: f"{e.z} - {e.nome} ({e.simbolo})"
    c1, c2 = st.columns(2)
    a = c1.selectbox("Elemento A", todos, index=7, format_func=rotulo)
    b = c2.selectbox("Elemento B", todos, index=15, format_func=rotulo)
    try:
        cfg_a, cfg_b = configuracao_eletronica(a.z), configuracao_eletronica(b.z)
    except ConfiguracaoNaoSuportada as erro:
        st.warning(str(erro))
    else:
        tabela = pd.DataFrame({
            a.simbolo: [a.z, a.massa, formatar(cfg_a.subniveis, False), eletrons_de_valencia(cfg_a.subniveis)],
            b.simbolo: [b.z, b.massa, formatar(cfg_b.subniveis, False), eletrons_de_valencia(cfg_b.subniveis)],
        }, index=["Número atômico", "Massa atômica (u)", "Configuração", "Elétrons de valência"]).astype(str)
        st.table(tabela)
        st.plotly_chart(figura_comparacao(a.simbolo, cfg_a.subniveis, b.simbolo, cfg_b.subniveis),
                        width="stretch")
        mesma = eletrons_de_valencia(cfg_a.subniveis) == eletrons_de_valencia(cfg_b.subniveis)
        st.caption("Os dois têm o mesmo número de elétrons de valência (pela definição adotada)."
                   if mesma else "Os elementos têm números diferentes de elétrons de valência.")

