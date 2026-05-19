# Padroes da Biblioteca 3D e 2D - Workbench Eletrica BIM

Este documento descreve os padroes de geometria, catalogo e insercao inteligente usados pela bancada Eletrica.

---

## 1. Estrutura De Pastas

```text
Library/
├── 3D/
│   ├── Tomadas/             # Tomadas simples, duplas, triplas (.FCStd e .brep)
│   └── Conjuntos_Modulares/ # Placas combinadas (interruptor + tomada, etc.)
├── 2D/
│   └── Conjuntos_Modulares/ # Simbolos 2D proprios de conjuntos, se houver
└── FamilyCatalog/
    └── families.toml        # Metadados BIM de todas as familias
```

Os modelos `.FCStd` ficam na subpasta correspondente. Versoes `.brep` da mesma geometria
sao priorizadas por serem muito mais rapidas de carregar. O sistema procura `.brep` primeiro;
se nao encontrar, abre o `.FCStd` e exporta o solido principal para o cache em memoria.

---

## 2. Padrao De Origem Dos Modelos 3D

Todo modelo 3D da biblioteca deve ter sua **origem geometrica no centro** do volume:

- X = 0: centro horizontal da placa/caixa
- Y = 0: centro de profundidade do corpo
- Z = 0: centro vertical

O motor de insercao centraliza automaticamente o modelo pelo bounding box ao carregar:

```python
best_s.translate(App.Vector(-center.x, -center.y, -center.z))
```

Isso garante que o ponto de insercao (cursor do mouse) corresponda ao centro geometrico
do objeto em planta. Nao use offsets fixos de origem nos modelos da biblioteca.

---

## 3. Separacao 3D e 2D (Arquitetura Atual)

A simbologia NBR 5444 **nao e embutida na geometria 3D**. Sao objetos separados:

| Objeto | Tipo FreeCAD | Conteudo |
|---|---|---|
| Tomada Matriz | `Part::FeaturePython` | Geometria 3D pura (sem simbolo) |
| Tomada Instancia | `Part::Feature` | Copia 3D da matriz |
| Simbolo 2D | `Part::Feature` | Simbologia NBR 5444 |

Essa separacao evita que o `BoundBox` da forma 3D seja contaminado pelo simbolo 2D,
garantindo que os conectores MEP (`getSnapPoints`) apontem para as faces fisicas reais
da caixa.

---

## 4. Conectores MEP (Snap Points)

O `getSnapPoints` de cada componente retorna pontos de conexao para eletrodutos e roteamento.
Os limites sao armazenados como propriedades `Snap_*` na matriz durante o `execute()`,
calculados sobre a geometria 3D pura antes de qualquer simbologia:

| Propriedade | Descricao |
|---|---|
| `Snap_XMin`, `Snap_XMax` | Limites X da caixa fisica |
| `Snap_YMin`, `Snap_YMax` | Limites Y da caixa fisica |
| `Snap_ZMin`, `Snap_ZMax` | Limites Z da caixa fisica |

Conectores gerados para tomadas:

- **Norte** (frente/parede), **Sul** (fundo), **Leste** (direita), **Oeste** (esquerda), **Fundo** (entrada do eletroduto)

---

## 5. Simbologia 2D e TechDraw

### 5.1 Organizacao no Documento

Os simbolos 2D sao agrupados na arvore do projeto por nivel:

```
📁 Simbologia 2D — Tomadas
   📁 Nivel Terreo       ← Z = elevacao do Terreo (ex: 0 mm)
   📁 Nivel 01           ← Z = elevacao do Nivel 01 (ex: 3000 mm)
   📁 Nivel 02           ...
```

Cada subgrupo pode ser ocultado independentemente do 3D.

### 5.2 Altura Do Plano De Simbologia

Padrao: `SymbolPlaneHeight = 0`:

```
Z do simbolo = elevacao do nivel + 0 = piso do nivel
```

| Elemento | Plano recomendado |
|---|---|
| Tomadas | Planta de piso (Z = elevacao do nivel) |
| Interruptores | Planta de piso |
| Pontos de luz | Planta de teto (Z = elevacao + pe-direito) |

### 5.3 Workflow TechDraw

1. Selecionar subgrupo `Nivel Terreo`
2. TechDraw → Inserir Vista → Top View
3. Resultado: planta eletrica do terreo com todos os simbolos no plano correto
4. Repetir para cada nivel

---

## 6. Matrizes E Instancias Visiveis

- A matriz e criada uma vez por combinacao familia/modulos/amperagem/altura e fica oculta.
- A matriz tem `BIMRole = SocketMatrix` e `IsLibraryMatrix = True`.
- A instancia inserida tem `BIMRole = Socket` e `IsLibraryMatrix = False`.
- Circuito, quadro, potencia, nivel, ambiente/setor e dados IFC ficam na instancia, nunca na matriz.
- A propriedade `LibraryMatrixObject` na instancia aponta para o nome da matriz, usada pelo
  roteador automatico para recuperar os snap points sem re-computar.

---

## 7. Roteamento Automatico (get_best_connection_point)

O metodo `AutoRouter.get_best_connection_point(obj, target_point)` em `EletricaLogic/Routing.py`
resolve o melhor ponto de conexao de qualquer objeto, na seguinte ordem de prioridade:

1. Proxy direto com `getSnapPoints` (caixas de passagem, FeaturePython)
2. Tomada instanciada: busca a matriz via `LibraryMatrixObject` e usa o Proxy da matriz
3. Duck-typing: procura `getSnapPoints()` ou `get_snap_points()` como bound method (sem argumento)
4. Fallback: `Placement.Base`

Os pontos locais sao transformados para coordenadas globais com `Placement.multVec(pt)`.
O conector mais proximo do ponto de destino e selecionado automaticamente.

---

## 8. Atalhos Da Ferramenta De Insercao

| Tecla | Acao |
|---|---|
| `ESPACO` | Gira 90° |
| `H` | Cicla altura (Baixa → Media → Alta) |
| `T` | Cicla tipo de circuito (TUG / TUE / UPS) |
| `A` | Cicla amperagem (10A / 20A) |
| `M` | Cicla modulos (Simples / Dupla / Tripla) |
| `N` | Cicla nivel de referencia |
| `I` | Alterna modo continuo / uma vez |
| `ESC` | Finaliza a ferramenta |

---

## 9. Estetica Dos Componentes

| Tipo de circuito | Cor |
|---|---|
| TUG (Geral) | Branco / Cinza |
| TUE (Especifico) | Amarelo |
| UPS (Emergencia) | Vermelho |

---
*Documentacao atualizada em 2026-05-19 — separacao 3D/2D, snap bounds e TechDraw por nivel.*
