# Exportador Seletivo por Disciplina (BIM Multi-Export)
import FreeCAD
import ImportGui
import csv
import os

class DisciplineExporter:
    @staticmethod
    def export_by_discipline(discipline, file_path):
        """
        Exporta apenas os objetos pertencentes a uma disciplina especifica.
        """
        doc = FreeCAD.ActiveDocument
        export_list = []
        
        # Filtros baseados nas propriedades dos objetos
        for obj in doc.Objects:
            is_match = False
            
            if discipline == "Elétrica":
                valid_types = ["QDC", "CCM", "CCA", "Tomada", "Luminaria", "Eletroduto", "Motobomba", "ArCondicionado", "Telecom", "Rack", "TUE"]
                if hasattr(obj, "TipoBIM") and obj.TipoBIM in valid_types:
                    is_match = True
            elif discipline == "SPDA":
                if "SPDA" in obj.Label or (hasattr(obj, "TipoBIM") and "SPDA" in str(obj.TipoBIM)):
                    is_match = True
            elif discipline == "Fotovoltaico":
                if "Solar" in obj.Label or "Painel" in obj.Label or "Inversor" in obj.Label:
                    is_match = True
            
            if is_match:
                export_list.append(obj)
        
        if export_list:
            # Exportar para IFC ou STEP conforme extensao
            if file_path.lower().endswith(".ifc"):
                from EletricaLogic.IFC import IFCExportManager
                IFCExportManager.prepare_for_ifc() # Enriquecer com Psets antes de exportar
                import importIFC
                importIFC.export(export_list, file_path)
            else:
                ImportGui.export(export_list, file_path)
            return len(export_list)
        return 0

    @staticmethod
    def run_multi_export(base_path):
        """Executa a exportacao de todas as disciplinas em arquivos separados"""
        results = {}
        for disc in ["Elétrica", "SPDA", "Fotovoltaico"]:
            path = f"{base_path}_{disc}.ifc"
            count = DisciplineExporter.export_by_discipline(disc, path)
            results[disc] = count
        return results

    @staticmethod
    def export_bom_to_csv(bom_data, budget_report=None):
        """
        Exporta a Lista de Materiais e o Orçamento para um arquivo CSV formatado para Excel.
        Usa ponto-e-vírgula como separador para compatibilidade com Excel em Português.
        """
        doc = FreeCAD.ActiveDocument
        if not doc: return None
        
        filename = f"Quantitativo_{doc.Name}.csv"
        if doc.FileName:
            file_path = os.path.join(os.path.dirname(doc.FileName), filename)
        else:
            file_path = os.path.join(os.path.expanduser("~"), filename)
            
        try:
            with open(file_path, mode='w', encoding='utf-8-sig', newline='') as f:
                writer = csv.writer(f, delimiter=';')
                
                # Cabeçalho da Lista de Materiais
                writer.writerow(["LISTA DE MATERIAIS - PROJETO ELÉTRICO"])
                writer.writerow(["Gerado por:", "Suite Elite BIM (FreeCAD)"])
                writer.writerow([])
                writer.writerow(["Item", "Quantidade", "Unidade"])
                
                for item, qty in bom_data.items():
                    unit = "m" if "Cabo" in item or "Eletroduto" in item or "Eletrocalha" in item else "pç"
                    # Formata número com vírgula para Excel PT-BR
                    qty_str = f"{qty:.2f}".replace('.', ',')
                    writer.writerow([item, qty_str, unit])
                
                # Se houver dados de orçamento, adiciona uma seção extra
                if budget_report:
                    writer.writerow([])
                    writer.writerow(["ORÇAMENTO ESTIMADO"])
                    writer.writerow(["(Preços baseados em precos_eletrica.csv ou padrões)"])
                    writer.writerow([])
                    writer.writerow(["Descrição", "Preço Unit.", "Subtotal"])
                    
                    # Extrair linhas do relatório de orçamento para o CSV
                    # (Assume-se que budget_report é o texto gerado pelo BudgetManager)
                    total = 0.0
                    for line in budget_report.split('\n'):
                        if ':' in line and '=' in line and 'R$' in line:
                            # Ex: "Tomada: 10.00 x R$ 15.00 = R$ 150.00"
                            parts = line.split(':')
                            desc = parts[0].strip()
                            prices = parts[1].split('=')
                            subtotal_str = prices[1].replace('R$', '').strip().replace('.', ',')
                            # Preço unitário aproximado do texto
                            unit_price = prices[0].split('x')[-1].replace('R$', '').strip().replace('.', ',')
                            writer.writerow([desc, unit_price, subtotal_str])
                        if 'TOTAL ESTIMADO' in line:
                            total = line.split('R$')[-1].strip().replace('.', ',')
                    
                    writer.writerow([])
                    writer.writerow(["TOTAL GERAL", "", f"R$ {total}"])
            
            FreeCAD.Console.PrintMessage(f"Excel (CSV) exportado com sucesso: {file_path}\n")
            return file_path
        except Exception as e:
            FreeCAD.Console.PrintWarning(f"Erro ao exportar CSV: {e}\n")
            return None
