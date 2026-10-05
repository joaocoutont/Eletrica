# 📋 Modos de Inserção de Tomada — Bancada Elétrica FreeCAD 1.2

> Arquivo de referência para o módulo `Eletrica`  
> Gerado em: 2026-06-06

---

## 1. Visão Geral dos Modos

| # | Nome | Gatilho | Descrição |
|---|------|---------|-----------|
| 1 | **Normal** | (padrão) | Clique insere na posição do cursor com rotação atual |
| 2 | **Girar 90°** | `G` | Aplica +90° acumulativo (0→90→180→270→0) |
| 3 | **Girar 15° (fino)** | `F` toggle / `[` -15° / `]` +15° | Passos finos de ±15°; botão do painel fica destacado |
| 4 | **Direção 2 Pontos** | `Shift+Clique` (1°) / `Shift+Clique` (2° = cancela) | Ponto fixo + cursor livre define ângulo; linha **ciano** no 3D |
| 5 | **Alinhamento de Parede** | `W` / botão "Parede" | 1° clique = posição da tomada; 2° clique = direção da parede → gira perpendicular; linha **verde** no 3D |
| 6 | **Referência + Distância** | `R` / botão "Ref" | Ponto de referência + distância exata no spinbox; linha **roxa** no 3D |

---

## 2. Teclas de Atalho — Referência Rápida

```
G         → Girar +90° (sempre, em qualquer modo)
F         → Ativar/desativar modo fino 15°
[         → Girar -15°
]         → Girar +15°
W         → Ativar/desativar modo Alinhamento de Parede
R         → Ativar/desativar modo Referência + Distância
Shift     → + Clique: define ponto de Direção (modo 4)

H         → Ciclar altura padrão (300 / 1100 / 2200 mm)
T         → Ciclar tipo de circuito (TUG / TUE / UPS)
N         → Ciclar nível BIM
A         → Ciclar amperagem (10A / 20A)
M         → Ciclar módulos (1 / 2 / 3)
I         → Ciclar modo de inserção (contínuo / uma vez)
Tab       → Mostrar/ocultar painel lateral  ⚠️ P removido (conflito Sketcher)
ESC       → Cancela modo ativo → se nenhum, encerra a ferramenta
```

### ESC em cascata (pressionar ESC não fecha imediatamente)
1. `ESC` com modo **Parede** ativo → cancela só a parede (volta ao Normal)
2. `ESC` com **Direção** travada → cancela só a direção
3. `ESC` com **Referência** ativa → cancela só a referência
4. `ESC` sem nenhum modo ativo → encerra o comando de inserção

---

## 3. Análise de Conflitos com Atalhos do FreeCAD

> **Pesquisa baseada no wiki oficial do FreeCAD (junho 2026)**

### Como funciona o filtro de teclado

O `BIMPlacementEngine` instala o `QtKeyFilter` em **`QApplication.instance()`** — ou seja, os eventos de teclado são interceptados **antes** de chegarem ao FreeCAD ou aos seus widgets. Isso garante que os atalhos funcionem na viewport 3D.

Como a ferramenta é **modal** (ativa durante a inserção), qualquer conflito com o FreeCAD é **temporário e esperado** — o usuário sabe que está usando uma ferramenta específica.

---

### Dois tipos de atalhos no FreeCAD

| Tipo | Descrição | Risco real |
|------|-----------|-----------|
| **Global / Workbench** | Ativos sempre que a bancada está carregada | Alto — conflito real |
| **In-command (Draft/BIM)** | Ativos somente DENTRO de uma tarefa Draft/BIM enquanto o cursor está em um campo de texto do painel | Baixo — contextos mutuamente exclusivos |

---

### Tabela Completa de Conflitos

