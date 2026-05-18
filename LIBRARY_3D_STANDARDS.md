# Padroes da Biblioteca 3D - Workbench Eletrica BIM

Este documento descreve os padroes de geometria, catalogo e insercao inteligente usados pela bancada Eletrica.

## 1. Estrutura De Pastas E Modelagem

Mantenha as regras de volume maximo, centralizacao e origem funcional dos modelos. A geometria deve ser leve, limpa e alinhada para que a insercao em planta e em parede seja previsivel.

### 1.1 Catalogo Leve De Familias

As propriedades BIM padrao da familia ficam no arquivo:

```text
Library/FamilyCatalog/families.toml
```

O FreeCAD nao precisa abrir todos os `.FCStd` para listar tomadas e familias. O comando **Gerenciar Familias** edita esse TOML, importa arquivos externos para a biblioteca e permite rodar **Regerar Catalogo** quando novos arquivos forem copiados manualmente.

Use os arquivos `.FCStd` para geometria e simbologia. Use o TOML para metadados padrao como categoria, classe IFC, potencia, tensao, amperagem, modulos, fabricante, modelo e altura sugerida.

### 1.2 Pastas Padrao

Use estas pastas para organizar a biblioteca:

```text
Library/3D/Tomadas
Library/3D/Conjuntos_Modulares
Library/2D/Conjuntos_Modulares
```

`Library/3D/Tomadas` guarda familias de tomadas simples, duplas e especiais. `Library/3D/Conjuntos_Modulares` guarda placas combinadas, por exemplo interruptor + tomada, tomada dupla com comando, ou outros conjuntos de modulos. `Library/2D/Conjuntos_Modulares` pode guardar simbolos 2D quando houver representacao propria em planta.

### 1.3 Matrizes E Instancias Visiveis

Tomadas repetidas devem usar matriz oculta + instancia visivel com forma copiada da matriz:

- a matriz e somente geometria/familia;
- a matriz deve ter `BIMRole = SocketMatrix` e `IsLibraryMatrix = True`;
- a instancia inserida no projeto deve ter `BIMRole = Socket` e `IsLibraryMatrix = False`;
- a instancia visivel deve ter `GeometrySourceMode = CachedShapeFromMatrix`;
- circuito, quadro, potencia, ambiente, nivel e dados IFC ficam na instancia, nunca na matriz;
- rotinas de carga, validacao, tabela de pontos, BOM, relatorios e exportacao devem ignorar matrizes;
- a chave da matriz deve considerar arquivo da familia, modulos, amperagem e altura.

## 2. Insercao Inteligente

O motor de insercao usa a mira BIM para posicionar pontos eletricos com menos recompute e menos interferencia de selecao.

### 2.1 Auto-Snap Em Caixas

- Se o mouse passar sobre uma `Caixa_BIM` ou `JunctionBox`, a tomada pode ser atraida para o centro da caixa.
- A tomada pode assumir a rotacao da caixa hospedeira quando o modo de snap estiver habilitado.

### 2.2 Atalhos

- `ESPACO`: gira a tomada em 90 graus.
- `H`: muda a altura entre baixa, media e alta.
- `T`: muda o tipo de circuito, quando aplicavel.
- `I`: alterna modo continuo / uma vez.
- `ESC`: finaliza a ferramenta.

## 3. Metadados E Estetica

- Circuitos UPS/emergencia usam cor vermelha.
- Circuitos TUE/especificos usam cor amarela.
- Circuitos TUG/gerais usam cor branca ou cinza.

## 4. Conectores MEP

O sistema de snaps (`getSnapPoints`) e importante para que eletrodutos e rotas saibam onde se conectar. Todos os componentes que participarem de infraestrutura devem fornecer pontos de conexao em suas faces funcionais.

---
Documentacao atualizada para tomadas com matriz em cache e conjuntos modulares.
