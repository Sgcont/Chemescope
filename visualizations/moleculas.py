"""Visualizações de moléculas: 2D (SVG do RDKit) e 3D rotacionável (Plotly)."""
import plotly.graph_objects as go

from core.molecules import mol_com_hidrogenios

CORES = {"H": "#d9d9d9", "C": "#404040", "N": "#3050f8", "O": "#e02020", "F": "#50c850",
         "Cl": "#1ff01f", "S": "#e0c000", "P": "#ff8000", "Br": "#a62929"}
RAIOS = {"H": 8, "C": 16, "N": 15, "O": 15}


def svg_2d(smiles, largura=380, altura=280):
    """Desenho 2D (átomos e ligações) em SVG, ou None se o SMILES for inválido."""
    from rdkit import Chem
    from rdkit.Chem.Draw import rdMolDraw2D
    mol = mol_com_hidrogenios(smiles)
    if mol is None:
        return None
    mol = Chem.RemoveHs(mol)
    desenho = rdMolDraw2D.MolDraw2DSVG(largura, altura)
    desenho.DrawMolecule(mol)
    desenho.FinishDrawing()
    return desenho.GetDrawingText()


def figura_3d(modelo):
    """Esferas (átomos) e linhas (ligações) com rotação pelo mouse ou toque."""
    atomos, ligacoes = modelo["atomos"], modelo["ligacoes"]
    fig = go.Figure()
    for i, j, ordem in ligacoes:
        a, b = atomos[i], atomos[j]
        fig.add_trace(go.Scatter3d(x=[a[1], b[1]], y=[a[2], b[2]], z=[a[3], b[3]], mode="lines",
                                   line=dict(width=4 + 3 * (ordem - 1), color="#888"),
                                   hoverinfo="skip", showlegend=False))
    fig.add_trace(go.Scatter3d(
        x=[a[1] for a in atomos], y=[a[2] for a in atomos], z=[a[3] for a in atomos],
        mode="markers+text", text=[a[0] for a in atomos], textposition="top center",
        marker=dict(size=[RAIOS.get(a[0], 14) for a in atomos],
                    color=[CORES.get(a[0], "#b565a7") for a in atomos], line=dict(width=1, color="black")),
        hovertemplate="%{text}<extra></extra>", showlegend=False))
    fig.update_layout(height=420, margin=dict(l=0, r=0, t=0, b=0),
                      scene=dict(xaxis_visible=False, yaxis_visible=False, zaxis_visible=False,
                                 aspectmode="data"))
    return fig
