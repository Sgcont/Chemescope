"""Componentes de interface reutilizados pelas páginas."""
import pandas as pd
import streamlit as st

from core.electron_configuration import (ConfiguracaoNaoSuportada, configuracao_eletronica,
                                         diagrama_orbitais, eletrons_de_valencia, explicacao_didatica,
                                         formatar)
from visualizations.orbitais import figura_camadas, figura_diagrama_orbitais

CSS = """
<style>
h1, h2, h3 { letter-spacing: -0.01em; }
.chem-config { font-size: 1.6rem; font-weight: 600; padding: .4rem .8rem; border-radius: 8px;
               background: rgba(79,109,143,.15); display: inline-block; }
.chem-tag { font-size: .8rem; padding: 2px 8px; border-radius: 10px; background: rgba(79,109,143,.25); }
</style>
"""


def carregar_estilo():
    st.markdown(CSS, unsafe_allow_html=True)


def mostrar_elemento(el, carga=0, completo=True):
    """Mostra todos os dados de um elemento (ou de um íon dele)."""
    st.subheader(f"{el.nome} ({el.simbolo})")
    st.markdown(f"<span class='chem-tag'>{el.categoria}</span> "
                f"<span class='chem-tag'>Período {el.periodo}</span>", unsafe_allow_html=True)
    try:
        cfg = configuracao_eletronica(el.z, carga)
    except ConfiguracaoNaoSuportada as erro:
        st.warning(f"Número atômico {el.z} e massa {el.massa}. {erro}")
        return
    except ValueError as erro:
        st.error(str(erro))
        return
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Número atômico", el.z)
    c2.metric("Prótons", el.z)
    c3.metric("Elétrons", cfg.eletrons)
    c4.metric("Massa atômica (u)", el.massa)
    st.markdown("**Configuração eletrônica**")
    st.markdown(f"<div class='chem-config'>{formatar(cfg.subniveis)}</div>", unsafe_allow_html=True)
    st.caption("Texto simples: " + formatar(cfg.subniveis, expoente=False))
    val = eletrons_de_valencia(cfg.subniveis)
    st.write(f"**Elétrons de valência:** {val}. Definição adotada: elétrons da camada de maior n "
             "ocupada. Em metais de transição, elétrons d da camada anterior também podem participar "
             "de ligações e não entram nessa contagem.")
    if cfg.aviso:
        st.info(cfg.aviso)
    if cfg.excecao and carga == 0:
        st.info("Este elemento é uma **exceção** à ordem de preenchimento simples.")
    if not completo:
        return
    aba1, aba2, aba3 = st.tabs(["Diagrama de orbitais", "Camadas", "Como foi obtida"])
    with aba1:
        if cfg.subniveis:
            st.plotly_chart(figura_diagrama_orbitais(diagrama_orbitais(cfg.subniveis)),
                            width="stretch", key=f"orb{el.z}{carga}")
            st.caption("Cada caixa é um orbital; ↑ e ↓ são spins opostos. As caixas representam "
                       "orbitais (regiões de probabilidade), não trajetórias dos elétrons.")
        else:
            st.write("Íon sem elétrons.")
    with aba2:
        if cfg.subniveis:
            st.plotly_chart(figura_camadas(cfg.subniveis), width="stretch", key=f"cam{el.z}{carga}")
    with aba3:
        st.markdown(explicacao_didatica(cfg))


def tabela_resumo(subniveis_por_nome):
    return pd.DataFrame(subniveis_por_nome)
