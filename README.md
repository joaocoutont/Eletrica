# Elite Industrial Suite - FreeCAD Electrical Workbench (v1.0)

O **Elite Industrial Suite** é um workbench profissional para o FreeCAD voltado para engenharia elétrica, infraestrutura e gestão BIM. Ele cobre todo o ciclo de vida do projeto, desde a conexão com a concessionária até a manutenção preventiva.

## 🚀 Principais Módulos

### 1. Redes de Distribuição (RDU/RDR)
- Projeto completo de redes urbanas e rurais (MRT).
- Cálculos mecânicos de esforços em postes, flechas, vento e tração.
- Dimensionamento elétrico de MT (13.8/34.5 kV) e BT (Multiplexados).
- Integração GIS: Conversão de pontos do QGIS em postes BIM e exportação KML.

### 2. Subestação e Média Tensão (MT)
- Inserção de cubículos de MT (Medição, Proteção, Entrada).
- Dimensionamento de barramentos de cobre de média tensão.
- Assistente de transformadores industriais até 2500 kVA.

### 3. Energia Solar Fotovoltaica (PV)
- Assistente de geração mensal (kWh/mês).
- Dimensionamento de strings e cabos CC.
- Inserção automática de arrays de painéis (Telhado/Solo).
- Relatório de Sustentabilidade (ESG) com economia de CO2.

### 4. Sistemas Especiais e Segurança
- **SDAI**: Detecção e alarme de incêndio (Detectores, Sirenes, Centrais).
- **Segurança**: CFTV (Câmeras IP), Controle de Acesso e Sensores PIR.
- **Sonorização**: Avisos sonoros e som ambiente industrial.

### 5. Energia Crítica e Industrial
- **Energia Crítica**: Geradores Diesel, Nobreaks (UPS) e Quadros de Transferência (QTA).
- **Busway**: Barramentos blindados de alta potência e caixas plug-in (Tap-offs).
- **Mobilidade**: Estações de recarga para Veículos Elétricos (EV).

### 6. Inteligência BIM Full-Stack (3D até 8D)
- **3D**: Modelagem geométrica rica.
- **4D (Tempo)**: Gerador de cronograma de execução da obra.
- **5D (Custo)**: Orçamento detalhado de materiais e mão de obra.
- **6D (Sustentabilidade)**: Impacto ambiental e economia de recursos.
- **7D (Manutenção)**: Plano de Manutenção Preventiva automático.
- **8D (Segurança)**: Plano de Segurança do Trabalho e Prevenção NR-10.

## 🛠️ Instalação
1. Clone este repositório na sua pasta `Mod` do FreeCAD.
2. Reinicie o FreeCAD.
3. Ative o workbench `Eletrica` no menu de seleção.

## 📊 Relatórios Automáticos
- Memorial de Cálculo RDU (Markdown).
- Lista de Materiais Explodida (Kits de Estruturas).
- Quadro de Cargas NBR 5410.
- Cronogramas e Orçamentos BIM.

---
## Preparacao BIM do Projeto Eletrico

A bancada possui comandos dedicados para iniciar projetos eletricos a partir de diferentes bases:

- **Preparar Projeto por CAD**: importa ou vincula planta 2D, permite conferir escala, associar a nivel/setor e travar a referencia.
- **Preparar Projeto por IFC**: usa a estrutura BIM existente do arquivo, incluindo Site, Building, Storey/Niveis e Spaces quando disponiveis.
- **Preparar Projeto FreeCAD**: usa desenhos, grupos e objetos nativos do FreeCAD como base de organizacao.

O assistente permite escolher perfis como Predial/Hospitalar, Industrial, Automacao Residencial, Automacao Industrial, Saneamento, Rede Urbana, Rede Rural, Subestacao/MT e Generico.

Os perfis sao editaveis em TOML na pasta:

```text
Templates/ProjectProfiles
```

Cada perfil define grupos BIM, quadros, circuitos e parametros de automacao. Se os templates TOML nao forem encontrados ou estiverem invalidos, a bancada usa perfis internos como fallback.

## Biblioteca de Familias

O comando **Gerenciar Familias** edita o catalogo leve em:

```text
Library/FamilyCatalog/families.toml
```

Esse TOML guarda nome, categoria, classe IFC, arquivo 3D, potencia, tensao, amperagem, modulos e altura padrao. A bancada carrega esse indice sem abrir os arquivos `.FCStd`, melhorando a performance. Use **Regerar Catalogo** apenas quando adicionar arquivos manualmente na pasta da biblioteca.

Arquivos 3D ficam, por padrao, em:

```text
Library/3D/Tomadas
Library/3D/Conjuntos_Modulares
```

Representacoes 2D opcionais para conjuntos modulares podem ficar em:

```text
Library/2D/Conjuntos_Modulares
```

## Tomadas com Matriz em Cache

A ferramenta **Inserir Tomada BIM** usa uma matriz oculta de biblioteca para melhorar a performance em projetos grandes. A primeira tomada de uma mesma familia/configuracao carrega a geometria na matriz; as proximas tomadas copiam essa forma ja carregada, sem reabrir o arquivo `.FCStd`.

- A matriz recebe `BIMRole = SocketMatrix` e `IsLibraryMatrix = True`.
- A tomada real inserida recebe `BIMRole = Socket` e `IsLibraryMatrix = False`.
- A tomada visivel usa `GeometrySourceMode = CachedShapeFromMatrix`.
- Circuito, quadro, potencia, nivel, ambiente e IFC ficam na instancia real, nao na matriz.
- Recalculo de cargas, validacao, tabela de pontos, relatorios, BOM e exportacao ignoram matrizes de biblioteca.
- A chave da matriz considera arquivo da familia, modulos, amperagem e altura, evitando mistura entre tomada baixa, media e alta.

## Quadros, Circuitos e Pontos

Os quadros e circuitos preparados pelo assistente sao objetos BIM com propriedades eletricas. A ferramenta de tomada permite escolher nivel, ambiente/setor, quadro, circuito, tipo de uso e altura de instalacao.

As tomadas criadas sao vinculadas ao quadro/circuito selecionado e alimentam validacoes, cargas preliminares, tabela de pontos e relatorios.

## Gestao, Validacao e Documentacao

Comandos adicionados:

- Gerenciar Quadros/Circuitos.
- Recalcular Cargas.
- Validar Eletrica BIM.
- Validacao Visual.
- Editar Pontos em Lote.
- Exportar Tabela de Pontos.
- Relatorio HTML.
- Gerar Legenda.
- Criar Ambiente/Setor.
- Rotas Preliminares.

---
*Elite Industrial Suite - Desenvolvido para a Engenharia do Futuro.*