| Tecla | Uso no Plugin | Atalho FreeCAD nativo | Tipo | Risco | Conclusão |
|-------|-------------|----------------------|------|-------|-----------|
| **G** | Girar +90° | `G` = Toggle Global mode | Draft **in-command** | 🟡 Médio | **SEGURO** — só ativa dentro do painel de tarefa Draft, não na viewport 3D |
| **F** | Modo fino 15° | `V, F` = Fit All (sequência de 2 teclas) | Standard | 🟢 Baixo | **SEGURO** — `F` isolado não tem ação nativa; `V,F` é sequência |
| **W** | Modo Parede | `W, P` = SelectPlane (sequência de 2 teclas) | Draft | 🟢 Baixo | **SEGURO** — `W` isolado não está atribuído globalmente |
| **H** | Ciclar altura | `H` = Constrain Horizontal | **Sketcher** | 🟡 Médio | **SEGURO** — conflito só se o Sketcher estiver aberto; incompatível com o plugin |
| **T** | Ciclar tipo circuito | `T` = Toggle Continue mode | Draft **in-command** | 🟡 Médio | **SEGURO** — contextos mutuamente exclusivos |
| **N** | Ciclar nível | `N` = Constrain Perpendicular | **Sketcher** | 🟡 Médio | **SEGURO** — conflito só no Sketcher, contexto incompatível |
| **A** | Ciclar amperagem | `A` = Exit/abort | Draft **in-command** | 🟡 Médio | **SEGURO** — contextos mutuamente exclusivos |
| **M** | Ciclar módulos | `M, V` = Draft Move (sequência) | Draft | 🟢 Baixo | **SEGURO** — `M` isolado não tem ação nativa |
| **I** | Ciclar modo inserção | *(Nenhum)* | — | 🟢 Baixo | **SEGURO** — sem atalho nativo |
| **P** | Toggle painel | `P` = Constrain Parallel | **Sketcher** | 🟡 Médio | **SEGURO** — conflito só no Sketcher; `Ctrl+P` = Imprimir (sem conflito) |
| **R** | Modo Referência | `R` = Toggle Relative mode | Draft **in-command** | 🟡 Médio | **SEGURO** — contextos mutuamente exclusivos |
| **[** | Girar -15° | `[` = Decrease radius (arc/circle) | Draft **in-command** | 🟢 Baixo | **SEGURO** — só ativa dentro de Draw Circle/Arc, nunca globalmente |
| **]** | Girar +15° | `]` = Increase radius (arc/circle) | Draft **in-command** | 🟢 Baixo | **SEGURO** — idem `[` acima |

---

### Resumo por nível de risco

#### ✅ Sem atalho nativo conhecido (mais seguros)
`F`, `W`, `M`, `I`, `[`, `]`

#### 🟡 Conflito de contexto diferente (seguros na prática)
`G`, `R`, `T`, `A` — conflitam com **Draft in-command** (só dentro de campos de texto do painel Draft, nunca na viewport)

`H`, `N`, `P` — conflitam com **Sketcher** (só quando o Sketcher está aberto, situação incompatível com o plugin)

#### 🔴 Conflito global real
*Nenhuma das 13 teclas propostas cai nessa categoria.*

---

### Por que os conflitos "in-command" não são um problema

O FreeCAD tem dois mecanismos totalmente distintos:
- O **Eletrica** captura teclas via `QApplication.eventFilter` na **viewport 3D**
- Os atalhos **Draft in-command** só disparam quando o cursor está **dentro de um campo de texto** (QLineEdit) do painel de tarefa do Draft

São contextos mutuamente exclusivos: se o usuário está inserindo uma tomada (Eletrica), não está digitando em um campo do Draft. Se está digitando num campo, o filtro `QtKeyFilter` já ignora (a lógica de exclusão por `LineEdit`/`TextEdit` já está implementada).

---

## 4. Painel Lateral — Grupo de Modo de Rotação

O `SocketTaskPanel` foi atualizado com o grupo **"✨ Modo de Rotação"**:

```
┌─ ✨ Modo de Rotação ─────────────────────────────┐
│  [ Normal ]   [ ↺ 90° [G] ]   [ ↺ 15° [F] ]    │
│  [ → Dir [Shift] ]   [ □ Parede [W] ]           │
└─────────────────────────────────────────────────┘
```

- **Normal**: sem modo ativo; tomada insere onde o cursor estiver
- **↺ 90° [G]**: aplica +90° imediatamente; o botão não fica marcado (é um toque)
- **↺ 15° [F]**: ativa/desativa modo fino; botão fica marcado quando ativo
- **→ Dir [Shift]**: instrução para usar Shift+Clique; botão fica marcado após 1° clique
- **□ Parede [W]**: ativa modo alinhamento; botão fica marcado

