# Guia do Usuário - Bancada Eletrica (FreeCAD 1.1)
**Versão**: 4.0 (Industrial & Automation Suite)
**Objetivo**: Fluxo de trabalho completo para projetos elétricos residenciais, comerciais e industriais.

---

## 🛠️ Guia Visual da Barra de Ferramentas (Esquerda para Direita)

Esta seção descreve cada botão exclusivo da bancada **Eletrica**, organizados por grupos funcionais conforme aparecem na sua interface.

### Grupo 1: Configuração da Obra
| Ícone | Nome do Botão | Função Principal |
| :---: | :--- | :--- |
| ![Icon](Icons/StartProject.png) | **Iniciar Novo Projeto** | Cria um novo arquivo .FCStd configurado, ativa a grade e prepara as camadas elétricas. |
| ![Icon](Icons/Report.png) | **Configuração da Obra** | Define metadados como Nome do Projeto, Autor, Concessionária e Tensão Nominal. |
| ![Icon](Icons/Dashboard.png) | **Painel de Controle** | Abre/Fecha o Dashboard lateral com KPIs de potência, custo e auditoria em tempo real. |
| ![Icon](Icons/TitleBlock.png) | **Sincronizar Selo** | Exporta automaticamente os dados da obra para o carimbo da folha no TechDraw. |

### Ferramentas de Qualidade e BIM
*   **Auditoria de Projeto**: Varre o modelo em busca de:
    *   Queda de tensão > 4% (NBR 5410).
    *   Colisões reais entre eletrodutos.
    *   Falta de circuitos ou quadros vinculados.
    *   Superlotação de eletrodutos (>40%).
*   **Gerar Etiquetas 3D**: Cria textos flutuantes sobre os componentes indicando `Circuito (Bitola)`, facilitando a conferência visual do modelo.
*   **Exportação BIM (IFC4)**: Sincroniza todos os dados técnicos (Trafo, UTM, Endereço) para o arquivo IFC.

### Grupo 2: Modelagem Elétrica
| Ícone | Nome do Botão | Função Principal |
| :---: | :--- | :--- |
| ![Icon](Icons/Substation.svg) | **Inserir Subestação** | Insere um objeto BIM de subestação (cabine primária) parametrizado. |
| ![Icon](Icons/Panel.png) | **Criar Quadro (QDC)** | Insere quadros de distribuição com inteligência para balanceamento de fases. |
| ![Icon](Icons/Socket.png) | **Inserir Tomada** | Biblioteca de tomadas (NBR 14136) com potências configuráveis. |
| ![Icon](Icons/Light.png) | **Inserir Lâmpada** | Insere pontos de iluminação com cálculo de fluxo luminoso integrado. |
| ![Icon](Icons/Switch.png) | **Inserir Interruptor** | Insere comandos simples, duplos, triplos ou paralelos (Three-way). |
| ![Icon](Icons/Merge.png) | **Mesclar Placas** | Une múltiplos interruptores ou tomadas em uma única caixa/placa 4x2 ou 4x4. |
| ![Icon](Icons/SmartHome.png) | **Inserir Smart/IoT** | Adiciona dispositivos de automação (Hubs, Sensores, Atuadores Zigbee/WiFi). |
| ![Icon](Icons/Pump.svg) | **Bomba de Poço** | Dimensionamento e inserção de bombas submersas e sistemas de recalque. |
| ![Icon](Icons/BIMify.png) | **BIMificar Objeto** | Converte uma geometria genérica em um componente elétrico inteligente. |

### Grupo 3: Infraestrutura
| Ícone | Nome do Botão | Função Principal |
| :---: | :--- | :--- |
| ![Icon](Icons/Conduit.png) | **Criar Eletroduto** | Traça tubulações flexíveis ou rígidas entre os pontos elétricos. |
| ![Icon](Icons/Tray.png) | **Criar Leito/Bandeja** | Modela eletrocalhas e leitos industriais de alta capacidade. |
| ![Icon](Icons/TrayAssistant.png) | **Assistente de Leitos** | Calcula a taxa de ocupação e sugere a dimensão ideal da eletrocalha. |
| ![Icon](Icons/AerialNetwork.png) | **Rede Aérea MT** | Dimensiona e insere postes e condutores de média tensão para loteamentos. |
| ![Icon](Icons/SPDA.svg) | **Wizard SPDA** | Assistente de proteção contra descargas atmosféricas (Para-raios). |

