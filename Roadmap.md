# Roadmap de Desenvolvimento - Bancada Eletrica
**Versão**: 3.0 | **Última Revisão**: 2026-05-12

---

## ✅ Fase 1: Fundação e Elétrica Predial (CONCLUÍDA)
- [x] Estrutura base da bancada (Ícones SVG, Menus, 8 Toolbars).
- [x] Sistema de Proxy de comandos para integração estável com BIM e Draft.
- [x] Ícone do Raio (`Raio.svg`) como identidade visual da bancada.
- [x] Metadados do projeto (Nome, Autor, Tipo, Concessionária, Tensão, Fase, CREA, ART).
- [x] Lógica de cálculo de corrente, seção, queda de tensão e disjuntor (NBR 5410).
- [x] Ferramenta de inserção de Tomadas (TUG/TUE com classificação NBR 5410).
- [x] Ferramenta de inserção de Iluminação e Interruptores (Simples, Paralelo, Sensor).
- [x] Mesclagem de interruptores em placa multi-tecla.
- [x] Quadros de Distribuição (QDC/CCM) com hierarquia multinível.
- [x] Geração de Quadro de Cargas com detecção automática de DR.
- [x] Balanceamento de fases R, S, T.
- [x] Assistente de Padrão de Entrada para 6 concessionárias (Cemig, Energisa, Enel, CPFL, Neoenergia, Copel).
- [x] Auditoria técnica com Clash Detection 3D e relatório visual Qt.
- [x] Fator de demanda dinâmico por tipo de instalação.
- [x] Integração com referências BIM (Arch_Reference) e IFC (BIM_IfcExplorer).

---


## Fase 2: Industrial & Segurança (CONCLUÍDA ✅)
- [x] Catálogo de Motores e Partidas (Padrão WEG).
- [x] Dimensionador de Barramentos com Peso de Materiais.
- [x] Análise de Arc Flash (IEEE 1584) e Etiquetas NR-10.
- [x] Automação e IIoT (CLP, IHM, MQTT).
- [x] Dimensionamento de Condutores de Motores Automático.
- [x] Gestão de Ativos BIM 7D (QR Codes de Manutenção).
- [x] Cálculo Luminotécnico Industrial (Método dos Lúmens).
- [x] Barra de ferramentas "Elite 9: Industrial" integrada à bancada.
- [x] Modelagem 3D de Eletrocalhas com propriedades BIM (Tipo, Material, Taxa de Ocupação, Capacidade kg/m).
- [x] Assistente de Eletrocalha: dimensionamento automático por lista de cabos com `CableTrayCalculator`.
- [x] Corrente de curto-circuito (Icc kA) integrada ao Quadro de Cargas — coluna J com status.

## Fase 3: Alta Tensão & Distribuição (INICIADA 🚀)
- [x] Assistente de Rede Aérea de Distribuição MT.
- [x] Análise de Risco SPDA Completa (NBR 5419:2015).
- [x] Dimensionamento de Transformadores de Corrente (TC) e Potencial (TP).
- [x] Diagramas Unifilares de MT Automáticos.
- [x] Cálculo de queda de tensão em linhas longas (MT) com limites ANEEL (7%).
- [x] Suporte a 4 tensões de distribuição: 13,8 kV / 23,1 kV / 34,5 kV / 69 kV.
- [x] Subestações Particulares (Poste Único → H → CSP Pré-Fabricada → Abrigada) + objeto BIM.
- [x] SPDA completo (NBR 5419): análise de risco, malha Faraday, esfera rolante, descidas, aterramento e DPS.
- [x] Barra "Elite 10: Distribuição MT" com 3 assistentes integrados.
- [x] Bug `Broadway` removido do `Substation.py`.

---

## ✅ Fase 4: Inteligência e Otimização (CONCLUÍDA)
- [x] Roteamento automático de eletrodutos por menor caminho (`Routing.py`).
- [x] Estimativa solar automatizada com dados de irradiação (`Solar.py`).
- [x] Integração total com IFC4 para exportação BIM completa (`IFC.py`).
- [x] Geração de QR Code AR para acesso a dados do painel in-loco (`AR.py`).
- [x] Otimização de balanceamento de fases via algoritmo de empacotamento.

---

## ✅ Fase 5: Gestão, Custos e Documentação Avançada (CONCLUÍDA)
- [x] Gerador de Orçamentos Dinâmico (`Budget.py`) com suporte a tabelas externas (CSV).
- [x] Exportação de BOM e Orçamento para Excel (CSV compatível).
- [x] Gerador de diagrama unifilar automático em TechDraw.
- [x] Dashboard de indicadores (KPIs) de consumo e custos no `EletricaPanel.py`.
- [x] Memorial Descritivo automático em Markdown (`Reporting.py`).

---

## ✅ Fase 6: Automação, Smart Home e IoT (CONCLUÍDA)
- [x] Biblioteca de componentes de automação (Zigbee, WiFi, KNX) no `SmartHome.py`.
- [x] Assistente de configuração de cenas e topologia de rede inteligente.
- [x] Integração com protocolos de comunicação para simulação de comandos.
- [x] Modelagem de sistemas de segurança (Câmeras, Sensores de Intrusão).

---

## ✅ Backlog Técnico (CONCLUÍDO)
- [x] Conectar `Voltage` e `Sistema` do `ProjectData` diretamente ao `calculate_current()`.
- [x] Tabela de métodos de instalação completa (A1 a F — NBR 5410).
- [x] Roteamento com desvio automático de obstáculos (Collision Avoidance) no `Routing.py`.
- [x] Análise de sombreamento 3D simplificada para sistemas fotovoltaicos.
- [x] Suporte a multi-documento (projetos com vários pavimentos em arquivos separados) via `ProjectManager.py`.
- [x] Compatibilidade total com FreeCAD 1.1 (Dark Mode e novos ícones SVG).

---

## ✅ Fase 7: Estabilização e Documentação Pro (CONCLUÍDA)
- [x] Correção de erros de inicialização (`NameError: tr`) no `InitGui.py`.
- [x] Otimização exclusiva para FreeCAD 1.1 (v3.2) — Remoção de fallbacks legados.
- [x] Padronização de imports `FreeCADGui.Workbench` para maior compatibilidade.
- [x] Guia de "Início Rápido" (Quick Start) adicionado ao manual.
- [x] Seção de "Troubleshooting" (Resolução de Problemas) integrada.
- [x] Diagramas de fluxo lógico (Mermaid) adicionados à Memória Técnica.

## 🚀 Próximos Passos (Futuro)
- [ ] Integração com Machine Learning para predição de rotas de cabos.
- [ ] Exportação direta para Revit (via plugin intermediário).
- [ ] Cálculo de harmônicos e compensação de reativos dinâmica.
