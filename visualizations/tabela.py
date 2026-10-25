"""Tabela periódica interativa (Plotly). Cada categoria é uma série, então a
legenda funciona como filtro; símbolos diferentes por categoria ajudam quem
não distingue cores."""
import plotly.graph_objects as go

from core.periodic_table import carregar_elementos

ESTILO = {  # categoria -> (cor, símbolo do marcador)
    "Metal alcalino": ("#e4572e", "square"),
    "Metal alcalino-terroso": ("#f3a712", "diamond"),
    "Metal de transição": ("#76b041", "circle"),
    "Lantanídeo": ("#2e9cca", "hexagon"),
    "Actinídeo": ("#7b6cd9", "pentagon"),
    "Outros metais": ("#8d99ae", "octagon"),
    "Semimetal": ("#4ecdc4", "triangle-up"),
    "Não metal": ("#ffd166", "star"),
    "Halogênio": ("#ef476f", "hexagram"),
    "Gás nobre": ("#9d4edd", "bowtie"),
}


def figura_tabela(categorias=None, destaque_z=None):
    categorias = categorias or list(ESTILO)
    fig = go.Figure()
    elementos = carregar_elementos()
    for cat, (cor, simbolo) in ESTILO.items():
        if cat not in categorias:
            continue
        grupo = [e for e in elementos if e.categoria == cat]
        fig.add_trace(go.Scatter(
            x=[e.coluna for e in grupo], y=[-e.linha for e in grupo], mode="markers+text",
            name=f"{cat} ({simbolo})", text=[e.simbolo for e in grupo],
            customdata=[[e.z] for e in grupo], textfont=dict(size=11, color="black"),
            marker=dict(size=34, color=cor, symbol=simbolo, opacity=0.95,
                        line=dict(width=3 if e_destaque(grupo, destaque_z) else 1, color="black")),
            hovertemplate="<b>%{text}</b> (Z=%{customdata[0]})<br>" + cat + "<extra></extra>",
        ))
    fig.update_xaxes(visible=False, range=[0.3, 18.7], fixedrange=True)
    fig.update_yaxes(visible=False, range=[-10.6, -0.4], fixedrange=True)
    fig.update_layout(height=520, margin=dict(l=0, r=0, t=10, b=0), legend=dict(orientation="h", y=-0.02),
                      clickmode="event+select", dragmode=False)
    return fig


def e_destaque(grupo, z):
    return z is not None and any(e.z == z for e in grupo)
