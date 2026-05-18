# Gerenciador de Lista de Cabos (Cable Schedule) - De/Para
import FreeCAD
import csv
import os
from EletricaLogic.Calculator import ElectricalCalculator

class CableScheduleManager:
    """
    Gera a listagem detalhada de cabos (De/Para) com comprimentos reais.
    """

    @staticmethod
    def generate_cable_schedule():
        """
        Gera uma lista de cabos baseada nas conexões do projeto.
        """
        doc = FreeCAD.ActiveDocument
        if not doc: return []
        
        schedule = []
        # Cabeçalho
        schedule.append(["TAG", "DE (Origem)", "PARA (Destino)", "Circuito", "Seção (mm²)", "Comprimento (m)", "Status"])
        
        for obj in doc.Objects:
            if hasattr(obj, "Circuito") and hasattr(obj, "Potencia"):
                # Origem: Quadro Vinculado
                origin_obj = getattr(obj, "QuadroVinculado", None)
                origin = origin_obj.Label if origin_obj else "Desconhecido"
                
                # Comprimento: Tenta buscar do WiringManager ou cálculo direto
                # Para o MVP, vamos usar a distância 3D + fator de sobra
                dist = 0.0
                if origin_obj and hasattr(obj, "Placement") and hasattr(origin_obj, "Placement"):
                    # Comprimento Manhattan (ortogonal) é mais realista que euclidiano
                    p1 = obj.Placement.Base
                    p2 = origin_obj.Placement.Base
                    dist = (abs(p1.x - p2.x) + abs(p1.y - p2.y) + abs(p1.z - p2.z)) / 1000.0
                    dist *= 1.15 # 15% de sobra para curvas e pontas
                
                # Seção do Cabo: Lida do objeto ou recalculada
                section = getattr(obj, "SecaoCabo", 2.5)
                
                tag = f"W-{obj.Circuito}-{obj.Label}"
                schedule.append([tag, origin, obj.Label, obj.Circuito, f"{section} mm²", f"{dist:.2f}", "OK"])
                    
        return schedule

    @staticmethod
    def export_to_csv():
        """Exporta a lista de cabos para um arquivo CSV"""
        doc = FreeCAD.ActiveDocument
        if not doc: return None
        
        data = CableScheduleManager.generate_cable_schedule()
        filename = f"Lista_Cabos_{doc.Name}.csv"
        
        if doc.FileName:
            file_path = os.path.join(os.path.dirname(doc.FileName), filename)
        else:
            file_path = os.path.join(os.path.expanduser("~"), filename)
            
        try:
            with open(file_path, mode='w', encoding='utf-8-sig', newline='') as f:
                writer = csv.writer(f, delimiter=';')
                writer.writerows(data)
            FreeCAD.Console.PrintMessage(f"Lista de Cabos exportada: {file_path}\n")
            return file_path
        except Exception as e:
            FreeCAD.Console.PrintWarning(f"Erro ao exportar cabos: {e}\n")
            return None

    @staticmethod
    def export_to_spreadsheet():
        """Exporta a lista para uma planilha interna do FreeCAD"""
        import Spreadsheet
        doc = FreeCAD.ActiveDocument
        if not doc:
            return None
        
        sheet = doc.getObject("Lista_de_Cabos") or doc.addObject("Spreadsheet::Sheet", "Lista_de_Cabos")
        data = CableScheduleManager.generate_cable_schedule()
        
        for row_idx, row_data in enumerate(data):
            for col_idx, value in enumerate(row_data):
                sheet.set(chr(65 + col_idx) + str(row_idx + 1), str(value))
        
        doc.recompute()
        return sheet.Name
