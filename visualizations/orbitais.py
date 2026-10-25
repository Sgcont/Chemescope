"""Gráficos de distribuição eletrônica (Plotly)."""
import plotly.graph_objects as go

from core.electron_configuration import ORDEM_PREENCHIMENTO, eletrons_por_camada


def figura_diagrama_orbitais(diagrama):
    """Caixas e setas: cada caixa é um orbital, seta para cima e para baixo são spins opostos.

    Aviso: as caixas representam orbitais (regiões de probabilidade), não
    trajetórias dos elétrons.
    """
    fig = go.Figure()
    subniveis = sorted(diagrama, key=ORDEM_PREENCHIMENTO.index)
    for linha, sn in enumerate(subniveis):
        fig.add_annotation(x=-0.3, y=linha, text=f"<b>{sn}</b>", showarrow=False, xanchor="right")
        for i, (cima, baixo) in enumerate(diagrama[sn]):
            x0 = i * 1.2
            fig.add_shape(type="rect", x0=x0, x1=x0 + 1, y0=linha - 0.4, y1=linha + 0.4,
                          line=dict(color="#4f6d8f", width=2))
            if cima:
                fig.add_annotation(x=x0 + 0.3, y=linha, text="↑", showarrow=False, font=dict(size=22))
            if baixo:
                fig.add_annotation(x=x0 + 0.7, y=linha, text="↓", showarrow=False, font=dict(size=22))
    max_orb = max((len(o) for o in diagrama.values()), default=1)
    fig.update_xaxes(visible=False, range=[-1.2, max_orb * 1.2 + 0.2])
    fig.update_yaxes(visible=False, range=[-0.8, len(subniveis) - 0.2])
    fig.update_layout(height=max(160, 56 * len(subniveis) + 40), margin=dict(l=0, r=0, t=10, b=0),
                      plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
    return fig


def figura_camadas(subniveis, titulo="Elétrons por camada"):
    camadas = eletrons_por_camada(subniveis)
    fig = go.Figure(go.Bar(x=[f"n={n}" for n in camadas], y=list(camadas.values()),
                           text=list(camadas.values()), textposition="outside",
                           marker_color="#4f6d8f"))
    fig.update_layout(title=titulo, yaxis_title="Elétrons", height=300, margin=dict(t=50, b=10))
    return fig


def figura_comparacao(rotulo_a, subs_a, rotulo_b, subs_b):
    """Barras lado a lado com os elétrons de cada camada de dois elementos."""
    ca, cb = eletrons_por_camada(subs_a), eletrons_por_camada(subs_b)
    camadas = sorted(set(ca) | set(cb))
    fig = go.Figure()
    for rotulo, c, cor in ((rotulo_a, ca, "#4f6d8f"), (rotulo_b, cb, "#d98c3f")):
        fig.add_bar(name=rotulo, x=[f"n={n}" for n in camadas], y=[c.get(n, 0) for n in camadas],
                    marker_color=cor, text=[c.get(n, 0) for n in camadas], textposition="outside")
    fig.update_layout(barmode="group", height=320, yaxis_title="Elétrons", margin=dict(t=30, b=10))
    return fig