---

## 5. Indicadores Visuais no 3D (Overlay Coin3D)

| Linha | Cor | Modo | Significado |
|-------|-----|------|-------------|
| Ciano `──` | (0.0, 0.9, 1.0) | Direção (4) | Linha do ponto fixo ao cursor |
| Roxa `- -` | (0.8, 0.0, 0.8) | Referência (6) | Linha do ponto de referência ao cursor |
| Verde `━━` | (0.0, 0.9, 0.2) | Parede (5) | Linha do 1° ponto ao cursor mostrando a reta da parede |

---

## 6. Arquitetura Técnica

### Arquivos modificados

| Arquivo | O que mudou |
|---------|-------------|
| `GeometryScripts/bim_placement_core.py` | Modos 1-6, overlay verde, teclas F/W/[/], ESC em cascata |
| `GeometryScripts/socket_gui.py` | Grupo de botões de modo, `sync_rot_mode_buttons()` |

### Estado interno do `BIMPlacementEngine`

```python
self.rot_mode      = 1      # 1=Normal 2=Rot90 3=Rot15 4=Direção 5=Parede 6=Ref
self.wall_p1       = None   # App.Vector — 1° ponto da reta de parede
self.wall_active   = False  # True enquanto modo parede aguarda cliques
self.dir_origin    = None   # App.Vector — ponto fixo do modo direção
self.dir_locked    = False  # True após 1° Shift+Clique
self.ref_mode_active = False
self.ref_point     = None
```

### Métodos novos

```python
engine.set_rot_mode(mode)        # Muda modo, cancela estados anteriores, sync UI
engine._apply_rotation(delta)    # Aplica delta°, reseta modos de direção/parede
overlay.set_wall_line(pt_a, pt_b) # Linha verde de parede no Coin3D
panel.sync_rot_mode_buttons(mode) # Atualiza visual dos botões do painel
```

---

## 7. Fluxo de Uso — Exemplos Práticos

### Tomada alinhada com parede inclinada (Modo 5 - Parede)
1. `W` → status bar: *"PAREDE: clique no 1° ponto da parede"*
2. Clique no ponto da parede onde quer a tomada → fantasma trava; linha verde aparece
3. Move o mouse → fantasma rotaciona em tempo real mostrando ângulo perpendicular
4. Clique no 2° ponto → tomada inserida com ângulo correto perpendicular à parede
5. Modo parede continua para a próxima inserção (modo contínuo)

### Tomada a distância exata de uma quina (Modo 6 - Referência)
1. `R` → status bar: *"REFERÊNCIA: clique no 1° ponto"*
2. Clique na quina da parede → linha roxa aparece; spinbox no painel fica ativo
3. Move o cursor na direção desejada → spinbox mostra distância em tempo real
4. Digita a distância no spinbox (ex.: `450`) e pressiona `Enter` → tomada inserida na posição exata
5. Referência limpa automaticamente; modo Normal restaurado

### Rotação fina para encaixe em caixinha inclinada (Modo 3 - Fino)
1. `F` → status bar: *"FINO 15° | Rot=0° | [ -15°  ] +15°"*
2. `]` → gira +15° → `]` → gira +30° → ... até alinhar
3. Clique → insere
4. `F` novamente desativa o modo fino

---

## 8. Notas Adicionais (Pesquisa FreeCAD Wiki)

- O FreeCAD **não tem atalhos de tecla única** ativos globalmente para letras (exceto dentro do Sketcher)
- A maioria dos atalhos globais usa `Ctrl+letra` (Ctrl+S, Ctrl+Z, etc.)
- As views de câmera usam teclas numéricas (1, 2, 3, 4, 5, 6)
- As views de câmera também usam sequências `V, O` / `V, P` / `V, F` etc.
- Part e PartDesign **não têm nenhum atalho de tecla única** por padrão
- BIM Workbench usa apenas atalhos in-command (herdados do Draft)

---

*Documentação gerada pelo Antigravity — FreeCAD Eletrica Workbench v1.2*
