"""Dados e busca de elementos químicos (independente da interface).

Fonte dos dados: data/elementos.csv (ver README, seção "Fontes dos dados").
"""
import csv
import unicodedata
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

CAMINHO_CSV = Path(__file__).resolve().parent.parent / "data" / "elementos.csv"
FIM_DE_PERIODO = [2, 10, 18, 36, 54, 86, 118]

_CATEGORIAS = {
    "Metal alcalino": {3, 11, 19, 37, 55, 87},
    "Metal alcalino-terroso": {4, 12, 20, 38, 56, 88},
    "Semimetal": {5, 14, 32, 33, 51, 52},
    "Não metal": {1, 6, 7, 8, 15, 16, 34},
    "Halogênio": {9, 17, 35, 53, 85, 117},
    "Gás nobre": {2, 10, 18, 36, 54, 86, 118},
    "Outros metais": {13, 31, 49, 50, 81, 82, 83, 84, 113, 114, 115, 116},
}


@dataclass(frozen=True)
class Elemento:
    z: int
    simbolo: str
    nome: str
    massa: float
    categoria: str
    periodo: int
    linha: int    # linha no desenho da tabela (lantanídeos e actinídeos ficam abaixo)
    coluna: int


def _categoria(z):
    for nome, conjunto in _CATEGORIAS.items():
        if z in conjunto:
            return nome
    if 57 <= z <= 71:
        return "Lantanídeo"
    if 89 <= z <= 103:
        return "Actinídeo"
    return "Metal de transição"


def _posicao(z):
    """Retorna (período, linha, coluna) no desenho da tabela de 18 colunas."""
    periodo = next(p for p, fim in enumerate(FIM_DE_PERIODO, start=1) if z <= fim)
    inicio = FIM_DE_PERIODO[periodo - 2] + 1 if periodo > 1 else 1
    idx = z - inicio
    if periodo == 1:
        return 1, 1, 1 if z == 1 else 18
    if periodo in (2, 3):
        return periodo, periodo, idx + 1 if idx < 2 else idx + 11
    if periodo in (4, 5):
        return periodo, periodo, idx + 1
    if idx < 2:
        return periodo, periodo, idx + 1
    if 57 <= z <= 71:
        return 6, 9, z - 57 + 3
    if 89 <= z <= 103:
        return 7, 10, z - 89 + 3
    # após os blocos f, o período volta ao grupo 4 (Hf = 72, Rf = 104)
    return periodo, periodo, z - (72 if periodo == 6 else 104) + 4


@lru_cache(maxsize=1)
def carregar_elementos():
    """Lê o CSV uma única vez e devolve a lista de 118 elementos."""
    elementos = []
    with open(CAMINHO_CSV, encoding="utf-8", newline="") as arq:
        for linha in csv.DictReader(arq):
            z = int(linha["z"])
            periodo, lin, col = _posicao(z)
            elementos.append(Elemento(z, linha["simbolo"], linha["nome"], float(linha["massa"]),
                                      _categoria(z), periodo, lin, col))
    return elementos


def _normalizar(texto):
    """Minúsculas e sem acentos, para 'Oxigenio' encontrar 'Oxigênio'."""
    sem_acento = unicodedata.normalize("NFD", texto.strip().lower())
    return "".join(c for c in sem_acento if unicodedata.category(c) != "Mn")


def buscar_elementos(consulta):
    """Busca por número atômico, símbolo ou nome em português.

    Retorna lista vazia para entrada vazia ou elemento inexistente. Um símbolo,
    número ou nome exato retorna só esse elemento; senão, nomes que começam
    com o texto (mínimo de 2 letras) são sugeridos.
    """
    texto = _normalizar(consulta or "")
    if not texto:
        return []
    elementos = carregar_elementos()
    if texto.isdigit():
        return [e for e in elementos if e.z == int(texto)]
    exatos = [e for e in elementos if _normalizar(e.simbolo) == texto or _normalizar(e.nome) == texto]
    if exatos:
        return exatos
    if len(texto) >= 2:
        return [e for e in elementos if _normalizar(e.nome).startswith(texto)]
    return []


def elemento_por_simbolo(simbolo):
    for e in carregar_elementos():
        if e.simbolo == simbolo:
            return e
    return None
