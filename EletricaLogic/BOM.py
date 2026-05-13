# Gerador de Lista de Materiais (BOM)
import FreeCAD
import Spreadsheet
from EletricaLogic.Wiring import WiringManager

class BOMManager:
    @staticmethod
    def get_raw_bom_data():
        """
        Central Data Engine: Varre o documento e retorna um dicionário consolidado.
        Retorna: { 'ItemName': quantidade_float }
        """
        import FreeCAD
        doc = FreeCAD.ActiveDocument
        if not doc: return {}
        
        data = {}
        for obj in doc.Objects:
            # 1. Componentes discretos (Tomadas, Luzes, Motores, etc.)
            if hasattr(obj, "Potencia") and not obj.Label.startswith("Simbolo_"):
                # Agrupa por prefixo (ex: Tomada_Cozinha -> Tomada)
                name = obj.Label.split('_')[0]
                data[name] = data.get(name, 0) + 1
            
            # 2. Infraestrutura Linear (Eletrodutos, Eletrocalhas)
            if hasattr(obj, "Diameter") and hasattr(obj, "Shape"):
                diam = f"Eletroduto {obj.Diameter}mm"
                length = obj.Shape.Length / 1000.0 # metros
                data[diam] = data.get(diam, 0.0) + length
                
            if hasattr(obj, "TrayWidth") and hasattr(obj, "Shape"):
                tray = f"Eletrocalha {obj.TrayWidth}x{obj.TrayHeight}mm"
                length = obj.Shape.Length / 1000.0
                data[tray] = data.get(tray, 0.0) + length

        return data

    @staticmethod
    def generate_global_bom():
        """
        Gera uma planilha consolidada com todos os materiais do projeto.
        """
        doc = FreeCAD.ActiveDocument
        if not doc: return
        
        materials = {} # {Nome: Quantidade/Comprimento}
        
        for obj in doc.Objects:
            # 1. Contagem de Componentes (Tomadas, Luzes, etc)
            if hasattr(obj, "Potencia") and not obj.Label.startswith("Simbolo_"):
                name = obj.Label.split('_')[0] # Pega o tipo base
                materials[name] = materials.get(name, 0) + 1
            
            # 2. Comprimento de Eletrodutos
            if hasattr(obj, "Diameter") and hasattr(obj, "Shape"):
                diam = f"Eletroduto PVC {obj.Diameter}mm"
                length = obj.Shape.Length / 1000.0 # metros
                materials[diam] = materials.get(diam, 0.0) + length
        
        # 3. Comprimento de Cabos (do WiringManager)
        lengths = WiringManager.calculate_circuit_lengths()
        for circuit, length in lengths.items():
            cable = f"Cabo Flexivel (Circuito {circuit})"
            materials[cable] = materials.get(cable, 0.0) + (length / 1000.0)
            
        # 4. Criar Planilha
        sheet_name = "Lista_de_Materiais"
        sheet = doc.getObject(sheet_name)
        if not sheet:
            sheet = doc.addObject("Spreadsheet::Sheet", sheet_name)
            
        sheet.set("A1", "Descricao do Material")
        sheet.set("B1", "Quantidade / Comprimento")
        sheet.set("C1", "Unidade")
        sheet.setStyle("A1:C1", "bold", "add")
        
        row = 2
        for mat, qty in materials.items():
            unit = "m" if "Cabo" in mat or "Eletroduto" in mat else "pç"
            sheet.set(f"A{row}", mat)
            sheet.set(f"B{row}", str(round(qty, 2)))
            sheet.set(f"C{row}", unit)
            row += 1
            
        doc.recompute()
        FreeCAD.Console.PrintMessage("Lista de Materiais gerada com sucesso!\n")
        return sheet

    @staticmethod
    def export_bom_to_csv():
        """Exporta o BOM para a pasta Downloads"""
        import os, csv
        doc = FreeCAD.ActiveDocument
        data = BOMManager.get_raw_bom_data()
        
        path = os.path.join(os.path.expanduser("~"), "Downloads", f"BOM_{doc.Label}.csv")
        with open(path, mode='w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f, delimiter=';')
            writer.writerow(['Material', 'Quantidade', 'Unidade'])
            for item, qty in data.items():
                unit = "m" if "Eletroduto" in item or "Cabo" in item else "pç"
                writer.writerow([item, f"{qty:.2f}", unit])
        
        from PySide import QtWidgets
        QtWidgets.QMessageBox.information(None, "BOM", f"Lista de Materiais exportada para:\n{path}")
        os.startfile(os.path.dirname(path))
