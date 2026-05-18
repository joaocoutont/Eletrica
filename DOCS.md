# Documentação Técnica e Manual do Usuário - Elite Industrial Suite

## 1. Memória Técnica (Metodologia de Cálculo)

O Elite Industrial Suite utiliza as normas brasileiras (ABNT) como base para todos os seus motores de cálculo.

### 1.1 Redes Aéreas (RDU/RDR) - NBR 15688 / NBR 14039
- **Cálculo de Esforço Resultante**: Utilizamos a soma vetorial das trações de cada condutor ($T$) baseada no ângulo de deflexão ($\alpha$):
  $$R = 2 \cdot T \cdot \sin(\alpha / 2)$$
- **Pressão do Vento**: Calculada sobre a área projetada dos condutores e poste, seguindo a fórmula $P = K \cdot V^2$, onde $K$ é o coeficiente de arrasto (daN/m²).
- **Flecha (Sag)**: Calculada pela equação da parábola para vãos nivelados:
  $$f = (w \cdot L^2) / (8 \cdot T)$$
  Onde $w$ é o peso linear (kg/m), $L$ o vão e $T$ a tração (daN).
- **Sistema MRT (Rural)**: O cálculo de queda de tensão em sistemas Monofilares com Retorno por Terra considera a impedância do solo como caminho de retorno, adotando o modelo de Carson simplificado para a resistência de retorno.

### 1.2 Instalações de BT - NBR 5410
- **Queda de Tensão**:
  - Monofásico: $\Delta U = (2 \cdot L \cdot I \cdot (R\cos\phi + X\sin\phi)) / V$
  - Trifásico: $\Delta U = (\sqrt{3} \cdot L \cdot I \cdot (R\cos\phi + X\sin\phi)) / V$
- **Coordenação de Proteção**: A sugestão de elos fusíveis para transformadores segue a regra de proteção contra sobrecarga de longo prazo e suportabilidade ao *inrush* ($12 \cdot I_n$ por 0.1s).

### 1.3 Prevenção de Incêndio e Pânico - NBR 17240
- **Detecção**: O raio de cobertura adotado para detectores de fumaça em áreas sem obstruções é de 6,3m (área de 81m²), conforme classe de risco.
- **Sinalização**: A distância máxima entre placas de rota de fuga e iluminação de emergência segue o limite de 15m para garantir visibilidade em caso de sinistro.

### 1.4 Energia Solar (PV)
- **Geração Mensal**: $E = P_{kwp} \cdot H_{rad} \cdot 30 \cdot PR$
  - $PR$ (Performance Ratio): Adotado 0.75 como padrão conservador, considerando perdas por temperatura, sujeira e cabeamento CC.

---

## 2. Manual do Usuário (Fluxo de Trabalho)

### 2.1 Iniciando um Projeto
1. Clique em **Configuração da Obra** para definir as tensões do projeto (Ex: 220/127V ou 380/220V).
2. Use o **GIS Converter** para importar pontos do QGIS ou loque os postes manualmente.

### 2.2 Dimensionamento de Redes
1. Selecione o condutor no **Assistente de Linha Aérea**.
2. Clique em **Calcular** para obter o NBI sugerido e o esforço no poste.
3. Use **Lançar Cabos** selecionando dois postes em sequência.

### 2.3 Geração de Documentos
- Ao finalizar o 3D, clique em **Gerar Memorial RDU** para obter o relatório Markdown.
- Para orçamentos, acesse a aba **Ciclo de Vida BIM** e selecione **Orçamento (5D)**.

---

## 3. Roadmap (Próximas Versões)

### Versão 1.1 (Curto Prazo)
- [ ] Integração com API de mapas para busca automática de irradiação solar via coordenadas GPS.
- [ ] Renderização foto-realística de painéis solares para apresentações comerciais.
- [ ] Biblioteca expandida de inversores híbridos (com baterias).

### Versão 2.0 (Longo Prazo)
- [ ] **Análise de Sombras Dinâmica**: Simulação de sombreamento de prédios/árvores sobre os painéis solares ao longo do dia.
- [ ] **Realidade Aumentada (AR)**: Exportador direto para visualização de postes e redes em campo via óculos AR ou smartphone.
- [ ] **Cálculo de Harmônicas**: Módulo avançado de qualidade de energia para cargas não-lineares industriais.

---
## 4. Estrutura BIM Eletrica Implementada

### 4.1 Preparacao de Projeto

A preparacao de projeto e centralizada nos comandos:

- `Eletrica_PrepareFromCAD`
- `Eletrica_PrepareFromIFC`
- `Eletrica_PrepareFromFreeCAD`

