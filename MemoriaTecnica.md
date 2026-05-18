# Memória Técnica - Bancada Eletrica (FreeCAD 1.1)
**Versão**: 5.0 (Elite BIM Suite - Edição Estabilidade Total)
**Última Atualização**: 2026-05-18

---

## 1. Visão Geral
A bancada **Eletrica** é uma ferramenta profissional para o FreeCAD 1.1 focada em projetos de engenharia elétrica. O objetivo é fornecer ferramentas para modelagem 3D, cálculos normatizados (NBR 5410) e geração de documentação técnica automática, integrando-se nativamente às bancadas BIM e Draft do FreeCAD.

---

## 2. Escopo Técnico
- **Base Normativa**: NBR 5410 (Instalações elétricas de baixa tensão), com suporte parcial à NBR 14039 (Média Tensão) e NDUs das concessionárias (Energisa NDU-001, Cemig ND-5.1, Enel NTC-901001, Neoenergia PAD-DIS-SRT/BT-001, Copel NTC-905200).
- **Abordagem BIM**: Cada componente (tomada, conduíte, quadro) possui metadados técnicos (potência, corrente, queda de tensão, material, circuito, fase).
- **Integração**: Compatível com as ferramentas nativas de Arquitetura (Arch/BIM) e Draft do FreeCAD, com suporte a arquivos IFC via `Arch_Reference` e `BIM_IfcExplorer`.

---

## 3. Arquitetura do Sistema

```
Eletrica/
├── InitGui.py          # Registro da bancada, toolbars e proxies de comandos externos
├── EletricaGui.py      # Hub Central: Wrapper de robustez e registro dinâmico de comandos
├── EletricaPanel.py    # Painel lateral de métricas (Dashboard)
├── Init.py             # Inicialização não-gráfica
├── Icons/              # Ícones SVG e PNG da bancada
└── EletricaLogic/      # Lógica de engenharia (pura, sem Qt)
    ├── Calculator.py       # Cálculos NBR 5410 (seção, queda, disjuntor, demanda)
    ├── Circuits.py         # Quadro de Cargas e balanceamento de fases
    ├── Panels.py           # Hierarquia de quadros (QDC, CCM, CCA)
    ├── ServiceEntrance.py  # Assistente de Padrão de Entrada por concessionária
    ├── ...                 # Outros módulos especializados
```

---

## 4. Camada de Robustez e Experiência do Usuário (UX)
Na versão 4.1, a arquitetura foi "endurecida" para garantir um comportamento profissional e estável:

### 4.1 Command Wrapper (Decorador Global)
Todos os comandos registrados no `EletricaGui.py` são automaticamente encapsulados por um wrapper que gerencia:
- **Transações Automáticas**: Abre uma transação (`openTransaction`) no início e faz o `commit` ao final. Se o comando falhar, executa o `abortTransaction`, garantindo que o arquivo não fique corrompido ou com objetos parciais.
- **Tratamento de Erros Global**: Captura exceções Python, gera logs detalhados no console e exibe uma caixa de diálogo (`QMessageBox`) amigável para o usuário.
- **Feedback Visual**: Atualiza a barra de status do FreeCAD com o nome da operação em execução e uma mensagem de sucesso/concluído.

### 4.2 Selection Guards (Filtros Inteligentes)
O sistema de ativação de botões (`IsActive`) foi expandido para ser ciente do contexto:
- **Filtro de Documento**: Todos os botões (toolbars e menus) são desabilitados automaticamente se não houver um documento ativo, seguindo o padrão da bancada BIM.
- **RequiredSelection**: Comandos específicos definem requisitos de seleção. Exemplo: O comando "Diagrama Unifilar" só habilita se um Quadro ou Subestação estiver selecionado.

---

## 5. Funcionalidades Principais

### 5.1 Cálculos Elétricos (`Calculator.py`)
- **Seção de cabos e Queda de Tensão**: Cálculos conforme NBR 5410.
- **Demanda Dinâmica**: Fatores de demanda variáveis por tipo de instalação.

### 5.2 Elétrica Industrial e RDU
- **Inserção Inteligente**: Componentes industriais (Geradores, Motores, Postes) utilizam o helper `insert_component_smart`, que aciona automaticamente a ferramenta de movimentação após a inserção.
- **Assistentes (Wizards)**: Interfaces guiadas para dimensionamento de partidas de motores e redes aéreas.

---

## 8. Melhorias e Estabilização (v4.1)
| Módulo | Melhoria | Benefício |
|---|---|---|
| `InitGui.py` | Deduplicação de Toolbar | Interface limpa, sem botões repetidos. |
| `EletricaGui.py` | Injeção de `IsActive` | Botões "cinzas" evitam erros de execução sem arquivo. |
| `Industrial.py` | Helper `insert_component_smart` | Fluxo de trabalho mais rápido (Insert + Move). |
| `Audit.py` | Geração de BIM 4D/9D | Implementação completa da integração com cronograma e manutenção. |

---

## 9. Estabilização Avançada e Motor de Inserção BIM (v5.0)
Na versão 5.0, o motor de posicionamento 3D (`GeometryScripts/bim_placement_core.py`) foi redesenhado para eliminar interferências do sistema de navegação e de seleção nativo do FreeCAD 1.1:

### 9.1 Filtro de Eventos Qt em Tempo Real (`QtClickFilter`)
- **Desvio de Viewport**: Implementação de um `QObject` de filtro de eventos Qt (`installEventFilter`) acoplado dinamicamente ao widget `QMdiArea` / `QuarterWidget` ativo.
- **Intercepção de Cliques**: Filtra todos os cliques do botão esquerdo (`LeftButton`) do mouse no nível de janela (Qt6), disparando a inserção em Python e consumindo o evento (`event.accept()`). Isso impede fisicamente que a engine C++ do FreeCAD receba o clique, eliminando menus de contexto e caixas de diálogo durante o desenho.

### 9.2 Bloqueio de Seleção Nativo C++ (`SELECT None`)
- **Selection Gate C++**: Substituição do filtro Python por um filtro nativo compilado através de query string de seleção. O comando `Gui.Selection.addSelectionGate("SELECT None")` rejeita a seleção a nível de máquina, impedindo o raycasting de faces e arestas que geravam o pop-up de seleção múltipla.

### 9.3 Correção do Caminho de Preferência de Pré-Seleção
- **Configuração Correta**: Correção do caminho do parâmetro de pré-seleção global de `BaseApp/Preferences/View` para `BaseApp/Preferences/Selection/EnablePreselection`. Agora, o realce visual (hover highlight) é desabilitado instantaneamente e restaurado perfeitamente ao fechar a ferramenta.

---
*Este documento é parte integrante da documentação técnica da bancada Eletrica.*
