# Chemescope
Aqui vai meu primeiro projeto de Química para a for_code! A ideia é criar uma plataforma para explorar elementos e moléculas, mostrando configurações eletrônicas como 1s² 2s² 2p⁴, estruturas moleculares e outras propriedades de forma visual e interativa. Bora juntar programação e Química!

Plataforma interativa e de código aberto para explorar **átomos, configurações eletrônicas, a tabela periódica, moléculas e a química representada como grafos**. Projeto acadêmico de Ciência da Computação, com interface em português do Brasil.

> Este é um projeto educacional. Os resultados didáticos não substituem referências científicas oficiais.

## Funcionalidades implementadas

- **Átomos:** busca por nome em português, símbolo ou número atômico; prótons, elétrons, distribuição por subníveis (com expoentes ou texto simples) e por camadas; elétrons de valência (definição explicada na tela); diagrama de orbitais com caixas e setas (Pauli e Hund); explicação passo a passo; comparação entre dois elementos.
- **Íons:** cátions e ânions simples (número de elétrons e configuração).
- **Tabela periódica:** 118 elementos, clique para ver detalhes, filtro por família, busca, legenda com formatos de marcador diferentes (não depende só de cor) e lista textual das famílias.
- **Moléculas:** busca por nome, fórmula ou SMILES; contagem de átomos, massa molar, estrutura 2D, modelo 3D rotacionável e, para moléculas pequenas da base local, geometria e polaridade didáticas.
- **Grafos (experimental):** lista de adjacência, número de átomos e ligações, conectividade, ciclos e comparação estrutural entre duas moléculas.
- **Testes automatizados** (`pytest`) para os cálculos químicos, o grafo e a renderização das páginas.

## Tecnologias

Python, Streamlit (interface), RDKit (estruturas moleculares), Plotly (gráficos e modelo 3D), Pandas (tabelas) e Pytest. O modelo 3D usa Plotly com coordenadas do RDKit, então não há biblioteca 3D extra. Não há API paga nem serviço externo: tudo roda localmente.

## Estrutura do projeto

```
chemscope/
├── app.py                      # ponto de entrada e navegação
├── ui.py                       # componentes de interface reutilizados
├── pages/                      # inicio, atomos, tabela_periodica, moleculas, grafos
├── core/                       # lógica científica, sem dependência do Streamlit
│   ├── electron_configuration.py
│   ├── periodic_table.py
│   ├── molecules.py
│   └── molecular_graph.py
├── data/                       # elementos.csv e moleculas.json
├── visualizations/             # figuras Plotly e desenhos moleculares
├── tests/
├── assets/
├── .streamlit/config.toml
├── .github/workflows/testes.yml
├── requirements.txt
├── LICENSE
└── README.md
```

## Instalação (Windows)

Requer Python 3.10 ou superior.

```powershell
git clone https://github.com/SEU_USUARIO/chemscope.git
cd chemscope
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Em Linux ou macOS, ative o ambiente com `source .venv/bin/activate`.

## Executar localmente

```bash
streamlit run app.py
```

## Executar os testes

```bash
python -m pytest
```

## Fontes dos dados e limitações

- `data/elementos.csv` (símbolo, nome em português, massa atômica): **compilação manual**, digitada pelo autor do projeto com valores abreviados no estilo IUPAC, **sem conferência automática com a fonte oficial**. Confira com o CIAAW/IUPAC e o NIST antes de usar academicamente. Para elementos sem isótopo estável, a massa é o número de massa de um isótopo escolhido (valor inteiro).
- Famílias químicas: classificação convencional feita no código (`core/periodic_table.py`). Para Z de 109 a 118 ela é prevista, não confirmada.
- Configurações eletrônicas: ordem de Madelung mais uma tabela de exceções (Cr, Cu, Nb, Mo, Ru, Rh, Pd, Ag, La, Ce, Gd, Pt, Au, Ac, Th, Pa, U, Np, Cm), conforme referências usuais. **Há suporte só para Z de 1 a 102**; acima disso o app informa a limitação em vez de calcular. A tabela de exceções deve ser conferida contra o NIST.
- Elétrons de valência: definidos como os elétrons da camada de maior n. Em metais de transição isso é uma simplificação.
- Ânions usam a ordem de Madelung (simplificação). Íons de metais de transição com carga negativa podem divergir da realidade.
- `data/moleculas.json`: lista pequena e curada à mão. Geometria e polaridade existem só para moléculas simples e são **didáticas**. Para as demais, o app diz que a informação não está disponível.
- Modelo 3D: coordenadas aproximadas do RDKit (ETKDG + MMFF), não experimentais. Ângulos e distâncias não são exibidos como dados.
- Grafos: só informação estrutural. Comparação por invariantes (não implementa isomorfismo de grafos). Complexidades estão descritas em `core/molecular_graph.py` e na própria página.
- A seleção por clique na tabela periódica depende do suporte a seleção do Plotly no Streamlit. A busca e o filtro funcionam como alternativa.

## Implantação

**Streamlit Community Cloud** (gratuito para repositórios públicos): publique o repositório no GitHub, entre em share.streamlit.io, escolha o repositório, a branch `main` e o arquivo principal `app.py`. Não há chaves nem credenciais: o projeto não usa segredos. Se algum dia usar, guarde-os em `.streamlit/secrets.toml` (já está no `.gitignore`) ou nas configurações de segredos do serviço.

**Por que não GitHub Pages?** O GitHub Pages hospeda apenas sites estáticos (HTML, CSS e JavaScript). O ChemScope é uma aplicação Python que precisa de um servidor executando código. O GitHub Pages pode servir futuramente uma página institucional do projeto, apontando para a aplicação hospedada em outro serviço.

## Ideias para contribuições

- Ampliar e validar os dados dos elementos com uma fonte oficial citada (e adicionar eletronegatividade, raios etc.).
- Notação de gás nobre (por exemplo, `[Ne] 3s¹`).
- Isomorfismo de grafos para comparar estruturas de verdade.
- Cálculo de polaridade e geometria com método documentado.
- Mais moléculas na base e leitura de arquivos SDF/MOL.
- Tradução da interface e testes visuais.

## Licença

MIT. Veja o arquivo `LICENSE`. A licença MIT permite usar, copiar, modificar e distribuir o código, inclusive comercialmente, desde que o aviso de copyright seja mantido, e não oferece garantia.
