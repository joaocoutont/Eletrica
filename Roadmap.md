# Roadmap - Elite Industrial Suite (Evolução do Projeto)

Este documento descreve os próximos passos e as metas de desenvolvimento para as versões futuras do Elite Industrial Suite.

## 🟢 Versão 1.1 (Smart Edition) - [CONCLUÍDA] ✅
- [x] **Busca de Irradiação via GPS**: Integração com banco de dados HSP nacional no módulo fotovoltaico.
- [x] **Biblioteca de Ícones Profissionais**: SVGs exclusivos para Solar, Incêndio e Subestação.
- [x] **Simulação de Fluxo de Carga**: Motor de cálculo para estabilidade de rede e saturação de trafo.

## 🟡 Versão 2.0 (Inteligência e Automação) - [PREVIEW DISPONÍVEL] 🚀
- [x] **Gerador de Diagramas Unifilares**: Automação esquemática via TechDraw.
- [x] **Análise Financeira (BI)**: Módulo de Payback, TIR e VPL.
- [x] **Automatização de Fiação (Auto-Wire)**: IA de roteamento generativo para otimização de cabos.

## 🔴 Versão 3.0 (Novas Tecnologias) - [INTEGRAÇÃO INICIADA] 🌐
- [x] **Realidade Virtual (VR/AR)**: Exportador de modelos imersivos glTF.
- [x] **BIM 9D (Comissionamento)**: Checklists automáticos de entrega técnica.
- [ ] **Digital Twin (Gêmeo Digital)**: Integração com sensores IoT (Próxima etapa).

---

### Metas de Compatibilidade
- [x] FreeCAD 1.1 (Stable)
- [x] Suporte nativo a Ondas de Choque (Análise de surto em SPDA avançado).
- [x] Exportação direta para formatos de manufatura de barramentos (CNC/Dobra).

---
## Versao 3.1 (Preparacao BIM Eletrica) - [IMPLEMENTADA]
- [x] Assistentes de preparacao por CAD, IFC e FreeCAD.
- [x] Perfis adaptativos: predial, industrial, saneamento, redes urbana/rural, subestacao/MT, automacao residencial e automacao industrial.
- [x] Templates editaveis em TOML em `Templates/ProjectProfiles`.
- [x] Criacao de Site, Edificacao, Niveis, Espacos, Zonas e Setores quando aplicavel.
- [x] Configuracao de ponto base, coordenadas compartilhadas, rotacao/norte e escala CAD.
- [x] Quadros e circuitos como objetos BIM com propriedades eletricas.
- [x] Vinculo de tomadas a quadro, circuito, nivel e ambiente/setor.
- [x] Recalculo preliminar de cargas por circuito.
- [x] Validacao BIM eletrica basica e validacao visual.
- [x] Exportacao de tabela de pontos CSV e relatorio HTML.
- [x] Legenda automatica e rotas preliminares por circuito.

## Proximas Melhorias Sugeridas
- [ ] Editor visual completo de quadros e circuitos com propriedades detalhadas.
- [ ] Regras normativas configuraveis por perfil TOML.
- [ ] Roteamento MEP avancado com caixas automaticas e conectores.
- [ ] Dimensionamento completo de queda de tensao por comprimento real.
- [ ] Integracao IFC aprimorada com Psets eletricos exportaveis.
- [ ] Biblioteca de simbolos 2D/3D por sistema.

---
*Elite Industrial Suite - Evoluindo a Engenharia Digital.*