### Grupo 4: Engenharia e Cálculos
| Ícone | Nome do Botão | Função Principal |
| :---: | :--- | :--- |
| ![Icon](Icons/ServiceEntrance.png) | **Padrão de Entrada** | Calcula a demanda total e dimensiona o padrão de entrada da concessionária. |
| ![Icon](Icons/Substation.svg) | **Dimensionar Subestação** | Dimensiona o transformador e a cabine primária baseado na carga total. |
| ![Icon](Icons/Busbar.png) | **Dimens. Barramento** | Calcula a seção de barras de cobre/alumínio para quadros industriais. |
| ![Icon](Icons/SelectivityPro.png) | **Seletividade** | Analisa a coordenação entre disjuntores para evitar desligamentos em cascata. |
| ![Icon](Icons/Generator.svg) | **Emergência/Gerador** | Configura grupos geradores e sistemas de transferência automática (QTA). |

### Grupo 5: Documentação
| Ícone | Nome do Botão | Função Principal |
| :---: | :--- | :--- |
| ![Icon](Icons/LoadSchedule.svg) | **Quadro de Cargas** | Gera a planilha automática com circuitos, bitolas e disjuntores. |
| ![Icon](Icons/CableSchedule.svg) | **Lista de Cabos** | Relatório detalhado "De-Para" com comprimentos para corte. |
| ![Icon](Icons/BudgetPro.png) | **Gerar Orçamento** | Exporta a lista de materiais (BOM) com preços e quantitativos. |
| ![Icon](Icons/UnifilarPro.png) | **Diagrama Unifilar** | Desenha o esquema elétrico gráfico automaticamente no TechDraw. |
| ![Icon](Icons/CCMDiagram.png) | **Diagrama CCM** | Gera o diagrama de comando industrial para motores. |
| ![Icon](Icons/Audit.png) | **Auditoria de Erros** | Verifica conflitos, sobrecargas e erros de conexão no projeto. |
| ![Icon](Icons/SafetyNR10.png) | **Segurança (NR-10)** | Analisa riscos de arco elétrico e conformidade com normas de segurança. |
| ![Icon](Icons/QR_AR.png) | **Gerar QR Code AR** | Cria um QR Code para visualização do projeto em Realidade Aumentada. |
| ![Icon](Icons/IFCExport.png) | **Exportar BIM (IFC)** | Gera o arquivo IFC4 com todas as propriedades elétricas integradas. |
| ![Icon](Icons/GroundingReport.png) | **Relatório NBR 15751** | Gera memória de cálculo de aterramento para subestações. |
| ![Icon](Icons/ArcFlash.png) | **Análise Arc Flash** | Calcula energia incidente e gera etiquetas de segurança NR-10. |
| ![Icon](Icons/LightingAnalysis.png) | **Cálculo Lúmens** | Dimensiona luminárias industriais com inserção automática em grid. |
| ![Icon](Icons/PriceEditor.png) | **Editor de Preços** | Configura valores unitários paramétricos para o projeto. |
| ![Icon](Icons/QRMaintenance.png) | **QR Manutenção** | Gera QRs para gestão de ativos e manutenção (BIM 7D). |

### Grupo 6: Referência BIM (Externo)
| Ícone | Nome do Botão | Função Principal |
| :---: | :--- | :--- |
| ![Icon](Arch_Reference) | **Arch Reference** | Importa modelos de arquitetura ou estrutura externos como links leves. |
| ![Icon](IFC) | **Explorador IFC** | Abre a árvore técnica de dados brutos do arquivo IFC (Atributos e Psets). |
| ![Icon](Arch_Site) | **Arch Site** | Define o terreno e as coordenadas geográficas do projeto elétrico. |
| ![Icon](Arch_Building) | **Arch Building** | Cria o container principal do edifício para organização espacial BIM. |
| ![Icon](Arch_BuildingPart) | **Arch BuildingPart**| Representa níveis (Pavimentos) ou partes específicas da construção. |

---

## 1. Iniciando o Projeto
O primeiro passo é preparar o ambiente de trabalho.

1.  **Abrir o FreeCAD** e selecionar a bancada **Eletrica** no seletor de bancadas.
2.  Clique no ícone **Iniciar Novo Projeto** (ícone do raio com folha branca). Isso criará um novo documento formatado e ativará a grade de desenho instantaneamente.
3.  **Configurar Dados da Obra**: Clique no botão **Configuração da Obra**.
    *   Preencha o nome do projeto, tipo de obra (importante para o fator de demanda) e a concessionária.
| Address            | Localização| Endereço completo da obra                      |
| UTM_E, UTM_N       | Localização| Coordenadas UTM (Easting/Northing)             |
| UTM_Zone           | Localização| Zona UTM (ex: 22S)                             |
| PrimaryVoltage     | Técnico    | Tensão primária MT (ex: 13.8kV, 34.5kV)        |
    *   Defina a **Tensão Secundária (BT)** (ex: 127/220V, **380/660V**) e a **Ligação do Trafo** (ex: Dyn11).
    *   Insira a **Localização da Obra**: Endereço completo e Coordenadas UTM (E, N, Zona) para georreferenciamento.
    *   Esses dados serão usados em todos os cálculos automáticos de queda de tensão e curto-circuito.

