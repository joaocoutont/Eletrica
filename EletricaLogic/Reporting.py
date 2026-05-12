# Gerador de Relatorios Tecnicos e Memoria de Calculo
import FreeCAD
from EletricaLogic.Settings import ProjectSettings

class ReportManager:
    @staticmethod
    def generate_technical_memory():
        """Gera uma memoria de calculo resumida em uma nova aba do FreeCAD (ou log)"""
        doc = FreeCAD.ActiveDocument
        settings = ProjectSettings.get_settings_obj()
        
        # 1. Coleta de dados globais
        total_va = 0.0
        circuits_count = 0
        for obj in doc.Objects:
            if hasattr(obj, "Potencia"):
                total_va += float(obj.Potencia)
            if hasattr(obj, "Circuito"):
                circuits_count += 1
                
        report = []
        report.append("====================================================")
        report.append(f"MEMÓRIA DE CÁLCULO - {settings.NomeProjeto}")
        report.append(f"Autor: {settings.Autor}")
        report.append("====================================================")
        report.append(f"Sistema de Fornecimento: {settings.Sistema}")
        report.append(f"Tensão Nominal: {settings.Tensao}")
        report.append(f"Tipo de Edificação: {settings.TipoEdificacao}")
        report.append("----------------------------------------------------")
        report.append(f"Carga Total Instalada: {round(total_va, 2)} VA")
        report.append(f"Quantidade de Circuitos: {circuits_count}")
        report.append("----------------------------------------------------")
        
        # Detalhes de Aterramento (se calculado)
        if hasattr(settings, "QtdCaixas4x2"):
            report.append("Resumo de Materiais:")
            report.append(f"- Caixas 4x2: {settings.QtdCaixas4x2}")
            report.append(f"- Caixas Octogonais: {settings.QtdCaixasOcto}")
            
        report.append("====================================================")
        report.append("Relatório gerado automaticamente pela Bancada Eletrica BIM.")
        
        full_text = "\n".join(report)
        FreeCAD.Console.PrintMessage(full_text + "\n")
        
        # Salvar em um arquivo de texto no workspace do usuario
        import os
        file_path = os.path.join(os.path.expanduser("~"), f"Memoria_Calculo_{settings.NomeProjeto}.txt")
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(full_text)
            return file_path
        except:
            return None
