"""Distribuição eletrônica de átomos e íons (independente da interface).

Método: preenchimento pela ordem de Madelung (diagrama de Linus Pauling),
respeitando a capacidade de cada subnível (s=2, p=6, d=10, f=14), com uma
tabela explícita de exceções experimentais conhecidas.

Limitações documentadas:
- Só há suporte para Z de 1 a 102. Para Z >= 103 as configurações são
  incertas ou apenas previstas, então o módulo recusa o cálculo.
- Íons de elementos com exceção partem da configuração real do átomo neutro.
  Ânions seguem a ordem de Madelung, o que é uma simplificação (ver `aviso`).
"""
from dataclasses import dataclass

CAPACIDADE = {"s": 2, "p": 6, "d": 10, "f": 14}
LETRAS = "spdf"
Z_MAX_SUPORTADO = 102

# Ordem de preenchimento (regra de Madelung: n+l crescente, empate pelo menor n)
ORDEM_PREENCHIMENTO = "1s 2s 2p 3s 3p 4s 3d 4p 5s 4d 5p 6s 4f 5d 6p 7s 5f 6d 7p".split()

# Exceções experimentais: só os subníveis que diferem do preenchimento simples.
# Valores conforme as referências usuais (ex.: NIST). Conferir antes de citar.
EXCECOES = {
    24: {"3d": 5, "4s": 1},   # Cr
    29: {"3d": 10, "4s": 1},  # Cu
    41: {"4d": 4, "5s": 1},   # Nb
    42: {"4d": 5, "5s": 1},   # Mo
    44: {"4d": 7, "5s": 1},   # Ru
    45: {"4d": 8, "5s": 1},   # Rh
    46: {"4d": 10, "5s": 0},  # Pd
    47: {"4d": 10, "5s": 1},  # Ag
    57: {"4f": 0, "5d": 1},   # La
    58: {"4f": 1, "5d": 1},   # Ce
    64: {"4f": 7, "5d": 1},   # Gd
    78: {"5d": 9, "6s": 1},   # Pt
    79: {"5d": 10, "6s": 1},  # Au
    89: {"5f": 0, "6d": 1},   # Ac
    90: {"5f": 0, "6d": 2},   # Th
    91: {"5f": 2, "6d": 1},   # Pa
    92: {"5f": 3, "6d": 1},   # U
    93: {"5f": 4, "6d": 1},   # Np
    96: {"5f": 7, "6d": 1},   # Cm
}

_SUPERESCRITO = str.maketrans("0123456789", "⁰¹²³⁴⁵⁶⁷⁸⁹")


class ConfiguracaoNaoSuportada(ValueError):
    """Erro para casos em que não há resultado confiável."""


@dataclass
class Configuracao:
    z: int
    carga: int
    eletrons: int
    subniveis: dict   # ex.: {"1s": 2, "2s": 2}
    excecao: bool     # True se o átomo neutro é uma exceção à regra simples
    aviso: str        # texto de limitação (vazio quando não há)


def _chave(subnivel):
    """Ordena por camada n e depois por tipo (s, p, d, f)."""
    return int(subnivel[0]), LETRAS.index(subnivel[1])


def configuracao_eletronica(z, carga=0):
    """Calcula a configuração de um átomo neutro (carga=0) ou de um íon."""
    if not isinstance(z, int) or isinstance(z, bool) or not 1 <= z <= 118:
        raise ValueError("O número atômico deve ser um inteiro entre 1 e 118.")
    if not isinstance(carga, int) or isinstance(carga, bool):
        raise ValueError("A carga deve ser um número inteiro.")
    if z > Z_MAX_SUPORTADO:
        raise ConfiguracaoNaoSuportada(
            f"Sem suporte para Z={z}: a configuração experimental não é estabelecida "
            f"para elementos acima de Z={Z_MAX_SUPORTADO}."
        )
    eletrons = z - carga
    if eletrons < 0:
        raise ValueError(f"Carga +{carga} impossível: o átomo só tem {z} elétrons.")

    # Átomo neutro: preenche cada subnível até a capacidade (Pauli)
    restante = z
    subs = {}
    for sn in ORDEM_PREENCHIMENTO:
        if restante == 0:
            break
        qtd = min(CAPACIDADE[sn[1]], restante)
        subs[sn] = qtd
        restante -= qtd
    excecao = z in EXCECOES
    subs.update(EXCECOES.get(z, {}))
    subs = {sn: e for sn, e in subs.items() if e > 0}

    aviso = ""
    if carga > 0:
        # Cátions: os elétrons saem da camada de maior n e, dentro dela, do
        # subnível de maior l. Por isso o 4s sai antes do 3d.
        a_remover = carga
        for sn in sorted(subs, key=_chave, reverse=True):
            tirar = min(subs[sn], a_remover)
            subs[sn] -= tirar
            a_remover -= tirar
        subs = {sn: e for sn, e in subs.items() if e > 0}
    elif carga < 0:
        # Ânions: entram no primeiro subnível incompleto da ordem de Madelung
        a_adicionar = -carga
        for sn in ORDEM_PREENCHIMENTO:
            colocar = min(CAPACIDADE[sn[1]] - subs.get(sn, 0), a_adicionar)
            if colocar:
                subs[sn] = subs.get(sn, 0) + colocar
                a_adicionar -= colocar
        if a_adicionar:
            raise ConfiguracaoNaoSuportada("Carga negativa grande demais para o modelo.")
        aviso = ("Ânion calculado pela ordem de Madelung (simplificação). "
                 "Íons reais de elementos de transição podem diferir.")
    if carga != 0 and excecao:
        aviso = (aviso + " " if aviso else "") + (
            "O átomo neutro é uma exceção à regra simples; o íon parte da configuração real dele.")
    return Configuracao(z, carga, eletrons, subs, excecao, aviso)


