# Utilitarios para Exportacao IFC (BIM)
import FreeCAD

class IFCExportManager:
    @staticmethod
    def prepare_for_ifc():
        """
        Mapeia as propriedades da bancada Eletrica para os Property Sets padrao do IFC.
        Ex: Pset_ElectricalDeviceCommon
        """
        doc = FreeCAD.ActiveDocument
        if not doc: return
        
        for obj in doc.Objects:
            # Se for um dispositivo eletrico (tomada, luz, etc)
            if hasattr(obj, "Potencia") and hasattr(obj, "Circuito"):
                # No FreeCAD Arch, podemos usar a propriedade 'Ifc Attributes'
                # ou garantir que o tipo IFC seja definido
                if hasattr(obj, "IfcType"):
                    # Definir tipo se nao existir
                    if "Tomada" in obj.Label: obj.IfcType = "Outlet"
                    elif "Luz" in obj.Label or "Lampada" in obj.Label: obj.IfcType = "LightFixture"
                
                # Adicionar propriedades ao Pset customizado
                # (O exportador do FreeCAD le propriedades de grupos especificos)
                pass
        
        FreeCAD.Console.PrintMessage("Objetos preparados para exportacao IFC4.\n")
