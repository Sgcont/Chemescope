"""Moléculas como grafos: átomo = vértice, ligação = aresta.

Complexidades (V = átomos, E = ligações):
- construir o grafo: O(V + E)
- componentes conexas (BFS): O(V + E)
- número ciclomático E - V + C: O(1) depois das componentes
- ciclos fundamentais: detecção O(V + E); listar cada ciclo custa até O(V)
- comparação estrutural: O(V log V) (ordenação da sequência de graus)

Aviso científico: a topologia NÃO determina propriedades químicas completas
(geometria, polaridade, reatividade). Aqui há apenas informação estrutural.
"""
from collections import deque

from core.molecules import mol_com_hidrogenios


class GrafoMolecular:
    def __init__(self):
        self.vertices = {}   # id -> símbolo do elemento
        self.adjacencia = {}  # id -> lista de (vizinho, ordem da ligação)

    def adicionar_vertice(self, vid, simbolo):
        self.vertices[vid] = simbolo
        self.adjacencia.setdefault(vid, [])

    def adicionar_aresta(self, u, v, ordem=1.0):
        if u not in self.vertices or v not in self.vertices:
            raise ValueError("Os dois átomos precisam existir antes da ligação.")
        self.adjacencia[u].append((v, ordem))
        self.adjacencia[v].append((u, ordem))

    @classmethod
    def de_smiles(cls, smiles, hidrogenios=True):
        """Constrói o grafo via RDKit. Retorna None se o SMILES for inválido."""
        mol = mol_com_hidrogenios(smiles)
        if mol is None:
            return None
        if not hidrogenios:
            from rdkit import Chem
            mol = Chem.RemoveHs(mol)
        g = cls()
        for a in mol.GetAtoms():
            g.adicionar_vertice(a.GetIdx(), a.GetSymbol())
        for b in mol.GetBonds():
            g.adicionar_aresta(b.GetBeginAtomIdx(), b.GetEndAtomIdx(), b.GetBondTypeAsDouble())
        return g

    @property
    def n_vertices(self):
        return len(self.vertices)

    @property
    def n_arestas(self):
        return sum(len(v) for v in self.adjacencia.values()) // 2

    def lista_adjacencia(self):
        return {f"{v}:{self.vertices[v]}": [f"{w}:{self.vertices[w]}" for w, _ in viz]
                for v, viz in self.adjacencia.items()}

    def _busca_em_largura(self):
        """BFS em todas as componentes. Devolve (componentes, pai, profundidade)."""
        pai, prof, componentes = {}, {}, []
        for inicio in self.vertices:
            if inicio in prof:
                continue
            prof[inicio], pai[inicio] = 0, None
            fila, comp = deque([inicio]), []
            while fila:
                u = fila.popleft()
                comp.append(u)
                for v, _ in self.adjacencia[u]:
                    if v not in prof:
                        prof[v], pai[v] = prof[u] + 1, u
                        fila.append(v)
            componentes.append(comp)
        return componentes, pai, prof

    def componentes(self):
        return self._busca_em_largura()[0]

    def esta_conectado(self):
        return self.n_vertices > 0 and len(self.componentes()) == 1

    def ciclos(self):
        """Ciclos fundamentais: cada aresta fora da árvore da BFS fecha um ciclo."""
        _, pai, prof = self._busca_em_largura()
        resultado, vistas = [], set()
        for u in self.vertices:
            for v, _ in self.adjacencia[u]:
                aresta = frozenset((u, v))
                if aresta in vistas:
                    continue
                vistas.add(aresta)
                if pai[v] == u or pai[u] == v:
                    continue  # aresta da árvore, não fecha ciclo
                a, b = [u], [v]
                while a[-1] != b[-1]:  # sobe até o ancestral comum
                    if prof[a[-1]] >= prof[b[-1]]:
                        a.append(pai[a[-1]])
                    else:
                        b.append(pai[b[-1]])
                resultado.append(a + b[:-1][::-1])
        return resultado

    def sequencia_de_graus(self):
        return sorted(len(v) for v in self.adjacencia.values())

    def contagem_elementos(self):
        c = {}
        for s in self.vertices.values():
            c[s] = c.get(s, 0) + 1
        return c


def comparar(g1, g2):
    """Compara invariantes estruturais. Igualdade total é condição NECESSÁRIA
    para isomorfismo, mas não suficiente (não implementamos isomorfismo de grafos)."""
    r = {
        "Átomos": (g1.n_vertices, g2.n_vertices),
        "Ligações": (g1.n_arestas, g2.n_arestas),
        "Componentes": (len(g1.componentes()), len(g2.componentes())),
        "Ciclos independentes": (len(g1.ciclos()), len(g2.ciclos())),
        "Elementos": (g1.contagem_elementos(), g2.contagem_elementos()),
        "Sequência de graus": (g1.sequencia_de_graus(), g2.sequencia_de_graus()),
    }
    return {nome: {"A": a, "B": b, "igual": a == b} for nome, (a, b) in r.items()}
