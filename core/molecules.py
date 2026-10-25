"""Moléculas: busca, contagem de átomos, massa molar e estrutura 3D.

Origem de cada informação (mantida separada de propósito):
- calculado: contagem de átomos, massa molar (a partir de data/elementos.csv)
  e coordenadas 3D (RDKit, ETKDG + MMFF, aproximadas).
- base local: nome, fórmula e SMILES de data/moleculas.json.
- didático: geometria e polaridade (só para moléculas pequenas e bem conhecidas).
"""
import json
import re
import unicodedata
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from core.periodic_table import carregar_elementos

try:
    from rdkit import Chem
    from rdkit.Chem import AllChem
    RDKIT_DISPONIVEL = True
except ImportError:  # modo básico: fórmula, contagem e massa funcionam sem RDKit
    RDKIT_DISPONIVEL = False

CAMINHO_JSON = Path(__file__).resolve().parent.parent / "data" / "moleculas.json"


@dataclass
class Molecula:
    nome: str
    formula: str
    contagem: dict          # {"H": 2, "O": 1}
    massa_molar: float      # g/mol
    smiles: str = ""        # vazio quando só a fórmula foi informada
    origem: str = ""        # "base local", "SMILES informado" ou "fórmula informada"
    geometria: str = ""     # didático, só para moléculas da base
    polaridade: str = ""    # didático, só para moléculas da base


def contar_atomos(formula):
    """'Ca(OH)2' -> {'Ca': 1, 'O': 2, 'H': 2}. Aceita parênteses."""
    formula = (formula or "").strip()
    if not formula:
        raise ValueError("Informe uma fórmula molecular.")
    simbolos = {e.simbolo for e in carregar_elementos()}
    tokens = re.findall(r"[A-Z][a-z]?|\d+|\(|\)", formula)
    if "".join(tokens) != formula:
        raise ValueError(f"Fórmula inválida: '{formula}'.")
    pilha = [{}]
    i = 0
    while i < len(tokens):
        t = tokens[i]
        # multiplicador opcional logo depois do átomo ou do parêntese
        tem_numero = i + 1 < len(tokens) and tokens[i + 1].isdigit()
        mult = int(tokens[i + 1]) if tem_numero else 1
        if t == "(":
            pilha.append({})
            i += 1
        elif t == ")":
            if len(pilha) == 1:
                raise ValueError("Parênteses não balanceados.")
            grupo = pilha.pop()
            for s, n in grupo.items():
                pilha[-1][s] = pilha[-1].get(s, 0) + n * mult
            i += 2 if tem_numero else 1
        elif t.isdigit():
            raise ValueError(f"Número inesperado em '{formula}'.")
        else:
            if t not in simbolos:
                raise ValueError(f"Símbolo químico inexistente: '{t}'.")
            pilha[-1][t] = pilha[-1].get(t, 0) + mult
            i += 2 if tem_numero else 1
    if len(pilha) != 1:
        raise ValueError("Parênteses não balanceados.")
    return pilha[0]


def massa_molar(contagem):
    """Soma das massas atômicas (g/mol) de cada átomo da contagem."""
    massas = {e.simbolo: e.massa for e in carregar_elementos()}
    return round(sum(massas[s] * n for s, n in contagem.items()), 3)


def formula_de_hill(contagem):
    """Notação de Hill: C primeiro, H em seguida, resto em ordem alfabética."""
    ordem = [s for s in ("C", "H") if s in contagem] if "C" in contagem else []
    ordem += sorted(s for s in contagem if s not in ordem)
    return "".join(s + (str(contagem[s]) if contagem[s] > 1 else "") for s in ordem)


def _normalizar(texto):
    sem_acento = unicodedata.normalize("NFD", texto.strip().lower())
    return "".join(c for c in sem_acento if unicodedata.category(c) != "Mn")


@lru_cache(maxsize=1)
def _base_local():
    with open(CAMINHO_JSON, encoding="utf-8") as arq:
        return json.load(arq)


def listar_base():
    return [m["nome"] for m in _base_local()]


def mol_com_hidrogenios(smiles):
    """Objeto RDKit com hidrogênios explícitos, ou None se o SMILES for inválido."""
    if not RDKIT_DISPONIVEL or not smiles:
        return None
    mol = Chem.MolFromSmiles(smiles)
    return Chem.AddHs(mol) if mol is not None else None


def _molecula_de_registro(reg):
    contagem = contar_atomos(reg["formula"])
    return Molecula(reg["nome"], reg["formula"], contagem, massa_molar(contagem), reg["smiles"],
                    "base local", reg.get("geometria", ""), reg.get("polaridade", ""))


def buscar_molecula(consulta):
    """Procura por nome, fórmula, SMILES ou (por último) só fórmula.

    Prioridade: nome na base, fórmula exata na base, SMILES válido, fórmula
    sem estrutura. Se a entrada for ao mesmo tempo fórmula da base e SMILES
    (ex.: 'CO'), vale a fórmula da base. Retorna None se nada for encontrado.
    """
    texto = (consulta or "").strip()
    if not texto:
        return None
    for reg in _base_local():
        if _normalizar(reg["nome"]) == _normalizar(texto):
            return _molecula_de_registro(reg)
    for reg in _base_local():
        if reg["formula"] == texto:
            return _molecula_de_registro(reg)
    mol = mol_com_hidrogenios(texto) if " " not in texto else None
    if mol is not None:
        contagem = {}
        for atomo in mol.GetAtoms():
            contagem[atomo.GetSymbol()] = contagem.get(atomo.GetSymbol(), 0) + 1
        return Molecula("Molécula a partir de SMILES", formula_de_hill(contagem), contagem,
                        massa_molar(contagem), texto, "SMILES informado")
    try:
        contagem = contar_atomos(texto)
    except ValueError:
        return None
    return Molecula("Fórmula informada (sem estrutura)", texto, contagem, massa_molar(contagem),
                    "", "fórmula informada")


def modelo_3d(smiles):
    """Coordenadas 3D aproximadas (RDKit ETKDG + MMFF) ou None se não for possível.

    Retorna {"atomos": [(símbolo, x, y, z)], "ligacoes": [(i, j, ordem)]}.
    As coordenadas vêm de um modelo de campo de força, não de um experimento.
    """
    mol = mol_com_hidrogenios(smiles)
    if mol is None or AllChem.EmbedMolecule(mol, randomSeed=42) != 0:
        return None
    try:
        AllChem.MMFFOptimizeMolecule(mol)
    except Exception:
        pass  # sem parâmetros MMFF para algum átomo: mantém a geometria do ETKDG
    pos = mol.GetConformer().GetPositions()
    return {
        "atomos": [(a.GetSymbol(), *map(float, pos[a.GetIdx()])) for a in mol.GetAtoms()],
        "ligacoes": [(b.GetBeginAtomIdx(), b.GetEndAtomIdx(), b.GetBondTypeAsDouble())
                     for b in mol.GetBonds()],
    }