---

### 1.1 Início Rápido (Quick Start)
1. **Ative** a bancada `Eletrica`.
2. Clique em **Iniciar Novo Projeto**.
3. Insira um **Quadro de Distribuição** (QDC).
4. Insira **Tomadas** e **Lâmpadas**.
5. No painel de dados, defina o `Circuito` (ex: C1) e o `QuadroVinculado` (ex: QDC).
6. Clique em **Gerar Quadro de Cargas**.

---

## 2. Preparando a Arquitetura de Referência
Nunca desenhe a elétrica no "vazio". Use uma arquitetura como base.

### 2.1 Usando um modelo IFC (Fluxo BIM)
1.  Vá na bancada **BIM** ou **Arch**.
2.  Use a ferramenta **Arch Reference** para selecionar o arquivo IFC do arquiteto.
3.  O modelo aparecerá como um link. Você pode usar as ferramentas de visibilidade para ocultar o que não for necessário.

### 2.2 Usando uma planta 2D (DXF/DWG)
1.  Vá em `Arquivo > Importar` e selecione seu DXF.
2.  Use a bancada **Draft** para mover o desenho para o marco zero (0,0,0) e ajustar a escala (comando `Scale`).
3.  **Dica**: Coloque o DXF em um "Draft Layer" e mude a cor para cinza para facilitar a visualização dos seus componentes elétricos.

---

## 3. Lançamento de Componentes (Modelagem)
Agora vamos "rechear" o projeto com inteligência.

1.  **Inserir Pontos**: Use a ferramenta **Biblioteca de Componentes**.
2.  Selecione o item (ex: Tomada 2P+T, Luminária LED, Interruptor).
3.  Clique no local da planta para inserir.
4.  **Definir Propriedades BIM**: Com o objeto selecionado, vá na aba "Dados" (Propriedades):
    *   **Potencia**: Insira a carga em VA.
    *   **Circuito**: Digite o nome do circuito (ex: C1).
    *   **QuadroVinculado**: Selecione a qual quadro esse ponto pertence.

---

## 4. Infraestrutura (Eletrodutos e Eletrocalhas)
1.  Selecione os pontos que deseja interligar.
2.  Use a ferramenta **Conduíte/Eletroduto**.
3.  O sistema criará o caminho 3D. Nas propriedades do eletroduto, você pode ver a **Taxa de Ocupação**. Se passar de 40%, o sistema avisará na auditoria.

---

## 5. Quadros de Distribuição (QDC/CCM)
1.  Clique em **Criar Quadro de Distribuição**.
2.  Posicione-o na parede.
3.  No painel de propriedades, defina se ele é um QDC (Residencial) ou CCM (Motores).
4.  Se for um sub-quadro, use a propriedade **AlimentadoPor** para vinculá-lo ao quadro principal.

---

## 6. Cálculos e Dimensionamento (Inteligência NBR 5410)
Com os pontos lançados e circuitos nomeados:

1.  **Quadro de Cargas**: Clique em **Gerar Quadro de Cargas**.
    *   O FreeCAD criará uma planilha (Spreadsheet) automática.
    *   O sistema calculará: Corrente nominal, Seção do cabo, Disjuntor sugerido e Queda de Tensão real baseada no comprimento 3D.
2.  **Balanceamento de Fases**: Clique em **Otimizar Fases**. O algoritmo irá redistribuir os circuitos entre R, S e T para minimizar o desequilíbrio.

---

## 7. Auditoria Técnica e Visualização (Heatmaps)
1.  **Auditor de Projeto**: Realiza Clash Detection preciso e verificação Ib <= In.
2.  **Heatmap de Queda de Tensão**: Clique em **Ativar Heatmap (V%)**. Os objetos ficarão coloridos (Verde/Amarelo/Vermelho) facilitando a detecção visual de subdimensionamento.
3.  **Heatmap de Ocupação**: Visualize quais eletrodutos estão próximos do limite de 40% de ocupação.

1.  **Sugestão de DR/DPS**: O sistema analisa áreas molhadas e a categoria da obra para sugerir o uso de Dispositivos Residuais e Protetores de Surto nos quadros.
2.  **Aplicação Automática**: Clique em **Aplicar Proteções** para que o sistema configure as propriedades de segurança em todos os quadros do projeto.

## 9. Orçamentação Dinâmica (SINAPI)
1.  **Tabelas Externas**: O sistema agora busca preços em arquivos `precos.json` ou `precos_eletrica.csv` na pasta do seu projeto.
2.  **Personalização**: Você pode exportar a tabela padrão, ajustar os preços conforme seu fornecedor e o FreeCAD passará a usar esses valores no Dashboard em tempo real.

