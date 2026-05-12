# Gerenciador de Lista de Cabos (Cable Schedule)
import FreeCAD

class CableScheduleManager:
    @staticmethod
    def generate_cable_schedule():
        """
        Gera uma lista de cabos baseada nas conexões De/Para do projeto.
        """
        doc = FreeCAD.ActiveDocument
        schedule = []
        
        # 1. Cabeçalho
        schedule.append(["TAG", "Origem (DE)", "Destino (PARA)", "Tipo/Bitola", "Distância (m)", "Função"])
        
        # 2. Varrer objetos que possuem conexões elétricas
        for obj in doc.Objects:
            # Caso 1: Motores/Equipamentos (BIMified)
            if hasattr(obj, "Circuito") and hasattr(obj, "Alimentacao") or hasattr(obj, "QuadroVinculado"):
                origin = ""
                if hasattr(obj, "QuadroVinculado") and obj.QuadroVinculado:
                    origin = obj.QuadroVinculado.Label
                elif hasattr(obj, "Alimentacao"):
                    origin = obj.Alimentacao
                
                if origin:
                    # Cálculo de distância (Distância Euclidiana simplificada ou via Trajeto se houver)
                    dist = 0.0
                    if hasattr(obj, "Placement"):
                        # Se houver um quadro vinculado, calcula distancia entre eles
                        q = doc.getObject(origin) if isinstance(origin, str) else origin
                        if q and hasattr(q, "Placement"):
                            dist = (obj.Placement.Base - q.Placement.Base).Length / 1000.0 * 1.2 # +20% sobra
                    
                    tag = f"CB-{obj.Label}"
                    bitola = "Ver Quadro de Cargas"
                    funcao = "Força" if "Motor" in obj.Label else "Comando/Geral"
                    
                    schedule.append([tag, origin, obj.Label, bitola, f"{dist:.2f}", funcao])
                    
        return schedule

    @staticmethod
    def export_to_spreadsheet():
        """Exporta a lista para uma planilha do FreeCAD"""
        import Spreadsheet
        doc = FreeCAD.ActiveDocument
        
        sheet = doc.getObject("Lista_de_Cabos") or doc.addObject("Spreadsheet::Sheet", "Lista_de_Cabos")
        data = CableScheduleManager.generate_cable_schedule()
        
        for row_idx, row_data in enumerate(data):
            for col_idx, value in enumerate(row_data):
                sheet.set(chr(65 + col_idx) + str(row_idx + 1), str(value))
        
        FreeCAD.ActiveDocument.recompute()
        return sheet.Name
