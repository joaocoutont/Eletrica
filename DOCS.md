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
*Documento atualizado em: Maio de 2026*