Esses comandos abrem um assistente que configura origem, perfil, ponto base, escala CAD, superficies, niveis, espacos, quadros e circuitos. A preparacao usa objetos nativos do FreeCAD/Arch/BIM quando disponiveis e cria apenas o que estiver faltando.

### 4.2 Templates TOML

Os perfis sao carregados de:

```text
Templates/ProjectProfiles/*.toml
```

Campos principais:

```toml
name = "Predial / Hospitalar"
site = true
building = true
levels = true
spaces = true
groups = ["Ambientes"]

[electrical]
panels = ["QD-Terreo"]
circuits = ["C-01 TUG"]

[automation]
Protocol = "KNX / Zigbee / Wi-Fi / Ethernet"
ControlVoltage = "24Vcc"
```

Se os TOML nao carregarem, `ProjectSetup.py` usa perfis internos como fallback.

### 4.2.1 Catalogo TOML de Familias

As familias da biblioteca usam um indice leve:

```text
Library/FamilyCatalog/families.toml
```

O comando `Eletrica_ManageFamilies` abre o editor desse catalogo. A lista de tomadas le esse TOML sem abrir os arquivos `.FCStd`; a geometria 3D so e carregada quando a familia e inserida ou editada.

Pastas padrao da biblioteca:

```text
Library/3D/Tomadas
Library/3D/Conjuntos_Modulares
Library/2D/Conjuntos_Modulares
```

`Library/3D/Tomadas` guarda familias de tomada. `Library/3D/Conjuntos_Modulares` guarda placas e combinacoes, como tomada + interruptor. A pasta 2D e opcional para simbologias separadas.

### 4.2.2 Tomadas com matriz em cache

A insercao de tomadas usa uma matriz oculta de biblioteca para reduzir abertura de arquivos e recompute:

- matriz oculta: `BIMRole = SocketMatrix`, `IsLibraryMatrix = True`;
- instancia real: `BIMRole = Socket`, `IsLibraryMatrix = False`;
- geometria visivel da instancia: `GeometrySourceMode = CachedShapeFromMatrix`;
- a matriz guarda geometria/familia e fica fora de cargas, validacoes, tabelas, BOM, relatorios e exportacao;
- a instancia real guarda `PanelBoard`, `CircuitNumber`, `CircuitObject`, `Power`, `ReferenceLevel`, `MountingHeight`, `FinalElevation` e demais dados BIM;
- a chave da matriz inclui arquivo da familia, modulos, amperagem e altura para evitar reaproveitamento incorreto entre tomada baixa, media e alta.

### 4.3 Objetos BIM de Quadro e Circuito

Quadros sao `App::FeaturePython` com `BIMRole = PanelBoard` e propriedades:

- `IFC_Class`
- `PanelType`
- `Voltage`
- `Phases`
- `RatedCurrent`
- `ShortCircuitLevel`
- `FeedingFrom`

Circuitos sao `App::FeaturePython` com `BIMRole = Circuit` e propriedades:

- `CircuitNumber`
- `Usage`
- `Voltage`
- `Power`
- `CableSection`
- `Breaker`
- `PanelBoard`
- `ConnectedLoad`
- `PointCount`
- `CurrentA`
- `DemandFactor`
- `DesignCurrent`
- `SuggestedBreaker`
- `SuggestedCableSection`
- `VoltageDropEstimate`

### 4.4 Vinculo dos Pontos

Pontos eletricos, como tomadas BIM, gravam:

- `PanelBoard`
- `CircuitNumber`
- `CircuitObject`
- `SpaceOrSector`
- `ReferenceLevel`
- `MountingHeight`
- `FinalElevation`
- `HostObject`
- `HostFace`

Esses dados alimentam calculos preliminares, validacao, tabela de pontos, filtros e relatorios.

Matrizes de biblioteca criadas para otimizar tomadas nao sao pontos eletricos. Elas devem ser ignoradas por qualquer rotina de carga ou documentacao quando `IsLibraryMatrix` for verdadeiro ou `BIMRole` for `SocketMatrix`.

### 4.5 Calculo Preliminar

O recalculo de cargas soma as potencias dos pontos vinculados e atualiza cada circuito com:

```text
ConnectedLoad
PointCount
CurrentA
DesignCurrent
SuggestedBreaker
SuggestedCableSection
```

Esse calculo e preliminar e serve para verificacao inicial do modelo, nao substituindo memoria de calculo final.

### 4.6 Relatorios e Auditoria

Recursos implementados:

- CSV de pontos eletricos.
- Relatorio HTML do projeto.
- Validacao basica de vinculos.
- Validacao visual por cores.
- Filtro de sistemas por tipo de circuito.
- Legenda automatica dos sistemas usados.
- Rotas preliminares por circuito.

---
*Documento atualizado em: Maio de 2026*
