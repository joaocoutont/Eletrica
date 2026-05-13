# Gerador de Relatorios Tecnicos e Memoria de Calculo
import FreeCAD
import os
from EletricaLogic.Settings import ProjectSettings
from EletricaLogic.Calculator import ElectricalCalculator

class ReportManager:
    @staticmethod
    def generate_markdown_memorial():
        """
        Gera um Memorial Descritivo completo em formato Markdown (.md).
        Inclui dados do projeto, análise de carga, demanda e estimativa de consumo.
        """
        doc = FreeCAD.ActiveDocument
        if not doc: return None
        
        meta = doc.getObject("Eletrica_ProjectData")
        settings = ProjectSettings.get_settings_obj()
        
        # Coleta de dados
        total_va = 0.0
        cargas = {} # {Tipo: PotenciaVA}
        
        for obj in doc.Objects:
            if hasattr(obj, "Potencia"):
                p = float(obj.Potencia)
                total_va += p
                tipo = getattr(obj, "TipoBIM", "Outros")
                cargas[tipo] = cargas.get(tipo, 0.0) + p

        p_type = getattr(meta, "ProjectType", "Residencial") if meta else "Residencial"
        demand_kva = ElectricalCalculator.calculate_demand(total_va, project_type=p_type)
        
        # Montagem do Markdown
        md = []
        md.append(f"# MEMORIAL DESCRITIVO ELÉTRICO")
        md.append(f"**Projeto:** {getattr(meta, 'ProjectName', doc.Name)}")
        md.append(f"**Data:** 12/05/2026")
        md.append(f"**Responsável Técnico:** {getattr(meta, 'DesignerName', 'Não Informado')}")
        md.append(f"**Registro (CREA/ART):** {getattr(meta, 'CREA', '-')}")
        
        md.append("\n## 1. Informações Gerais")
        md.append(f"- **Concessionária:** {getattr(meta, 'Utility', 'Local')}")
        md.append(f"- **Tensão de Atendimento:** {getattr(meta, 'Voltage', '220V')}")
        md.append(f"- **Tipo de Instalação:** {getattr(meta, 'ProjectType', 'Residencial')}")
        
        md.append("\n## 2. Levantamento de Cargas")
        md.append("| Tipo de Carga | Potência Total (VA) |")
        md.append("| :--- | :--- |")
        for tipo, pot in cargas.items():
            md.append(f"| {tipo} | {pot:,.2f} |")
        md.append(f"| **TOTAL INSTALADO** | **{total_va:,.2f} VA** |")
        
        md.append("\n## 3. Cálculos de Demanda (NBR 5410)")
        md.append(f"A demanda calculada para o projeto, considerando o fator de demanda para o tipo '{getattr(meta, 'ProjectType', 'Residencial')}', é de:")
        md.append(f"\n> **Demanda Estimada: {demand_kva:.2f} kVA**")
        
        # --- NOVO: SEÇÃO SPDA ---
        if hasattr(meta, "SPDARisk"):
            md.append("\n## 4. Análise de Proteção contra Descargas Atmosféricas (SPDA)")
            md.append(f"Análise realizada conforme critérios da NBR 5419-2:")
            md.append(f"- **Status da Estrutura:** {getattr(meta, 'SPDAStatus', 'Não Analisado')}")
            md.append(f"- **Risco Calculado (R):** {getattr(meta, 'SPDARisk', '0')}")
            md.append(f"- **Nível de Proteção:** {getattr(meta, 'SPDALevel', '-')}")
            if getattr(meta, 'SPDARequired', False):
                md.append("\n### Requisitos Técnicos SPDA:")
                md.append(f"- **Malha:** {getattr(meta, 'SPDAMesh', '-')}")
                md.append(f"- **Descidas:** {getattr(meta, 'SPDADowns', '-')}")
                md.append(f"- **Esfera Rolante:** R={getattr(meta, 'SPDASphere', '0')}m")
        
        md.append("\n## 5. Eficiência e Consumo")
        kwh_month = (total_va * 24 * 30 * 0.15) / 1000.0 # 15% uso médio
        md.append(f"Estimativa de consumo mensal baseada em regime de uso de 15%:")
        md.append(f"- **Consumo Mensal:** {kwh_month:.2f} kWh/mês")
        md.append(f"- **Custo Estimado (R$ 0,95/kWh):** R$ {kwh_month*0.95:,.2f}")
        
        md.append("\n---")
        md.append("*Relatório gerado automaticamente pela Suite Elite BIM - Bancada Eletrica FreeCAD.*")
        
        full_text = "\n".join(md)
        
        # Salvar arquivo
        filename = f"Memorial_{doc.Name}.md"
        if doc.FileName:
            file_path = os.path.join(os.path.dirname(doc.FileName), filename)
        else:
            file_path = os.path.join(os.path.expanduser("~"), filename)
            
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(full_text)
            FreeCAD.Console.PrintMessage(f"Memorial Markdown gerado em: {file_path}\n")
            return file_path
        except Exception as e:
            FreeCAD.Console.PrintWarning(f"Erro ao salvar memorial: {e}\n")
            return None

    @staticmethod
    def generate_technical_memory():
        """Fallback para a versão simplificada no console"""
        return ReportManager.generate_markdown_memorial()
