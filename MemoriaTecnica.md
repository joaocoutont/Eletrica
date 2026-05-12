# Memória Técnica - Bancada Eletrica (FreeCAD)

## 1. Visão Geral
A bancada **Eletrica** é uma extensão para o FreeCAD focada em projetos de engenharia elétrica baseados em BIM (Building Information Modeling). O objetivo é fornecer ferramentas para modelagem 3D, cálculos normatizados e geração de documentação técnica automática.

## 2. Escopo Técnico
- **Base Normativa**: Inicialmente focada na **NBR 5410** (Instalações elétricas de baixa tensão).
- **Abordagem BIM**: Cada componente (tomada, conduíte, quadro) possui metadados técnicos (potência, corrente, queda de tensão, material).
- **Integração**: Compatível com as ferramentas nativas de Arquitetura (Arch/BIM) do FreeCAD.

## 3. Arquitetura do Sistema
- **Linguagem**: Python 3 (API do FreeCAD).
- **Interface**: PySide (Qt) para diálogos e painéis.
- **Estrutura de Dados**: Utilização de Propriedades Customizadas (App::Property) para armazenar dados de engenharia nos objetos 3D.

## 4. Funcionalidades Principais (Lógica Predial)
- **Dimensionamento de Condutores**: Cálculo automático baseado na capacidade de condução de corrente e queda de tensão.
- **Gestão de Circuitos**: Agrupamento de cargas em circuitos e quadros de distribuição.
- **Posicionamento Inteligente**: Inserção de componentes com alinhamento automático a paredes e estruturas.
- **Lista de Materiais (BOM)**: Extração automática de quantitativos.

## 5. Considerações Futuras
- Integração com sistemas fotovoltaicos.
- Cálculos de curto-circuito e seletividade.
- Modelagem de sistemas industriais (leitos, eletrocalhas de grande porte).