## 10. Automação de Pranchas (TechDraw)
1.  **Gerar Prancha**: Com um clique, o sistema cria uma folha técnica A3.
2.  **Preenchimento de Carimbo**: O nome do autor, obra e data são puxados automaticamente do `ProjectData`.
3.  **Vistas Automáticas**: O sistema gera a vista de planta baixa do modelo 3D diretamente na folha de desenho.

## 11. Roteamento Inteligente (Auto-Routing)
1.  **Interligação Automática**: Selecione dois componentes (ex: uma tomada e um quadro) e use o **Roteamento Ortogonal**.
2.  **Traçado**: O sistema calculará o caminho subindo pelo teto e descendo no destino, criando o eletroduto automaticamente.

## 12. Dimensionamento de Ambientes (NBR 5410)
1.  **Mínimo de Tomadas**: O Auditor agora avisa se um cômodo (Arch Space) tem menos tomadas que o exigido pelo seu perímetro.
2.  **Iluminação**: O sistema sugere a potência em VA e o número de luminárias LED necessárias para atingir o nível de iluminância (Lux) correto.

## 13. Diagrama Unifilar Gráfico
1.  **Gerar Diagrama**: Selecione um Quadro de Distribuição e clique em **Gerar Diagrama Unifilar**.
2.  **Saída TechDraw**: Um esquema elétrico profissional será desenhado automaticamente na folha de desenho, contendo disjuntores, bitolas e potências de cada circuito.

## 14. Lista de Cabos (De-Para)
1.  **Relatório de Instalação**: Gere uma lista detalhada que informa a origem, destino, bitola e comprimento de cada trecho de cabo do projeto.
2.  **Exportação**: Disponível em CSV para uso direto na obra.

## 15. Estudo de Sombreamento Solar
1.  **Análise de Perdas**: O sistema detecta se outros prédios, árvores ou muros estão projetando sombras sobre seus painéis fotovoltaicos.
2.  **Fator de Eficiência**: O cálculo de geração anual será ajustado automaticamente considerando essas perdas reais do modelo 3D.

## 16. Documentação e Entrega
1.  **Lista de Materiais**: Clique em **Exportar BOM**. Isso gerará um arquivo CSV (Excel) com todos os cabos, eletrodutos e dispositivos.
2.  **Memorial Descritivo**: Clique em **Gerar Memorial**. Um arquivo Markdown (.md) será criado com toda a memória de cálculo do projeto.
3.  **Exportação IFC4**: Clique em **Exportar para IFC**. 
    *   O sistema irá "enriquecer" os objetos com Property Sets oficiais.
    *   O arquivo gerado poderá ser aberto em qualquer software BIM (Revit, Navisworks) com todas as informações elétricas preservadas.
3.  **Gestão de Ativos (BIM 7D)**: Clique em **Gerar QR Codes de Manutenção** para criar as fichas técnicas vinculadas aos equipamentos físicos.

---

## 18. Automação e Indústria 4.0
O workbench agora suporta o ciclo completo de automação:
1.  **Inserir CLP/IHM**: Adicione controladores e telas de operação com metadados de protocolo (MQTT, OPC UA, Profinet).
2.  **Redes Industriais**: Configure portas de E/S digitais/analógicas e protocolos de comunicação para interoperabilidade.

## 19. Aterramento Crítico (Subestações)
Baseado na **NBR 15751**:
1.  **Assistente de Malha**: Desenha o grid de cobre nu automaticamente.
2.  **Cálculo de Segurança**: Valida as tensões de toque e passo para proteção da vida humana em faltas de alta intensidade.

---

---

## 17. Resolução de Problemas (Troubleshooting)
| Problema | Causa Provável | Solução |
|----------|---------------|---------|
| Erro `name 'tr' is not defined` | Falha na inicialização do sistema de tradução | Atualize para a versão 3.1 (ou aplique o patch no `InitGui.py`). |
| Erro `name '__file__' is not defined` | Limitação do `exec()` no FreeCAD 1.1 | Versão 3.2.1 utiliza `globals()` e fallbacks de diretório do sistema. |
| Quadro de Cargas vazio | Objetos sem o campo `QuadroVinculado` preenchido | Use o **Auditor de Projeto** para encontrar objetos órfãos. |
| Dashboard não atualiza | O FreeCAD não disparou o evento de recomputação | Clique no botão **Atualizar** no painel lateral. |
| Ícones sumiram | Caminho da pasta `Mod/Eletrica` alterado | Reinstale a bancada na pasta padrão do usuário. |

---

### Atalhos Úteis no Dashboard (Painel Lateral)
*   **KPI Potência**: Clique para selecionar todos os objetos com carga no projeto.
*   **KPI Orçamento**: Clique para ver quanto custará o projeto em tempo real.
*   **Botão Atualizar**: Sempre clique aqui após mover objetos para atualizar as métricas.
