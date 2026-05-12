# Automacao de Andares e Repeticao (Multi-Storey Automation)
import FreeCAD
import Draft

class MultiStoreyManager:
    @staticmethod
    def clone_electrical_to_floor(source_floor, target_floor):
        """
        Clona todos os objetos eletricos de um andar para o outro,
        ajustando a altura Z proporcionalmente.
        """
        doc = FreeCAD.ActiveDocument
        
        # 1. Delta de altura
        dz = target_floor.Placement.Base.z - source_floor.Placement.Base.z
        
        # 2. Identificar objetos eletricos dentro do andar origem
        cloned_count = 0
        for obj in source_floor.OutList:
            # Clona apenas objetos que nos interessam
            if hasattr(obj, "Potencia") or hasattr(obj, "CircuitosPassantes"):
                new_obj = doc.copyObject(obj)
                # Ajustar Posicao
                new_pos = obj.Placement.Base + FreeCAD.Vector(0, 0, dz)
                new_obj.Placement.Base = new_pos
                
                # Adicionar ao novo andar container
                target_floor.addObject(new_obj)
                cloned_count += 1
                
        doc.recompute()
        FreeCAD.Console.PrintMessage(f"Sucesso: {cloned_count} objetos replicados para o andar {target_floor.Label}.\n")
        return cloned_count