def formatar(subniveis, expoente=True):
    """'1s² 2s² 2p⁴' (expoente=True) ou '1s2 2s2 2p4' (expoente=False)."""
    if not subniveis:
        return "(sem elétrons)"
    partes = []
    for sn in sorted(subniveis, key=_chave):
        n = str(subniveis[sn])
        partes.append(sn + (n.translate(_SUPERESCRITO) if expoente else n))
    return " ".join(partes)


def eletrons_por_camada(subniveis):
    """Total de elétrons em cada camada n. Ex.: oxigênio -> {1: 2, 2: 6}."""
    camadas = {}
    for sn, e in subniveis.items():
        camadas[int(sn[0])] = camadas.get(int(sn[0]), 0) + e
    return dict(sorted(camadas.items()))


def eletrons_de_valencia(subniveis):
    """Definição adotada: elétrons da camada de maior n ocupada (camada de valência).

    Em metais de transição os elétrons d da camada anterior também podem
    participar de ligações, e essa definição não os conta.
    """
    camadas = eletrons_por_camada(subniveis)
    return camadas[max(camadas)] if camadas else 0


def diagrama_orbitais(subniveis):
    """Retorna {subnível: [(cima, baixo), ...]} com 1 tupla por orbital.

    Regra de Hund: cada orbital recebe um elétron (spin para cima) antes de
    qualquer emparelhamento. Pauli: no máximo 2 elétrons por orbital, com
    spins opostos.
    """
    diagrama = {}
    for sn in sorted(subniveis, key=_chave):
        e = subniveis[sn]
        if e > CAPACIDADE[sn[1]]:
            raise ValueError(f"{sn} comporta no máximo {CAPACIDADE[sn[1]]} elétrons.")
        n_orbitais = CAPACIDADE[sn[1]] // 2
        orbitais = [[0, 0] for _ in range(n_orbitais)]
        for i in range(e):
            if i < n_orbitais:
                orbitais[i][0] = 1               # primeira passada: um por orbital
            else:
                orbitais[i - n_orbitais][1] = 1  # segunda passada: emparelha
        diagrama[sn] = [tuple(o) for o in orbitais]
    return diagrama


def explicacao_didatica(cfg):
    """Texto passo a passo (Markdown) de como a configuração foi obtida."""
    linhas = [f"1. O átomo neutro tem **{cfg.z}** elétrons (igual ao número atômico)."]
    if cfg.carga:
        verbo = "perde" if cfg.carga > 0 else "ganha"
        linhas.append(f"2. Como a carga é **{cfg.carga:+d}**, o íon {verbo} {abs(cfg.carga)} "
                      f"elétron(s) e fica com **{cfg.eletrons}**.")
    linhas.append("3. Os subníveis são preenchidos na ordem de Madelung ("
                  + " → ".join(ORDEM_PREENCHIMENTO[:8]) + " → ...), "
                  "respeitando as capacidades s=2, p=6, d=10, f=14 (princípio de Pauli).")
    if cfg.excecao:
        linhas.append("4. **Exceção:** a configuração experimental deste elemento difere da regra "
                      "simples (subníveis semipreenchidos ou completos ficam mais estáveis).")
    if cfg.carga > 0:
        linhas.append("4. Nos cátions, os elétrons saem primeiro da camada de maior n "
                      "(por exemplo, o 4s antes do 3d).")
    linhas.append("5. Em subníveis com vários orbitais, a regra de Hund coloca um elétron em cada "
                  "orbital antes de emparelhar (ver diagrama).")
    return "\n".join(linhas)
